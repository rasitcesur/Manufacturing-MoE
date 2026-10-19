"""CPU forward/backward check for ALL parametrized model architectures; no checkpoint."""
import sys,json
from pathlib import Path
import numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from config import VARIANT
from architecture import count_all,inputs_from_data
from train import TimeMoE,EnergyMoE,MODES_COMPONENTS
from machine_characterization import MachineCharacterizationExpert
from robotics_moe import RoboticsMoE51
from arc_welding_moe import ArcWeldingMoE54
from welding_specialists import WeldingMoE55

torch.set_num_threads(1)
B,T=2,7
m=TimeMoE();p,_=m(torch.ones(B,T,dtype=torch.long),torch.randn(B,T,42),torch.ones(B,T,1),torch.ones(B,T,dtype=torch.bool),torch.zeros(B,dtype=torch.long));p.sum().backward();assert torch.isfinite(p).all()
components=[(k,n) for k,v in MODES_COMPONENTS.items() for n in v]
m=EnergyMoE(components);p=m(torch.randn(B,15),torch.zeros(B,dtype=torch.long),torch.zeros(B,dtype=torch.long),torch.ones(B));p.sum().backward();assert torch.isfinite(p).all()
m=MachineCharacterizationExpert(components=len(components));assert sum(x.numel() for x in m.parameters())>0
m=RoboticsMoE51();j=torch.randn(B,15,23);mask=torch.ones(B,15);g=torch.randn(B,26);h=torch.randn(B,12);p=m(j,mask,g,h);p.sum().backward();assert p.shape==(B,2)
d=inputs_from_data(ROOT)
for typ in ('gmaw','rsw','tig'):
 m=ArcWeldingMoE54(*d['gmaw']) if typ=='gmaw' else WeldingMoE55(*d[typ],typ)
 if typ=='gmaw':p,_=m(torch.randn(B,15,25),mask,torch.randn(B,d[typ][0]),torch.randn(B,d[typ][1]))
 else:p,_=m(torch.randn(B,15,15),mask,torch.randn(B,d[typ][0]),torch.randn(B,d[typ][1]))
 p.sum().backward();assert p.shape[0]==B and torch.isfinite(p).all()
print(json.dumps({'variant':VARIANT,'smoke_pass':True,**count_all()},indent=2))
