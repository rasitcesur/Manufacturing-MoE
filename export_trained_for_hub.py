"""Package weights produced by independent training stages for the Hub demo."""
from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parent
FILES={
 'manufacturing':('reports/trained/model.pt','checkpoints/manufacturing/model.pt'),
 'robotics':('reports/robotics/robotics_model.pt','checkpoints/robotics/robotics_model.pt'),
 'gmaw':('reports/gmaw/arc_welding_model.pt','checkpoints/gmaw/arc_welding_model.pt'),
 'rsw':('reports/rsw/model.pt','checkpoints/rsw/model.pt'),
 'tig':('reports/tig/model.pt','checkpoints/tig/model.pt'),
}
def main():
 missing=[src for src,_ in FILES.values() if not (ROOT/src).is_file()]
 required=['reports/metrics.csv','reports/training_report.md','reports/training_report.json']
 missing.extend(x for x in required if not (ROOT/x).is_file())
 if missing:raise SystemExit('Training output is incomplete: '+', '.join(missing))
 status=json.loads((ROOT/'reports/training_report.json').read_text())
 if status.get('quick_undertrained') or status.get('incomplete_stage_reports'):
  raise SystemExit('A complete full-training report is required before publishing checkpoints.')
 for src,dest in FILES.values():
  target=ROOT/dest;target.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(ROOT/src,target)
 target=ROOT/'training_results';target.mkdir(exist_ok=True)
 for src in required:shutil.copy2(ROOT/src,target/Path(src).name)
 (target/'manifest.json').write_text(json.dumps({'variant':'normal','checkpoint_files':[d for _,d in FILES.values()],
      'training_report':'training_results/training_report.json','synthetic_data_only':True},indent=2))
 print('Five checkpoints and evaluation reports prepared for publication.')
if __name__=='__main__':main()
