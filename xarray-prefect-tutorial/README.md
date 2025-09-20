## Cloud-Native Ocean Data Processing

This repository contains code accompanying a long-form tutorial on our OceanStream blog about building a cloud-native stack for scientific data processing (focused on water columns sonar data) using xarray, Zarr, Dask, echopype, and Prefect 3.

Tools: [xarray](https://docs.xarray.dev/), [Zarr](https://zarr.readthedocs.io/), [Dask](https://docs.dask.org/), [echopype](https://echopype.readthedocs.io/), [Prefect 3](https://docs.prefect.io/)

### 1) xarray example (script + notebook)
- Files: `xarray_example.py`, `xarray_example.ipynb`
- What: Create synthetic Dataset, chunk, write/read Zarr on S3
- Run (script):
```bash
pip install xarray zarr dask distributed s3fs
python xarray_example.py
```
- Run (notebook via JupyterLab):
```bash
pip install jupyterlab xarray zarr dask distributed s3fs
jupyter lab xarray_example.ipynb
```

### 2) Prefect flows (download + convert)
- Files: `prefect_flows/download_raw_data.py`, `prefect_flows/convert_to_zarr.py`
- What: Download EK60 RAW files and convert to Zarr via echopype; parallelized with Dask
- Run:

```bash
pip install prefect echopype httpx dask distributed s3fs
cd prefect_flows
python download_raw_data.py         # downloads to ../raw_data
python convert_to_zarr.py          # starts local Dask; writes Zarr to S3
```
- Configure: set `S3_BUCKET_NAME` and `s3_prefix` in `convert_to_zarr.py`. 

## License
MIT License. See [LICENSE](LICENSE) for details.
