#!/usr/bin/env python3
"""Train ALL 15 operation families from independent random initialization.
No pretrained checkpoint is read. Validation controls early stopping and blending;
test/OOD metrics are written only after selection. The five training stages run sequentially to limit peak GPU memory use.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from config import VARIANT
from prepare_data import prepare

def main():
 prepare()
 p=argparse.ArgumentParser()
 p.add_argument('--device',choices=('auto','cpu','cuda'),default='auto')
 p.add_argument('--quick',action='store_true',help='Pipeline check ONLY: undertrained; NOT publishable metrics')
 p.add_argument('--stage',choices=('all','manufacturing','robotics','gmaw','rsw','tig','report'),default='all')
 p.add_argument('--seed',type=int,default=20261018)
 p.add_argument('--batch',type=int,default=8,help='manufacturing Time Transformer batch; start with 4 or 8 on limited GPU memory')
 args=p.parse_args()
 print('Manufacturing-MoE',VARIANT,'device',args.device,'quick',args.quick,flush=True)
 env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONUNBUFFERED='1')
 epoch=2 if args.quick else None
 cmds={
  'manufacturing':['src/train.py','--output',str(ROOT/'reports'/'trained'),'--device',args.device,'--seed',str(args.seed),'--batch',str(args.batch),
    '--epochs-time',str(epoch or 65),'--epochs-energy',str(epoch or 120),'--epochs-machine',str(epoch or 300),
    '--patience',str(2 if args.quick else 15),'--patience-energy',str(2 if args.quick else 25), '--smoke-max-per-group',str(8 if args.quick else 0)],
  'robotics':['src/train_robotics.py','--device',args.device,'--seed',str(args.seed+1),'--epochs',str(epoch or 45),'--patience',str(2 if args.quick else 12)],
  'gmaw':['src/train_arc_welding.py','--device',args.device,'--seed',str(args.seed+2),'--epochs',str(epoch or 260),'--patience',str(2 if args.quick else 55)],
  'rsw':['src/train_welding.py','--process','rsw','--device',args.device,'--seed',str(args.seed+3),'--epochs',str(epoch or 260),'--patience',str(2 if args.quick else 55)],
  'tig':['src/train_welding.py','--process','tig','--device',args.device,'--seed',str(args.seed+4),'--epochs',str(epoch or 260),'--patience',str(2 if args.quick else 55)],
 }
 chosen=list(cmds) if args.stage=='all' else ([args.stage] if args.stage!='report' else [])
 completed=[]
 for stage in chosen:
  start=time.time();print('START',stage,flush=True)
  subprocess.run([sys.executable,*cmds[stage]],cwd=ROOT,env=env,check=True)
  completed.append({'stage':stage,'elapsed_seconds':time.time()-start});print('DONE',stage,flush=True)
 if chosen:(ROOT/'reports').mkdir(exist_ok=True);(ROOT/'reports'/'stage_durations.json').write_text(json.dumps(completed,indent=2))
 if args.stage in ('all','report'):
  subprocess.run([sys.executable,'src/make_report.py',*(['--quick'] if args.quick else [])],cwd=ROOT,check=True)
 print('Training workflow ended. Reports: reports/training_report.md and reports/metrics.csv')
if __name__=='__main__':main()
