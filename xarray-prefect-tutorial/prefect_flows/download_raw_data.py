import logging
import sys
import httpx
from pathlib import Path
from prefect import flow, task
from prefect.task_runners import ThreadPoolTaskRunner


DEST_FOLDER = Path("../raw_data")
BUCKET_URL = "https://noaa-wcsd-pds.s3.amazonaws.com"
PREFIX = "data/raw/Henry_B._Bigelow/HB1907/EK60"
FILENAMES = [
    "D20190727-T035511.raw",
    "D20190727-T042803.raw",
    "D20190727-T050056.raw",
    "D20190727-T053138.raw",
    "D20190727-T060130.raw"
]


@task(
    retries=5,
    retry_delay_seconds=30,
    task_run_name="download-file-{file_name}",
)
def download_file(url: str, download_dir: str, file_name: str) -> str:
    print(f"Starting download of {file_name} from {url}...")
    dest = Path(download_dir) / url.rsplit("/", 1)[-1]
    dest.parent.mkdir(parents=True, exist_ok=True)

    with httpx.stream("GET", url, timeout=None) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)

    print(f"Finished download of {file_name} to {dest}")

    return str(dest)


@flow(
    name="download-raw-data",
    task_runner=ThreadPoolTaskRunner(max_workers=2)
)
def download_raw_data(download_dir: str):
    task_futures = []

    for file_name in FILENAMES:
        url = f"{BUCKET_URL}/{PREFIX}/{file_name}"
        task_futures.append(download_file.submit(url=url, download_dir=download_dir, file_name=file_name))

    for future in task_futures:
        future.result()

    print("All files have been downloaded.")


if __name__ == "__main__":
    try:
        download_raw_data.serve(
            name='download-raw-data-from-noaa-s3',
            parameters={
                'download_dir': str(DEST_FOLDER)
            }
        )
    except Exception as e:
        logging.critical(f'Unhandled exception: {e}', exc_info=True)
        sys.exit(1)
