"""From-scratch shared 1--15 DOF robot motion/energy MoE training and reporting."""
from __future__ import annotations
import argparse,json,csv,math,random,time,copy,sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
from robotics_calibrated import RoboticsMoECalibrated as RoboticsMoE,PreparedCalibrated as Prepared,prediction
ROOT=Path(__file__).resolve().parents[1]

def load(split):
    with np.load(ROOT/'data'/'robotics'/f'{split}.npz') as data:
        
        d={k:data[k] for k in data.files}
    with np.load(ROOT/'data'/'robotics'/f'{split}_gravity.npz') as extra:
        d.update({k:extra[k] for k in extra.files})
    with np.load(ROOT/'data'/'robotics'/f'{split}_past_calibration.npz') as past:
        d.update({k:past[k] for k in past.files})
    return d

def scores(true,pred):
    true=np.asarray(true,float);pred=np.asarray(pred,float)
    err=pred-true
    return dict(MAPE_pct=float(np.mean(abs(err)/np.maximum(abs(true),1e-8))*100),
        WAPE_pct=float(abs(err).sum()/max(abs(true).sum(),1e-8)*100),
        MSE=float(np.mean(err*err)),MAE=float(np.mean(abs(err))),
        R2=float(1-np.sum(err**2)/max(np.sum((true-true.mean())**2),1e-9)))

def grouped(y,p,axes,top,split):
    rows=[]
    for typ,labels in [('all',['all']),('axes',list(range(1,16))),('topology',sorted(set(top))),('axes_topology',[(n,t) for n in range(1,16) for t in sorted(set(top)) if np.any((axes==n)&(top==t))])]:
        for lab in labels:
            sel=np.ones(len(axes),bool) if typ=='all' else (axes==lab if typ=='axes' else ((axes==lab[0])&(top==lab[1]) if typ=='axes_topology' else top==lab))
            for k,name,unit in ((0,'time_s','s'),(1,'energy_Wh','Wh')):
                rows.append({'split':split,'group_type':typ,'group':f'{lab[0]:02d}_{lab[1]}' if typ=='axes_topology' else lab,'metric_target':name,'unit':unit,
                             'n_programs':int(sel.sum()),**scores(y[sel,k],p[sel,k])})
    return rows

def run(args):
    t0=time.time();random.seed(args.seed);np.random.seed(args.seed);torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    device=('cuda' if torch.cuda.is_available() else 'cpu') if args.device=='auto' else args.device
    if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
    train=Prepared(load('train'))
    sets={'train':train}
    for split in ('val','test','ood'):
        sets[split]=Prepared(load(split),train.mean,train.std)
    m=RoboticsMoE().to(device);optim=torch.optim.AdamW(m.parameters(),lr=args.lr,weight_decay=.00008)
    step=0;best=float('inf');best_state=None;best_ep=0;history=[];wait=0
    J,G,H,M=train.tensors(device)
    Y=torch.from_numpy(train.target).to(device)
    for ep in range(1,args.epochs+1):
        m.train();perm=torch.randperm(len(Y));losses=[]
        for ix in perm.split(args.batch):
            optim.zero_grad()
            o=m(J[ix],M[ix],G[ix],H[ix]);loss=torch.nn.functional.smooth_l1_loss(o,Y[ix],beta=.025)
            loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),3)
            optim.step();losses.append(float(loss.detach()))
        v=sets['val'];yp=prediction(m,v)
        valerr=np.abs(yp[:,1]-v.y[:,1])/np.maximum(v.y[:,1],1e-8)*100
        val_time=np.abs(yp[:,0]-v.y[:,0])/np.maximum(v.y[:,0],1e-8)*100
        by_axes=[float(np.mean(valerr[v.axes==n])) for n in range(1,16)]
        by_configuration=[float(np.mean(valerr[(v.axes==n)&(v.topology==t)])) for n in range(1,16) for t in set(v.topology) if np.any((v.axes==n)&(v.topology==t))]
        criterion=float(np.mean(by_configuration)+.25*np.mean(val_time))
        history.append({'epoch':ep,'train_loss':float(np.mean(losses)),'val_mean_axis_energy_MAPE':np.mean(by_axes),'val_mean_configuration_energy_MAPE':np.mean(by_configuration),'val_time_MAPE':np.mean(val_time),'val_criterion':criterion})
        if criterion<best-1e-6:
            best=criterion;best_state=copy.deepcopy(m.state_dict());best_ep=ep;wait=0
        else:wait+=1
        if ep==1 or ep%10==0:
            print(f'ROBOT EPOCH {ep} train={np.mean(losses):.5f} val_energy={np.mean(by_configuration):.3f}% val_time={np.mean(val_time):.3f}% best_ep={best_ep}',flush=True)
        if wait>=args.patience:break
    m.load_state_dict(best_state)
    out=ROOT/'reports'/'robotics';out.mkdir(parents=True,exist_ok=True)
    results={};allrows=[]
    for split,d in sets.items():
        p=prediction(m,d);cold=prediction(m,d,use_history=False)
        rr=grouped(d.y,p,d.axes,d.topology,split)
        allrows+=rr
        results[split]={'duration_s':scores(d.y[:,0],p[:,0]),'energy_Wh':scores(d.y[:,1],p[:,1]),
               'cold_energy_Wh':scores(d.y[:,1],cold[:,1]),
               'energy_by_axis_MAPE_pct':{str(n):scores(d.y[d.axes==n,1],p[d.axes==n,1])['MAPE_pct'] for n in range(1,16)}}
        if split in ('val','test','ood'):
            with (out/f'{split}_predictions.csv').open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['robot_id','n_axes','topology','actual_time_s','predicted_time_s','actual_energy_Wh','predicted_energy_Wh','nominal_energy_Wh','cold_energy_Wh'])
                for j in range(len(p)):
                    w.writerow([d.ids[j],int(d.axes[j]),d.topology[j],float(d.y[j,0]),float(p[j,0]),float(d.y[j,1]),float(p[j,1]),float(d.prior[j,1]),float(cold[j,1])])
    with (out/'all_metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
    report={'checkpoint_selection':'minimum validation mean-per-axis-topology energy MAPE + 0.25 time MAPE; test and OOD never used for selection',
       'architecture':'signed gravity+subtree context; MCE latent from six independent past sensor trajectories; physically calibrated baseline with learnable residual',
       'initialized_from_scratch':True,'best_epoch':best_ep,'runtime_s':time.time()-t0,
       'trainable_parameters':sum(p.numel() for p in m.parameters()),'seed':args.seed,
       'results':results,'history':history,'notes':['No true machine efficiency coefficients in model inputs.','Each robot ID belongs to exactly one split.','OOD tests deliberately altered mass and link length distribution.','Synthetic Newton-Euler and electrical surrogate, not MuJoCo benchmark.']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x)))
    torch.save({'model_type':'RoboticsMoECalibrated','robotics':m.cpu().state_dict(),
       'train_normalizer':{'mean':train.mean,'std':train.std},'hyperparameters':vars(args),
       'best_epoch':best_ep,'data_manifest':json.loads((ROOT/'data/robotics/manifest.json').read_text())},out/'robotics_model.pt')
    print('FINISHED',json.dumps({'epochs':best_ep,'results':results,'time_s':round(time.time()-t0,1)},indent=2),flush=True)

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--epochs',type=int,default=55);pa.add_argument('--patience',type=int,default=16)
    pa.add_argument('--batch',type=int,default=168);pa.add_argument('--lr',type=float,default=.0017)
    pa.add_argument('--seed',type=int,default=20261018);pa.add_argument('--device',choices=['auto','cpu','cuda'],default='auto');run(pa.parse_args())
