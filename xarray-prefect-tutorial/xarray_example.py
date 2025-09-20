import xarray as xr
import numpy as np

# Create a small example dataset and write with a chunking strategy
time = np.arange(0, 3600, 1)  # seconds
range_bin = np.arange(0, 1800, 1)  # samples

ds = xr.Dataset(
    data_vars=dict(
        Sv=(["time", "range_bin"], np.random.randn(time.size, range_bin.size).astype("float32")),
    ),
    coords=dict(time=("time", time), range_bin=("range_bin", range_bin)),
    attrs={"convention": "SONAR-netCDF4 v1.0"},
)

# Choose chunk sizes that reflect read patterns (time-scan, or depth stripes, etc.)
ds_chunked = ds.chunk({"time": 300, "range_bin": 256})

# Write to a Zarr store (could be local or remote object store like S3)
#out = "sonar_scan.zarr"

ds_chunked.to_zarr("s3://xarray-zarr-demo/sonar_scan.zarr",
           mode="w",
           consolidated=True,
           zarr_format=2)

ds2 = xr.open_zarr("s3://xarray-zarr-demo/sonar_scan.zarr")
print(ds2)