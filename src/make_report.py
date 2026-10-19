"""Create plain Markdown, JSON and CSV per-operation evaluation after training.
Never fabricate metrics for missing stages. No checkpoint required to run this reporter.
"""
from pathlib import Path
import argparse,csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from config import VARIANT
from architecture import count_all

def main():
 p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');a=p.parse_args()
 out=ROOT/'reports';out.mkdir(exist_ok=True)
 counts=count_all()
 rows=[];missing=[]
 def add(family,split,target,m,source):
  if not isinstance(m,dict):return
  rows.append({'variant':VARIANT,'family':family,'split':split,'target':target,'count':m.get('count',m.get('n',m.get('program_count',''))),
    'MAPE_pct':m.get('MAPE_pct',''),'WAPE_pct':m.get('WAPE_pct',''),'MSE':m.get('MSE',''),
    'R2':m.get('R2',''),'MAE':m.get('MAE',''),'source':source})
 src=out/'trained'/'metrics.json'
 if src.exists():
  d=json.loads(src.read_text());sm={'fdm':'FDM','cnc_milling':'Milling','cnc_turning':'Turning','cnc_drilling':'Drilling/Boring/Reaming/Tapping',
    'cnc_grinding':'Grinding','cnc_sawing':'Sawing','cnc_laser':'Laser','cnc_plasma':'Plasma'}
  for sp,modes in d.get('scores',{}).items():
   for k,targets in modes.items():
    for target,mm in targets.items():
     if isinstance(mm,dict) and target in ('time_s','energy_Wh','material_g'):
      add(sm.get(k,k),sp,target,mm,'manufacturing')
  for sp,groups in d.get('grouped_scores',{}).items():
   for k,targets in groups.items():
    for target,mm in targets.items():
     if isinstance(mm,dict) and target in ('time_s','energy_Wh','material_g'):
      add(k,sp,target,mm,'manufacturing_group')
 else:missing.append(str(src.relative_to(ROOT)))
 src=out/'robotics'/'metrics.json'
 if src.exists():
  d=json.loads(src.read_text());
  for sp,targets in d.get('results',{}).items():
   for k in ('duration_s','energy_Wh','cold_energy_Wh'):
    if k in targets:add('General Robotics',sp,k,targets[k],'robotics')
 else:missing.append(str(src.relative_to(ROOT)))
 src=out/'gmaw'/'metrics.json'
 if src.exists():
  d=json.loads(src.read_text());
  for sp,targets in d.get('results',{}).items():
   for k,mm in targets.items():
    if isinstance(mm,dict) and 'MAPE_pct' in mm:add('GMAW',sp,k,mm,'gmaw')
 else:missing.append(str(src.relative_to(ROOT)))
 for family,sub in [('RSW','rsw'),('TIG','tig')]:
  src=out/sub/'metrics.json'
  if src.exists():
   d=json.loads(src.read_text())
   for sp,targets in d.get('splits',{}).items():
    for k,mm in targets.items():
     if isinstance(mm,dict) and 'MAPE_pct' in mm:add(family,sp,k,mm,family.lower())
  else:missing.append(str(src.relative_to(ROOT)))
 fields=['variant','family','split','target','count','MAPE_pct','WAPE_pct','MSE','R2','MAE','source']
 with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 report={'version':'1.0','variant':VARIANT,'synthetic_simulator_warning':True,'quick_undertrained':a.quick,
  'architecture_parameters':counts,'metrics_rows':len(rows),'incomplete_stage_reports':missing,
  'validation_model_selection':'train scripts use validation; test/OOD are audits only',
  'no_pretrained_checkpoint':'training initializes from random weights only',
  'weights_not_shared_between_general_robot_gmaw_rsw_tig':True}
 (out/'training_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 ls=[f'# Manufacturing-MoE Normal {VARIANT.upper()} — eğitim raporu', '',
     '**UYARI:** Sentetik fizik simülasyonu; gerçek makine doğruluğu değildir. '+('QUICK deneme sonuçları üretim metriği değildir.' if a.quick else ''),
     '',f"**Öğrenilebilir parametre:** {counts['total_parameters']:,}",
     f"**Model parametreleri:** {json.dumps(counts['parts'],ensure_ascii=False)}",'',
     'Kriterler: MAPE, WAPE, MSE, R², MAE. Eğitim raporu validation checkpoint seçimi sonrası üretilir.',
     'Ağırlık paylaşımı yok: genel robot, GMAW, RSW ve TIG ayrı ağlar.',
     'Eksik raporlar: '+(', '.join(missing) if missing else 'Yok'),'',
     '| Operasyon | Bölüm | Çıktı | MAPE (%) | WAPE (%) | MSE | R² | MAE |',
     '|---|---|---|---:|---:|---:|---:|---:|']
 for r in rows:
  if r['source']=='manufacturing_group' and r['target']!='energy_Wh':continue
  def fmt(v):return f'{v:.5g}' if isinstance(v,(int,float)) else ('—' if v is None or v=='' else str(v))
  ls.append('| '+' | '.join(fmt(r[k]) for k in ('family','split','target','MAPE_pct','WAPE_pct','MSE','R2','MAE'))+' |')
 (out/'training_report.md').write_text('\n'.join(ls)+'\n',encoding='utf-8')
 print('Created',out/'training_report.md','metrics rows',len(rows),'missing',missing)
if __name__=='__main__':main()
