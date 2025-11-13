# North Atlantic SST Analysis with ERA5 ARCO

This notebook demonstrates how to compute and visualise **Sea Surface Temperature (SST)** over the North Atlantic region using the [Analysis‑Ready, Cloud‑Optimised ERA5 dataset (ARCO)](https://github.com/google-research/arco-era5). The data are hosted in a public Google Cloud Storage bucket and can be streamed lazily into memory using **xarray** and **dask**.

We will:

1. Load the ARCO ERA5 dataset (surface and pressure levels) from its Zarr store.
2. Subset the domain to the North Atlantic region (approx. 5–32°E, 55–72°N) and convert SST from Kelvin to Celsius.
3. Mask land grid cells and heavy sea‑ice by thresholding the sea‑ice area fraction.
4. Aggregate the SST to monthly means.
5. Extract the latest available monthly mean SST field.
6. Plot the results using **Matplotlib** and **Cartopy**.

> **Prerequisites**: You will need recent versions of `xarray`, `dask`, `gcsfs` and `numpy`. Install them with e.g.:
>
> ```bash
> pip install "xarray[complete]" dask[complete] gcsfs cartopy matplotlib numpy
> ```

ARCO ERA5 data are updated monthly; to make sure you access the latest available period, we read the dataset attributes `valid_time_start` and `valid_time_stop` exposed in the Zarr metadata. The dataset path used here streams the unified 0.25° pressure and surface levels dataset.