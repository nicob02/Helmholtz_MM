import torch
from core.utils.tools import parse_config, modelTester, RemoveDir
from core.utils.tools import compute_steady_error, render_results
from core.models import msgPassing
from functions import ElectroThermalFunc as Func
import os
from functions import MagneticFunc as Func
import matplotlib.pyplot as plt

out_ndim = 1

dens=65
ckptpath = 'checkpoint/simulator_%s.pth' % Func.func_name    #FIGURE THIS OUT
device = torch.device(0)

func_main = Func(mu_in=3.0, mu_out=1.0,
                    center=(0.5,0.5), radius=0.2, steep=500.0)

mesh = ElectrodeMesh(ru=(1, 1), lb=(0, 0), density=65)
graph = mesh.getGraphData()
model = msgPassing(message_passing_num=3, node_input_size=out_ndim+2, 
                   edge_input_size=3, ndim=out_ndim, device=device, model_dir=ckptpath)
model.load_model(ckptpath)
model.to(device)
model.eval()
test_steps = 20

test_config = parse_config()

#model = kwargs['model'] # Extracts the model's dictioanry with the weights and biases values
setattr(test_config, 'device', device)   
setattr(test_config, 'model', model)
setattr(test_config, 'test_steps', test_steps)
setattr(test_config, 'NodeTypesRef', ElectrodeMesh.node_type_ref)
setattr(test_config, 'ndim', out_ndim)
setattr(test_config, 'graph_modify', func_main.graph_modify)
setattr(test_config, 'graph', graph)
setattr(test_config, 'density', dens)

      

#-----------------------------------------

print('************* model test starts! ***********************')
predicted_results = modelTester(test_config)

u_exact = func_main.exact_solution(graph)  
u_exact_np  = u_exact.detach().cpu().numpy()
# 2) Compute exact & error
rel_l2 = compute_steady_error(predicted_results, u_exact_np, test_config)
print(f"Relative L2 error: {rel_l2:.3e}")

# 3) Render the three‐panel result
render_results(predicted_results, u_exact_np, graph, filename="helmholtz_steady.png")

