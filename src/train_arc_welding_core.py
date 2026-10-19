"""Train Arc Welding MCE and process experts from scratch; validation-only selection."""
from __future__ import annotations
import argparse,random,copy,json,time,csv
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from arc_welding_core import PreparedArc,ArcWeldingMoE,predict
ROOT=Path(__file__).resolve().parents[1]
TARGETS=['time_s','electricity_Wh','wire_consumed_g','wire_deposited_g','shielding_gas_L']
COMPONENTS=['robot_joint_drives_Wh','robot_controller_Wh','welding_source_Wh','wire_feeder_Wh','cooling_Wh','fume_extraction_Wh','gas_valve_Wh','source_standby_Wh']

def metrics(y,p):
    err=np.asarray(p,float)-np.asarray(y,float)
    y=np.asarray(y,float)
    return dict(MAPE_pct=float(np.mean(abs(err)/np.maximum(abs(y),1.e-9))*100),WAPE_pct=float(np.sum(abs(err))/max(np.sum(abs(y)),1e-9)*100),MSE=float(np.mean(err**2)),R2=float(1-np.sum(err**2)/max(np.sum((y-y.mean())**2),1e-9)),MAE=float(np.mean(abs(err))))

def load(s):
    p=ROOT/'data/arc_welding'
    with np.load(p/f'{s}.npz') as a, np.load(p/f'{s}_input_priors.npz') as b:
        return ({k:a[k] for k in a.files},{k:b[k] for k in b.files})

def train(a):
    torch.set_num_threads(1);random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
    base=ROOT/'reports/arc_welding_v52';base.mkdir(exist_ok=True,parents=True)
    raw={s:load(s) for s in ('train','val','test','ood')}
    train=PreparedArc(*raw['train'])
    sets={'train':train}
    for s in ('val','test','ood'):sets[s]=PreparedArc(*raw[s],center=train.center,scale=train.scale)
    model=ArcWeldingMoE(train.global_dim,train.history_dim)
    optimizer=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=.00008)
    J,M,G,H=train.tensors();Y=torch.from_numpy(train.comp_target);Dep=torch.from_numpy(train.transfer_target)
    P=torch.from_numpy(train.component_prior);Ytotal=torch.from_numpy(train.y[:,1]);Wire=torch.from_numpy(train.y[:,2])
    best=1e10;best_ep=0;best_w=None;pat=0;hist=[];t0=time.time()
    for ep in range(1,a.epochs+1):
        model.train();ids=torch.randperm(len(Y));running=[]
        for ix in ids.split(a.batch):
            optimizer.zero_grad()
            z,transfer=model(J[ix],M[ix],G[ix],H[ix])
            true_log=Y[ix]
            # Components with tiny absolute energy have limited impact on total WAPE.
            comp_loss=F.smooth_l1_loss(z,true_log,beta=.055)
            pred_energy=(torch.exp(torch.clamp(z,-1,1))*P[ix]).sum(1)
            total_loss=F.smooth_l1_loss(torch.log(pred_energy.clamp_min(.00001)/Ytotal[ix]),torch.zeros_like(Ytotal[ix]),beta=.05)
            trans_loss=F.smooth_l1_loss(transfer,Dep[ix],beta=.03)
            loss=.32*comp_loss+1.3*total_loss+.32*trans_loss
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),3.)
            optimizer.step();running.append(float(loss.detach()))
        pv,_=predict(model,sets['val'])
        en=metrics(sets['val'].y[:,1],pv[:,1])['MAPE_pct']
        dep=metrics(sets['val'].y[:,3],pv[:,3])['MAPE_pct']
        criterion=en+.08*dep
        hist.append({'epoch':ep,'train_loss':float(np.mean(running)),'val_energy_MAPE_pct':en,'val_deposition_MAPE_pct':dep,'criterion':criterion})
        if criterion<best-1e-5:best=criterion;best_ep=ep;best_w=copy.deepcopy(model.state_dict());pat=0
        else:pat+=1
        if ep==1 or ep%10==0:print('ARC EPOCH',ep,'loss',round(np.mean(running),5),'validation energy%',round(en,4),'deposition%',round(dep,4),'best',best_ep,flush=True)
        if pat>=a.patience:break
    model.load_state_dict(best_w)
    results={};all_rows=[];comparisons=[]
    for split,ds in sets.items():
        pp,c=predict(model,ds)
        pb=ds.prior.copy()
        cold,_=predict(model,ds,zero_history=True)
        result={name:metrics(ds.y[:,i],pp[:,i]) for i,name in enumerate(TARGETS)}
        result['prior_energy_Wh']=metrics(ds.y[:,1],pb[:,1])
        result['without_machine_history_energy_Wh']=metrics(ds.y[:,1],cold[:,1])
        result['energy_component_metrics']={name:metrics(ds.c[:,i],c[:,i]) for i,name in enumerate(COMPONENTS)}
        for flag,label in ((np.ones(len(pp),bool),'all'),(ds.industrial_scope,'industrial_scope'),(~ds.industrial_scope,'stress_long_serial')):
            if not flag.any():continue
            for i,name in enumerate(TARGETS):
                all_rows.append({'split':split,'category':'scope','group':label,'output':name,'count':int(flag.sum()),**metrics(ds.y[flag,i],pp[flag,i])})
        for n in range(1,16):
            flag=ds.axes==n
            for i,name in enumerate(TARGETS):
                all_rows.append({'split':split,'category':'axis','group':n,'output':name,'count':int(flag.sum()),**metrics(ds.y[flag,i],pp[flag,i])})
        for name in sorted(set(ds.topology)):
            flag=ds.topology==name
            for i,out in enumerate(TARGETS):
                all_rows.append({'split':split,'category':'topology','group':name,'output':out,'count':int(flag.sum()),**metrics(ds.y[flag,i],pp[flag,i])})
        if split in ('test','ood'):
            with open(base/f'{split}_predictions.csv','w',newline='') as f:
                w=csv.writer(f);w.writerow(['program_id','robot_id','n_axes','topology','industrial_scope']+[z for k in TARGETS for z in ('true_'+k,'pred_'+k)])
                for k in range(len(pp)):
                    w.writerow([ds.pids[k],ds.ids[k],int(ds.axes[k]),ds.topology[k],bool(ds.industrial_scope[k])]+[x for i in range(5) for x in (float(ds.y[k,i]),float(pp[k,i]))])
        results[split]=result
        print('RESULT',split, 'energy%',result['electricity_Wh']['MAPE_pct'],'deposited%',result['wire_deposited_g']['MAPE_pct'],'no_history%',result['without_machine_history_energy_Wh']['MAPE_pct'],flush=True)
    with open(base/'group_metrics.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(all_rows[0].keys()));w.writeheader();w.writerows(all_rows)
    normalizer={'center':train.center,'scale':train.scale}
    torch.save({'model_type':'ArcWeldingMoE','model':model.state_dict(),'normalizer':normalizer,
         'model_config':{'global_dim':train.global_dim,'history_dim':train.history_dim},
         'trained_from_scratch':True,'best_epoch':best_ep,'seed':a.seed,'version':'normal'},base/'arc_welding_model.pt')
    report={'method':'component-energy physics priors + shared joint expert + arc power + auxiliaries + MCE + material-addition experts',
       'checkpoint_selection':'validation total energy MAPE plus 0.08 x validation deposited wire MAPE',
       'previous_weights_loaded':False,'hidden_machine_parameters_used_as_inputs':False,
       'physics_preserved_outputs':['time_s','wire_consumed_g','shielding_gas_L'],
       'n_parameters':sum(p.numel() for p in model.parameters()),'best_epoch':best_ep,'seed':a.seed,
       'runtime_s':time.time()-t0,'splits':results,'training_history':hist,
       'notes':['Synthetic labels have not been measured on real welding equipment.','Transfer efficiency is not an input and varies independently between programs; deposited wire uncertainty is irreducible without new observations.','Simulated physics exact time/wire/gas heads are deterministic; only electrical components and deposited wire correction are learned.','No pretrained robot model weights were loaded.']}
    (base/'metrics.json').write_text(json.dumps(report,indent=2))
    print('TRAIN COMPLETE',best_ep,flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--epochs',type=int,default=180);p.add_argument('--batch',type=int,default=64);p.add_argument('--patience',type=int,default=35)
    p.add_argument('--lr',type=float,default=.0015);p.add_argument('--seed',type=int,default=52110)
    train(p.parse_args())
