#!/usr/bin/env python3
"""Download OSI SAF sea ice concentration data for the experiment.

Data source: EUMETSAT OSI SAF, anonymous FTP (osisaf.met.no)
- CDR v3p0 (2019-2020): /reprocessed/ice/conc/v3p0/YYYY/MM/
- ICDR (2021-2024):      /archive/ice/conc/YYYY/MM/

Both products are on EASE-Grid 2.0 at 12.5 km native resolution.
The experiment subsamples to 25 km (every 2nd pixel) during preprocessing;
see notebooks/validation_experiment.ipynb for details.

Grid: EASE-Grid 2.0, Northern Hemisphere
Format: NetCDF4
Total download: ~2.5 GB (2,192 files)
"""

import ftplib
import os
from datetime import date, timedelta
from pathlib import Path

FTP_HOST = "osisaf.met.no"

# CDR v3p0: reprocessed climate data record (2019-2020)
CDR_PATH = "/reprocessed/ice/conc/v3p0/{year}/{month:02d}/"
# ICDR: interim climate data record from the archive (2021+)
ICDR_PATH = "/archive/ice/conc/{year}/{month:02d}/"

# Only download Northern Hemisphere EASE-Grid files
FILE_PATTERN = "ice_conc_nh_ease-125_multi_{date}1200.nc"

DATA_DIR = Path(__file__).parent / "raw"


def get_remote_path(d: date) -> str:
    """Return FTP directory path for a given date."""
    if d.year <= 2020:
        return CDR_PATH.format(year=d.year, month=d.month)
    return ICDR_PATH.format(year=d.year, month=d.month)


def download_range(start: date, end: date, output_dir: Path):
    """Download daily SIC files for a date range."""
    output_dir.mkdir(parents=True, exist_ok=True)

    ftp = ftplib.FTP(FTP_HOST, timeout=60)
    ftp.login()
    print(f"Connected to {FTP_HOST} (anonymous)")

    downloaded, skipped, errors = 0, 0, 0
    current = start
    last_dir = None

    while current <= end:
        remote_dir = get_remote_path(current)
        fname = FILE_PATTERN.format(date=current.strftime("%Y%m%d"))
        local_path = output_dir / fname

        # Skip if already downloaded
        if local_path.exists() and local_path.stat().st_size > 10_000:
            skipped += 1
            current += timedelta(days=1)
            continue

        try:
            # Only cd if directory changed
            if remote_dir != last_dir:
                ftp.cwd(remote_dir)
                last_dir = remote_dir

            with open(local_path, "wb") as fp:
                ftp.retrbinary(f"RETR {fname}", fp.write)
            downloaded += 1

            if downloaded % 100 == 0:
                print(f"  Downloaded {downloaded} files...")

        except ftplib.error_perm as e:
            errors += 1
            if local_path.exists():
                local_path.unlink()
            if errors <= 5:
                print(f"  Warning: {current} - {e}")
        except (ftplib.error_temp, EOFError, ConnectionResetError) as e:
            # Reconnect on transient errors
            print(f"  Reconnecting after error on {current}: {e}")
            try:
                ftp.quit()
            except Exception:
                pass
            ftp = ftplib.FTP(FTP_HOST, timeout=60)
            ftp.login()
            last_dir = None
            errors += 1

        current += timedelta(days=1)

    try:
        ftp.quit()
    except Exception:
        pass

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {errors} errors")
    return downloaded


if __name__ == "__main__":
    START = date(2019, 1, 1)
    END = date(2024, 12, 31)

    print(f"Downloading OSI SAF SIC data: {START} to {END}")
    print(f"  CDR v3p0 (2019-2020): {CDR_PATH}")
    print(f"  ICDR archive (2021-2024): {ICDR_PATH}")
    print(f"  Output: {DATA_DIR}")
    print()

    n = download_range(START, END, DATA_DIR)
    print(f"\nTotal files in {DATA_DIR}: {len(list(DATA_DIR.glob('*.nc')))}")
