# Echogram Semantic Segmentation

Semantic segmentation pipeline for underwater acoustic (echogram) data using PyTorch Lightning + segmentation-models-pytorch. The notebook `Train_Model.ipynb` covers:

1. Path setup & data directory structure
2. Mapping processed ZARR files to EVR region annotation files
3. Preprocessing & patch generation (multi-class + binary masks)
4. PyTorch dataset & augmentations
5. Train / validation / test split by day (to reduce leakage)
6. U-Net (ResNet encoder) training with Focal Loss + metrics
7. Threshold selection & prediction utilities

Original notebook was created by [@eovchinn](https://github.com/eovchinn) and is is located [here](https://github.com/OceanStreamIO/echosounder-segmentation/blob/main/Train_Demo.ipynb).

The code here is accompanying a blog article here: 

---
## 1. Environment Setup

It is recommended to use a Python virtual environment (>=3.9). Below are instructions for macOS / Linux (bash/zsh) and Windows (PowerShell).

### Create and activate virtual environment (venv)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

If you need a specific CUDA build of PyTorch, visit: https://pytorch.org/get-started/locally/ and install the wheel they recommend, then run the rest of the dependency install (you can omit `torch`/`torchvision` from `requirements.txt` by editing it first).

---
## 2. Launch Jupyter Lab

```bash
jupyter lab
```

Then open `Train_Model.ipynb`.

If you add the environment after Jupyter was installed globally, you may need to install an IPython kernel:

```bash
python -m ipykernel install --user --name echogram-seg --display-name "Echogram Seg (venv)"
```
Select that kernel inside Jupyter Lab.

---
## 3. Data Layout
Update the `DATA_BASE_DIR` variable near the top of the notebook. Expected structure (example):

```
DATA_BASE_DIR/
  EVR_region_files/            # .evr annotation files
  processed/                   # processed ZARR subdirectories
  ML_data/
    imgs/                      # generated .npy image patches
    masks/                     # generated multi-class masks
    binary_masks/              # generated binary masks
```

The preprocessing cells will populate `ML_data/*` after scanning ZARR + EVR pairs.

---
## 4. Generating Patches
Run cells in order until the preprocessing section. This will:
- Load & concatenate ZARR datasets for a date
- Align region annotations (EVR)
- Slice the echogram into width-constrained patches
- Normalize channels & write `.npy` arrays for images, masks, and binary masks

You can restrict processing to a single date by inserting a `break` or filtering the loop.

---
## 5. Training
Key parameters to tweak:
- `batch_size`
- `encoder` (e.g., `resnet18`, `resnet50`, `timm-efficientnet-b0`, etc.)
- Learning rate in the optimizer (`Adam` currently with `lr=5e-3`)
- `alpha` / `gamma` in `FocalLoss`
- Early stopping patience

Launch training by executing the trainer cell:

```python
trainer.fit(pl_model, train_loader, val_loader)
```

Check TensorBoard for progress:
```bash
tensorboard --logdir outputs/tb_logs
```

Visit http://localhost:6006.

---
## 6. Evaluation & Threshold Selection
After training you can:

```python
# Load best checkpoint if not already in memory
# pl_model = SegModel.load_from_checkpoint('path/to/checkpoints/best_model.ckpt', ...)

results_df = pl_model.select_threshold(val_loader, device=device)
results_df.sort_values('IoU', ascending=False).head()
```

Use the best threshold to set `pl_model.threshold` before running `trainer.test(...)` or custom prediction logic.

---
## 7. Making Predictions

```python
from torch.utils.data import DataLoader
pred_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
output_dir = 'outputs/preds'
os.makedirs(output_dir, exist_ok=True)
pl_model.predict(pred_loader, device=device, output_dir=output_dir, file_prefix='val')
```

Each batch’s raw logits will be saved as `.npy`. Post-process with `sigmoid > threshold` for binary masks.

---
## 8. Reproducibility Tips
- Set `random.seed`, `np.random.seed`, and `torch.manual_seed` at the start for deterministic splits.
- Pin library versions in `requirements.txt` if you move to production.
- Record the `run_name` (includes timestamp) to associate checkpoints and TensorBoard logs.

---
## 9. Troubleshooting
| Issue | Possible Cause | Fix |
|-------|----------------|-----|
| CUDA not detected | No NVIDIA GPU / driver | Use CPU or MPS; reinstall proper PyTorch wheel |
| OOM during training | Batch too large | Reduce `batch_size` or image size, enable gradient accumulation |
| Extremely slow patch prep | Large ZARR + single thread | Install `dask` w/ threading; ensure SSD storage |
| Blank masks | EVR mismatch or date exclusion | Inspect mapping dataframe; verify EVR filenames |
| NaNs in loss | Invalid normalization or division by zero | Check data range; add value clamps |

---
## 10. License
MIT
