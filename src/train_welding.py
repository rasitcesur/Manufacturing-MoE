"""Train RSW and TIG experts independently, starting from randomized weights.
Select checkpoint and post-model blending on validation ONLY.
"""
import argparse,copy,csv,json,random,time
from pathlib import Path
import numpy as np,torch
from torch.nn import functional as F
from welding_specialists import WeldingSet,WeldingMoE55,predict
ROOT=Path(__file__).resolve().parents[1]
COMP=['robot_joint_drives_Wh','robot_controller_Wh','process_power_source_Wh','process_actuator_Wh','cooling_Wh','fume_extraction_Wh','gas_valve_Wh','source_standby_Wh','external_axes_Wh']
Y=['time_s','energy_Wh','material_added_g','wire_consumed_g','gas_consumed_L','spot_count']

def metrics(y,p,zero_policy='ignore'):
 y=np.asarray(y,float);p=np.asarray(p,float);error=p-y
 nz=np.abs(y)>1e-9
 return {'count':int(len(y)),'MAPE_pct':(float(np.mean(np.abs(error[nz]/y[nz]))*100) if np.any(nz) else None),
 'MAPE_nonzero_n':int(nz.sum()),'WAPE_pct':(float(np.sum(abs(error))/np.sum(abs(y))*100) if abs(y).sum()>1e-9 else None),
 'MSE':float(np.mean(error**2)),'R2':(float(1-np.sum(error**2)/np.sum((y-y.mean())**2)) if np.sum((y-y.mean())**2)>1e-9 else None),
 'MAE':float(np.mean(abs(error)))}

def load(process,sp):
 with np.load(ROOT/'data'/('resistance_spot_welding' if process=='rsw' else 'tig_welding')/f'{sp}.npz') as f:return {k:f[k] for k in f.files}

def run(process='rsw',epochs=240,patience=50,seed=5551,batch=64,device='auto'):
 torch.set_num_threads(1);np.random.seed(seed);random.seed(seed);torch.manual_seed(seed)
 device=('cuda' if torch.cuda.is_available() else 'cpu') if device=='auto' else device
 if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA requested but unavailable')
 train=WeldingSet(load(process,'train'))
 sets={'train':train,**{sp:WeldingSet(load(process,sp),train.norm) for sp in ('val','test','ood')}}
 model=WeldingMoE55(train.global_x.shape[1],train.history.shape[1],process).to(device)
 opt=torch.optim.AdamW(model.parameters(),lr=.0011,weight_decay=.0001)
 J,M,G,H=[t.to(device) for t in train.tensors()];targ=torch.from_numpy(train.y_logratio).to(device);p=torch.from_numpy(train.comp_prior).to(device);yt=torch.from_numpy(train.y[:,1]).to(device);
 fill=torch.from_numpy(train.material_ratio).to(device)
 best=float('inf');best_state=None;best_ep=0;pat=0;hist=[];start=time.time()
 for ep in range(1,epochs+1):
  model.train();losses=[]
  for batchidx in torch.randperm(len(J)).split(batch):
   opt.zero_grad();z,dep=model(J[batchidx],M[batchidx],G[batchidx],H[batchidx]);z=z.clamp(-1,1)
   proposed=p[batchidx]*torch.exp(z)
   pred=proposed.sum(1)
   loge=torch.log(pred.clamp_min(1e-8)/yt[batchidx].clamp_min(1e-8))
   shares=(p[batchidx]/p[batchidx].sum(1,keepdim=True).clamp_min(1e-8)).detach()
   component_loss=(F.smooth_l1_loss(z,targ[batchidx],beta=.06,reduction='none')*(.3+shares)).mean()
   total_loss=F.smooth_l1_loss(loge,torch.zeros_like(loge),beta=.035)
   if process=='tig':
    valid=(fill[batchidx]>.01)
    material_loss=F.smooth_l1_loss(dep[valid],fill[batchidx][valid],beta=.025) if valid.any() else 0.
   else:material_loss=0.
   loss=2*total_loss+.8*component_loss+.20*material_loss
   loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),3.);opt.step()
   losses.append(float(loss.detach()))
  pv,_=predict(model,sets['val']);en=metrics(sets['val'].y[:,1],pv[:,1]);
  material=metrics(sets['val'].y[:,2],pv[:,2]);criterion=en['MAPE_pct']+.20*en['WAPE_pct']+(.05*material['MAPE_pct'] if material['MAPE_pct'] is not None else 0)
  hist.append({'epoch':ep,'train_loss':np.mean(losses),'val_energy_MAPE_pct':en['MAPE_pct'],'val_WAPE_pct':en['WAPE_pct'],'val_added_MAPE_pct':material['MAPE_pct'],'criterion':criterion})
  if criterion<best-1e-5:best=criterion;best_state=copy.deepcopy(model.state_dict());best_ep=ep;pat=0
  else:pat+=1
  if ep==1 or ep%25==0: print(process,'epoch',ep,'val_M',round(en['MAPE_pct'],4),'val_W',round(en['WAPE_pct'],4),'best',best_ep,flush=True)
  if pat>=patience:break
 model.load_state_dict(best_state)
 # Blend choice also validation-only; fallback to physical prior when NN hurts.
 val=sets['val'];options=[]
 for blend in (0.,.25,.5,.75,1.):
  yp,_=predict(model,val,blend=blend);v=metrics(val.y[:,1],yp[:,1]);score=v['MAPE_pct']+.2*v['WAPE_pct'];options.append((score,blend))
 blend=min(options)[1]
 output=ROOT/'reports'/process
 output.mkdir(parents=True,exist_ok=True)
 results={};group=[];matched=[]
 for sp,d in sets.items():
  yp,c=predict(model,d,blend=blend)
  pure,_=predict(model,d,blend=0)
  cold,_=predict(model,d,no_history=True,blend=blend)
  m={nm:metrics(d.y[:,i],yp[:,i]) for i,nm in enumerate(Y)}
  m['physics_prior_energy']=metrics(d.y[:,1],pure[:,1]);m['history_zeroed_residual_energy']=metrics(d.y[:,1],cold[:,1]);
  m['components']={name:metrics(d.c[:,i],c[:,i]) for i,name in enumerate(COMP)}
  results[sp]=m
  for name in sorted(set(d.topology)):
   f=(d.topology==name)
   group.append({'split':sp,'topology':name,'programs':int(f.sum()),**metrics(d.y[f,1],yp[f,1])})
  if sp in ('test','ood'):
   for k in range(len(yp)):
    matched.append({'split':sp,'program_id':str(d.pids[k]),'robot_id':str(d.ids[k]),'topology':str(d.topology[k]),'n_axes':int(d.axes[k]),
                    'true_energy_Wh':float(d.y[k,1]),'prediction_energy_Wh':float(yp[k,1]),'physics_prior_Wh':float(d.prior[k,1]),
                    'true_added_g':float(d.y[k,2]),'prediction_added_g':float(yp[k,2])})
  print(process,sp,'energy MAPE',round(m['energy_Wh']['MAPE_pct'],5),'WAPE',round(m['energy_Wh']['WAPE_pct'],5),flush=True)
 with open(output/'group_metrics.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(group[0]));w.writeheader();w.writerows(group)
 with open(output/'matched_predictions.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(matched[0]));w.writeheader();w.writerows(matched)
 torch.save({'architecture':'WeldingMoE55','process':process,'model_state':model.state_dict(),
    'normalizer':train.norm,'global_dim':train.global_x.shape[1],'history_dim':train.history.shape[1],
    'blend':blend,'seed':seed,'best_epoch':best_ep,'from_scratch':True,'previous_weights_loaded':False},output/'model.pt')
 report={'process':process,'version':'normal','from_scratch':True,'weights_shared_with_mig_or_other_welding_models':False,
   'robot_kinematics_source':'nine welding-cell topologies','best_epoch':best_ep,'validation_blend':blend,
   'checkpoint_selection':'validation MAPE+0.2 WAPE + 0.05 material MAPE (TIG)',
   'num_parameters':sum(p.numel() for p in model.parameters()),'runtime_seconds':time.time()-start,
   'splits':results,'training_history':hist}
 (output/'metrics.json').write_text(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--process',choices=['rsw','tig'],required=True);p.add_argument('--epochs',type=int,default=240)
 p.add_argument('--patience',type=int,default=50);p.add_argument('--seed',type=int,default=5551);p.add_argument('--batch',type=int,default=64);p.add_argument('--device',choices=['auto','cpu','cuda'],default='auto')
 args=p.parse_args();run(**vars(args))
