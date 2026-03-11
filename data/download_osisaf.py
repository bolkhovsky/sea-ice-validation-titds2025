#!/usr/bin/env python3
"""Download OSI SAF CDR/ICDR sea ice concentration data for the experiment.

Data source: EUMETSAT OSI SAF
- CDR v3p0 (2019-2020): ftp://osisaf.met.no/reprocessed/ice/conc/v3p0/
- ICDR v3p0 (2021-2024): ftp://osisaf.met.no/prod/ice/conc_cdr_icdr/

Grid: EASE-Grid 2.0, 25 km resolution
Format: NetCDF4
"""

import ftplib
import os
from datetime import date, timedelta
from pathlib import Path

FTP_HOST = "osisaf.met.no"
CDR_BASE = "/reprocessed/ice/conc/v3p0/{year}/{month:02d}/"
ICDR_BASE = "/prod/ice/conc_cdr_icdr/{year}/{month:02d}/"

DATA_DIR = Path(__file__).parent / "raw"


def download_year(year: int, output_dir: Path):
    """Download all daily SIC files for a given year."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # CDR for 2019-2020, ICDR for 2021+
    base = CDR_BASE if year <= 2020 else ICDR_BASE

    ftp = ftplib.FTP(FTP_HOST)
    ftp.login()

    current = date(year, 1, 1)
    end = date(year, 12, 31)

    while current <= end:
        remote_dir = base.format(year=current.year, month=current.month)
        try:
            ftp.cwd(remote_dir)
            files = ftp.nlst()
            # Find the file for this date (pattern: *YYYYMMDD*.nc)
            date_str = current.strftime("%Y%m%d")
            matches = [f for f in files if date_str in f and f.endswith(".nc")]
            for fname in matches:
                local_path = output_dir / fname
                if local_path.exists() and local_path.stat().st_size > 10_000:
                    pass  # Skip already downloaded
                else:
                    print(f"Downloading {fname}...")
                    with open(local_path, "wb") as fp:
                        ftp.retrbinary(f"RETR {fname}", fp.write)
        except ftplib.error_perm as e:
            print(f"  Skip {current}: {e}")
        current += timedelta(days=1)

    ftp.quit()


if __name__ == "__main__":
    for year in range(2019, 2025):
        print(f"\n=== {year} ===")
        download_year(year, DATA_DIR / str(year))
    print("\nDone. Raw data saved to:", DATA_DIR)
