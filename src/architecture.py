"""Instantiate architecture only (random weights); no checkpoint/data loading."""
from train import TimeMoE,EnergyMoE,MODES_COMPONENTS
from machine_characterization import MachineCharacterizationExpert
from robotics_moe import RoboticsMoE51
from arc_welding_moe import ArcWeldingMoE54
from welding_specialists import WeldingMoE55
from pathlib import Path
import numpy as np

def inputs_from_data(root):
 from arc_welding_moe import PreparedArc54
 from train_arc_welding import load
 with np.load(root/'data/gmaw/train_gravity.npz') as f:gravity={k:f[k] for k in f.files}
 with np.load(root/'data/gmaw/train_past_motion.npz') as f:past={k:f[k] for k in f.files}
 ar=PreparedArc54(*load('train'),gravity,past)
 ans={'gmaw':(ar.global_dim,ar.history_dim)}
 from welding_specialists import WeldingSet
 for pr,dr in [('rsw','resistance_spot_welding'),('tig','tig_welding')]:
  with np.load(root/'data'/dr/'train.npz') as f:tr={k:f[k] for k in f.files}
  ds=WeldingSet(tr)
  ans[pr]=(ds.global_x.shape[1],ds.history.shape[1])
 return ans

def count_all():
 root=Path(__file__).resolve().parents[1]
 components=[(m,n) for m,names in MODES_COMPONENTS.items() for n in names]
 dims=inputs_from_data(root)
 mods={'Time Transformer':TimeMoE(), 'Manufacturing Energy MoE':EnergyMoE(components),
  'Manufacturing MCE':MachineCharacterizationExpert(),
  'General Robotics':RoboticsMoE51(history_dim=36),
  'GMAW':ArcWeldingMoE54(*dims['gmaw']),
  'RSW':WeldingMoE55(*dims['rsw'],'rsw'),
  'TIG':WeldingMoE55(*dims['tig'],'tig')}
 parts={k:sum(p.numel() for p in v.parameters() if p.requires_grad) for k,v in mods.items()}
 return {'parts':parts,'total_parameters':sum(parts.values()),'num_families':15,
   'float32_weight_MiB':sum(parts.values())*4/(1024**2),
   'int8_raw_weight_MiB':sum(parts.values())/(1024**2)}
