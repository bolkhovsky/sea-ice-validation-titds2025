# Spatial Error Decomposition for Neural Network Sea Ice Forecasts

Reproducible experiment for the paper:

> **Bolkhovskiy, I., Bidenko, S.** (2025). Implementation and Experimental Validation of a Spatial Error Decomposition Framework for Neural Network Sea Ice Forecasts Along the Northern Sea Route. *Proceedings of TITDS-XV-2025*, Springer LNCS.

## Key Finding

In **29.6%** of forecasts (95% CI: 29.0–30.3%), RMSE indicates acceptable quality while the Integrated Ice Edge Error (IIEE) decomposition reveals operationally dangerous ice edge displacement — invisible to traditional metrics.

## Repository Structure

```
├── data/
│   └── download_osisaf.py      # Script to download OSI SAF CDR/ICDR data
├── notebooks/
│   └── validation_experiment.ipynb  # Full experiment (runs on Google Colab)
├── src/
│   └── iiee.py                 # IIEE decomposition functions
├── results/
│   ├── all_validation_results.csv
│   ├── figures/                # PNG + PDF figures
│   └── tables/                 # CSV tables
├── requirements.txt
└── LICENSE
```

## Data

**Source:** EUMETSAT OSI SAF sea ice concentration Climate Data Record (CDR v3p0) and Interim CDR (ICDR v3p0).

- Grid: EASE-Grid 2.0, 25 km resolution (625 km²/cell)
- Period: 2019–2024 (training: 2019–Nov 2021; test: Jan 2022–Dec 2024)
- Region: Kara Sea (65–82°N, 55–100°E) and Laptev Sea (70–82°N, 100–145°E)

To download the raw data (~2 GB):

```bash
python data/download_osisaf.py
```

## Models

| Model | Type | Parameters |
|-------|------|------------|
| Persistence | Null hypothesis (no training) | 0 |
| LSTM | Pixelwise temporal | ~5K |
| U-Net | Spatial encoder-decoder | ~300K |
| ConvLSTM | Spatiotemporal | ~100K |

All neural models trained with MSE loss, Adam optimizer, 10% validation split. A separate model per lead time (1, 3, 5, 7, 10 days).

## Reproducing the Experiment

### Option A: Google Colab (recommended)

1. Upload `notebooks/validation_experiment.ipynb` to Google Colab
2. Enable GPU runtime (T4 or better)
3. Run all cells (~65 min on RTX 3090, ~4h on Colab T4)

### Option B: Local

```bash
pip install -r requirements.txt
python data/download_osisaf.py
jupyter notebook notebooks/validation_experiment.ipynb
```

## Results Summary

| Model | Disagreement Rate | RMSE (1d) | ME/IIEE (1d) |
|-------|------------------|-----------|--------------|
| Persistence | 25.2% | 0.031 | 0.503 |
| LSTM | 27.5% | 0.047 | 0.504 |
| U-Net | **35.0%** | 0.049 | 0.463 |
| ConvLSTM | 30.2% | 0.051 | 0.467 |

Disagreement = RMSE < 0.10 but ME/IIEE > 0.50 (forecast appears good by traditional metrics but has dangerous ice edge displacement).

## Citation

```bibtex
@inproceedings{bolkhovskiy2025iiee,
  author    = {Bolkhovskiy, Ilya and Bidenko, Sergey},
  title     = {Implementation and Experimental Validation of a Spatial Error
               Decomposition Framework for Neural Network Sea Ice Forecasts
               Along the Northern Sea Route},
  booktitle = {Proceedings of TITDS-XV-2025},
  year      = {2025},
  publisher = {Springer},
  series    = {LNCS}
}
```

## License

MIT
