# Training and publishing the Normal model

Run these commands from the model repository root.

```bash
python -m pip install -r requirements.txt
python prepare_data.py
python src/smoke.py
python train.py --device auto --batch 4
```

Install a PyTorch build compatible with the available device. `--device auto` uses CUDA when available and otherwise falls back to CPU. The training workflow runs one branch at a time; its five parts are `manufacturing`, `robotics`, `gmaw`, `rsw` and `tig`.

```bash
python train.py --stage robotics --device auto
python train.py --stage report
```

Full training writes model weights and reports in `reports/`. Each branch initializes its neural networks with a new random seed; **existing model weights are never read as training initialization**. Validation data selects checkpoints. A training interruption may leave reports incomplete; the summary explicitly lists missing branches.

When all five stages have completed, stage files for the Space and Hub release:

```bash
python export_trained_for_hub.py
```

The command copies five checkpoint files into `checkpoints/`, and copies the final reports into `training_results/`. It will fail if a required checkpoint or report is missing.

Upload the new `checkpoints/` and `training_results/` folders to the model repository, or upload the entire repository after checking its contents. The Space automatically checks whether each model checkpoint is present. No token is stored in this repository.

### Checkpoint paths

- `checkpoints/manufacturing/model.pt`
- `checkpoints/robotics/robotics_model.pt`
- `checkpoints/gmaw/arc_welding_model.pt`
- `checkpoints/rsw/model.pt`
- `checkpoints/tig/model.pt`

### Measurements

The model reports predictions from synthetic physics-based data. Do not present the synthetic test error as a measured accuracy on industrial machines. Calibration data must precede the target operation; the target's energy or material labels are never legitimate inference inputs.
