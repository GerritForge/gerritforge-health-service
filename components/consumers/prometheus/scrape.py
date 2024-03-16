# Copyright (C) 2024 GerritForge, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from scraper import Scraper
import argparse
from enum import Enum
import time
import schedule


class Mode(Enum):
    batch = "batch"
    snapshot = "snapshot"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prometheus Scraper")
    parser.add_argument("url", help="prometheus URL to scrape")
    parser.add_argument("--bearer-token", help="Bearer token for authentication")
    parser.add_argument(
        "--repository",
        required=True,
        help="The repository to look after for detailed metrics",
    )
    parser.add_argument(
        "--output-csv-file",
        required=False,
        help=f"The full path of the output csv file. Required in {Mode.batch.value} mode.",
    )
    parser.add_argument(
        "--mode",
        required=False,
        type=Mode,
        default=Mode.batch,
        help=f"The scraper modes: '{Mode.batch.value}' (default) where it keeps getting and storing metrics in the "
        + f"`--output-csv-file`, '{Mode.snapshot.value}' where it will get metrics and return them as JSON",
    )
    args = parser.parse_args()

    if args.mode == Mode.batch and args.output_csv_file is None:
        parser.error(f"--mode {Mode.batch.value} requires `--output-csv-file` value.")

    scraper = Scraper(
        args.repository.replace("-", "_"),
        args.url,
        args.output_csv_file,
        args.bearer_token,
    )

    if args.mode == Mode.snapshot:
        print(scraper.scrape_to_dict())
    else:
        scraper.scrape_to_csv()
        schedule.every(1).minutes.do(scraper.scrape_to_csv)

        while True:
            schedule.run_pending()
            time.sleep(1)
