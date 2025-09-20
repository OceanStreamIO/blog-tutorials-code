from pathlib import Path
from typing import Optional, Dict

from prefect import flow, task
from dask.distributed import LocalCluster
from prefect_dask import DaskTaskRunner
from prefect.futures import as_completed


DEFAULT_INPUT_DIR = Path("../raw_data")
S3_BUCKET_NAME = "xarray-zarr-demo"


@task(
    retries=3,
    retry_delay_seconds=60,
    task_run_name="convert-to-zarr-{raw_path}",
)
def convert_single_raw_to_zarr(
    raw_path: str,
    s3_bucket: str,
    s3_prefix: str = "",
    sonar_model: str = "EK60",
    overwrite: bool = True,
    storage_options: Optional[Dict] = None
) -> str:
    # Lazy import so workers don't need echopype at collection time
    import echopype as ep

    raw_path_p = Path(raw_path)
    if not raw_path_p.exists():
        raise FileNotFoundError(f"Input RAW file not found: {raw_path}")

    key_prefix = s3_prefix.strip("/")

    key = f"{key_prefix}/{raw_path_p.stem}.zarr" if key_prefix else f"{raw_path_p.stem}.zarr"
    zarr_uri = f"s3://{s3_bucket}/{key}"

    ed = ep.open_raw(str(raw_path_p), sonar_model=sonar_model)
    ed.to_zarr(zarr_uri, overwrite=overwrite, output_storage_options=storage_options)

    return zarr_uri


@flow(
    name="convert-raw-to-zarr",
    log_prints=True,
    task_runner=DaskTaskRunner(address="tcp://127.0.0.1:8786")
)
def convert_raw_to_zarr(
    input_dir: str,
    s3_bucket: str,
    s3_prefix: str = "",
    sonar_model: str = "EK60",
    overwrite: bool = True,
    glob_pattern: str = "*.raw",
    storage_options: Optional[Dict] = None
):
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    raw_files = sorted(input_path.glob(glob_pattern))
    if not raw_files:
        print(f"No files matching '{glob_pattern}' found in {input_dir}.")
        return

    in_flight = []
    batch_size = 2

    for rp in raw_files:
        task = convert_single_raw_to_zarr.submit(
            raw_path=str(rp),
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            sonar_model=sonar_model,
            overwrite=overwrite,
            storage_options=storage_options
        )
        in_flight.append(task)

        if len(in_flight) >= batch_size:
            finished = next(as_completed(in_flight))
            in_flight.remove(finished)

    for future_task in in_flight:
        future_task.result()


if __name__ == "__main__":
    cluster = LocalCluster(
        n_workers=2,
        scheduler_port=8786,
        threads_per_worker=1,
        memory_limit="8GB"
    )
    client = cluster.get_client()

    convert_raw_to_zarr.serve(
        name="convert-raw-to-zarr-serve",
        parameters={
            "input_dir": str(DEFAULT_INPUT_DIR),
            "s3_bucket": S3_BUCKET_NAME,
            "s3_prefix": "echodata",
            "sonar_model": "EK60",
            "overwrite": True,
            "glob_pattern": "*.raw",
            "storage_options": {}
        },
    )
