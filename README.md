---
license: other
license_name: polyform-noncommercial-1.0.0
license_link: https://polyformproject.org/licenses/noncommercial/1.0.0
language:
- en
- tr
tags:
- manufacturing
- mixture-of-experts
- physics-informed-machine-learning
- robotics
- machining
- gcode
- welding
- energy-modeling
- processing-time-estimation
---

# Manufacturing-MoE

**Demo:** [Manufacturing-MoE-Demo](https://huggingface.co/spaces/rasitcesur/Manufacturing-MoE-Demo). The Space loads model checkpoints from this repository when they are available.

Manufacturing-MoE estimates manufacturing operation time, electricity use and material movement from process programs, machine descriptions and measurements collected before the target operation. It combines mechanical and electrical calculations with operation-specific neural experts. The normal configuration has **369,608 trainable parameters** across 15 operation families.

The repository contains the **model architecture, inference physics, synthetic training data and training code**. It does not contain pretrained model weights. Run the training pipeline to create the checkpoints and evaluation reports before using the demo for predictions.

## Operations

| Operation | What is modeled |
|---|---|
| FDM 3D printing | Print duration, printer electricity consumption and filament use from extrusion and movement commands. |
| CNC milling | Cutting and non-cutting motion, spindle and feed drives, machining time, energy and removed metal. |
| CNC turning | Turning passes, spindle demand, feed motion and removed material. |
| Drilling | Axial hole-making, thrust-related loads, machine components and cycle time. |
| Boring | Hole enlargement and finishing, with its own cutting conditions. |
| Reaming | Hole finishing under comparatively small stock removal. |
| Tapping | Thread cutting, synchronized spindle-feed motion and reversal. |
| Grinding | Surface grinding passes, wheel drive demand and machine auxiliary consumption. |
| Band sawing | Blade and feed motion, cutting time and material removed along the kerf. |
| Laser cutting | Beam on-time, travel, electrical power demand and kerf removal. |
| Plasma cutting | Torch motion, plasma power, auxiliary equipment and kerf removal. |
| General robotics | Motion time and joint-drive electricity for 1–15-axis configurations, including gravity and downstream loads. |
| MIG/MAG (GMAW) welding | Six- and seven-axis welding arms, rails and positioners, arc power, wire deposition, shielding gas and auxiliary energy. |
| Resistance spot welding | Electrode squeeze and hold, current pulses, electrical contact losses, robot motion and auxiliary energy. |
| TIG (GTAW) welding | Arc power, continuous torch motion, shielding gas, cooling and optional filler wire. |

The general robotics model and the three welding models have **independent learned weights**. They may use common rigid-body simulation code, but the welding models have their own machine characterization and process experts. An external rail or workpiece positioner is not treated as another joint in the welding arm.

## Training

Python 3.10–3.12 and PyTorch 2.x are recommended. Data is included in `training_data.zip` and extracted into `data/` with `prepare_data.py`; there is no checkpoint to download and no pretrained initialization.

```bash
python -m pip install -r requirements.txt
python prepare_data.py
python src/smoke.py
python train.py --device auto --batch 4
```

On a CUDA-capable GPU with a compatible PyTorch installation, `--device auto` uses CUDA. Otherwise it uses the CPU. The five training stages run sequentially to reduce peak memory consumption. Checkpoints created during training are written to `reports/`; they are not packaged in this source release.

To check that the training scripts start without committing to a complete run:

```bash
python train.py --quick --device cpu --batch 4
```

The quick run is a pipeline check, **not** a trained model release or a meaningful accuracy benchmark. After full training, `reports/training_report.md`, `reports/training_report.json` and `reports/metrics.csv` contain the available results. See [TRAINING.md](TRAINING.md) for checkpoint locations, uploading results and the Space connection.

## Evaluation and limits

Each operation is evaluated with MAPE, WAPE, MSE, R² and MAE, where applicable. The split structure distinguishes training, validation, test and out-of-distribution data. Checkpoint selection uses validation data; test and OOD measurements are held for reporting.

The supplied synthetic datasets were created with separate process simulators. Those dataset generators are not part of this repository; only the physics needed for inference is included. Numerical results from these datasets measure agreement with a synthetic model of the process, not independent accuracy on real CNC machines or welding cells. Machine calibration uses measurements taken before the operation to be predicted; hidden simulator coefficients are not supplied directly to the neural model. No tool-wear or weld-strength prediction is included in this release.

## Demo

[Manufacturing-MoE Demo](https://huggingface.co/spaces/rasitcesur/Manufacturing-MoE-Demo) reads the model checkpoints from this repository after training and publication. Until those files exist, the Space displays the process descriptions and the training status without generating predictions from random weights.

## License

**PolyForm Noncommercial License 1.0.0.** [Read the full license](https://polyformproject.org/licenses/noncommercial/1.0.0). Research and other permitted noncommercial activities are allowed under its terms. Commercial use requires separate permission from the rights holder. The license is also included as `LICENSE`.
