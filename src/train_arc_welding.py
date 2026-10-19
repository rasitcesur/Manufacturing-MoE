"""current fresh robot-aware Arc Welding training. Validation only checkpoint selection."""
from __future__ import annotations
import argparse,csv,json,random,time,copy
from pathlib import Path
import numpy as np, torch
from torch.nn import functional as F
from arc_welding_moe import PreparedArc54,ArcWeldingMoE54,predict
from train_arc_welding_core import metrics,TARGETS
COMPONENTS=['robot_joint_drives_Wh','robot_controller_Wh','welding_source_Wh','wire_feeder_Wh','cooling_Wh','fume_extraction_Wh','gas_valve_Wh','source_standby_Wh','external_axes_Wh']
def load(s):
    p=ROOT/'data/gmaw'
    with np.load(p/f'{s}.npz') as a, np.load(p/f'{s}_input_priors.npz') as b:
        return ({k:a[k] for k in a.files},{k:b[k] for k in b.files})
ROOT=Path(__file__).resolve().parents[1]

def run(a):
    torch.set_num_threads(1);random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
    device=('cuda' if torch.cuda.is_available() else 'cpu') if a.device=='auto' else a.device
    if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
    datasets={s:load(s) for s in ('train','val','test','ood')}
    gravity={};past={}
    for split in datasets:
        with np.load(ROOT/f'data/gmaw/{split}_gravity.npz') as d:gravity[split]={k:d[k] for k in d.files}
        with np.load(ROOT/f'data/gmaw/{split}_past_motion.npz') as d:past[split]={k:d[k] for k in d.files}
    train=PreparedArc54(*datasets['train'],gravity['train'],past['train'])
    ds={'train':train}
    for sp in ('val','test','ood'):ds[sp]=PreparedArc54(*datasets[sp],gravity[sp],past[sp],center=train.norm_center,scale=train.norm_scale)
    model=ArcWeldingMoE54(train.global_dim,train.history_dim).to(device)
    opt=torch.optim.AdamW(model.parameters(),lr=a.lr,weight_decay=.00008)
    J,M,G,H=[t.to(device) for t in train.tensors()];true=torch.from_numpy(train.comp_target).to(device);p=torch.from_numpy(train.component_prior).to(device)
    y=torch.from_numpy(train.y[:,1]).to(device);target_deposit=torch.from_numpy(train.transfer_target).to(device)
    best=1e9;best_state=None;best_ep=None;pat=0;history=[];t0=time.time()
    for ep in range(1,a.epochs+1):
        model.train();indices=torch.randperm(len(y));losses=[]
        for ix in indices.split(a.batch):
            opt.zero_grad();z,d=model(J[ix],M[ix],G[ix],H[ix]);z=torch.clamp(z,-1,1)
            energy=(torch.exp(z)*p[ix]).sum(1)
            log_error=torch.log(energy.clamp_min(.0001)/y[ix])
            # Robot drive gets its OWN supervised component head with high emphasis;
            # process components are trained separately. Log loss discourages relative bias.
            robot_loss=F.smooth_l1_loss(z[:,0],true[ix,0],beta=.035)
            process_loss=F.smooth_l1_loss(z[:,2:],true[ix,2:],beta=.05)
            total_loss=F.smooth_l1_loss(log_error,torch.zeros_like(log_error),beta=.035)
            wire_loss=F.smooth_l1_loss(d,target_deposit[ix],beta=.03)
            loss=1.2*total_loss+.55*robot_loss+.10*process_loss+.16*wire_loss
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),3)
            opt.step();losses.append(float(loss.detach()))
        pp,_=predict(model,ds['val'])
        en=metrics(ds['val'].y[:,1],pp[:,1]);dep=metrics(ds['val'].y[:,3],pp[:,3])
        # Both MAPE and WAPE; high-energy cases cannot be neglected.
        crit=en['MAPE_pct']+.25*en['WAPE_pct']+.06*dep['MAPE_pct']
        history.append({'epoch':ep,'train_loss':float(np.mean(losses)),'val_energy_MAPE_pct':en['MAPE_pct'],'val_energy_WAPE_pct':en['WAPE_pct'],'val_deposit_MAPE_pct':dep['MAPE_pct'],'criterion':crit})
        if crit<best-1e-6: best=crit;best_ep=ep;best_state=copy.deepcopy(model.state_dict());pat=0
        else:pat+=1
        if ep==1 or ep%10==0:print('v54 epoch',ep,'valid',round(en['MAPE_pct'],3),'WAPE',round(en['WAPE_pct'],3),'best',best_ep,flush=True)
        if pat>=a.patience:break
    model.load_state_dict(best_state)
    output=ROOT/'reports/gmaw';output.mkdir(exist_ok=True,parents=True)
    results={};group_rows=[];comparisons=[]
    for sp,dd in ds.items():
        pp,comps=predict(model,dd);cold,_=predict(model,dd,zero_history=True)
        result={k:metrics(dd.y[:,i],pp[:,i]) for i,k in enumerate(TARGETS)}
        result['physics_prior']=metrics(dd.y[:,1],dd.prior[:,1]);result['no_history_energy']=metrics(dd.y[:,1],cold[:,1])
        result['components']={k:metrics(dd.c[:,i],comps[:,i]) for i,k in enumerate(COMPONENTS)}
        results[sp]=result
        for ty,keys in [('scope',['industrial_scope','stress_long_serial']),('axis',list(range(1,16))),('topology',list(set(dd.topology)))]:
            for key in keys:
                flag=(dd.industrial_scope if key=='industrial_scope' else ~dd.industrial_scope) if ty=='scope' else ((dd.axes==key) if ty=='axis' else (dd.topology==key))
                if not flag.any():continue
                group_rows.append({'split':sp,'group_type':ty,'group':key,'count':int(flag.sum()),**metrics(dd.y[flag,1],pp[flag,1])})
        if sp in ('test','ood'):
            for i in range(len(pp)):
                comparisons.append({'split':sp,'program_id':str(dd.pids[i]),'robot_id':str(dd.ids[i]),
                  'axes':int(dd.axes[i]),'topology':str(dd.topology[i]),
                  'real_energy_Wh':float(dd.y[i,1]),'v54_pred_Wh':float(pp[i,1]),
                  'robot_drive_pred_Wh':float(comps[i,0]),'robot_drive_true_Wh':float(dd.c[i,0]),
                  'external_axes_pred_Wh':float(comps[i,-1]),'external_axes_true_Wh':float(dd.c[i,-1])})
        print('RESULT',sp,'MAPE',result['electricity_Wh']['MAPE_pct'],'WAPE',result['electricity_Wh']['WAPE_pct'],flush=True)
    with (output/'groups.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=group_rows[0].keys());w.writeheader();w.writerows(group_rows)
    with (output/'matched_predictions.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=comparisons[0].keys());w.writeheader();w.writerows(comparisons)
    conf={'global_dim':train.global_dim,'history_dim':train.history_dim}
    torch.save({'model_type':'ArcWeldingMoE54','model':model.state_dict(),'model_config':conf,
        'normalizer':{'center':train.norm_center,'scale':train.norm_scale},'best_epoch':best_ep,
        'seed':a.seed,'from_scratch':True,'previous_weights_loaded':False,'version':'normal'},output/'arc_welding_model.pt')
    report={'method':'separate scratch-trained six/seven axis GMAW gravity-aware joint expert, external positioner/rail energy specialist, welding PSU & auxiliary experts',
        'data':'GMAW welding-cell-specific nine-stratum synthetic data; six/seven axis arms, external rail/positioner separate',
        'checkpoint_selection':'validation MAPE+0.25 WAPE+0.06 deposited MAPE','best_epoch':best_ep,
        'architecture_version':'normal','previous_weights_loaded':False,'n_parameters':sum(v.numel() for v in model.parameters()),
        'runtime_s':time.time()-t0,'splits':results,'history':history}
    (output/'metrics.json').write_text(json.dumps(report,indent=2))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--epochs',type=int,default=260);p.add_argument('--patience',type=int,default=55);
    p.add_argument('--batch',type=int,default=64);p.add_argument('--device',choices=['auto','cpu','cuda'],default='auto');p.add_argument('--lr',type=float,default=.0012);p.add_argument('--seed',type=int,default=53100)
    run(p.parse_args())
