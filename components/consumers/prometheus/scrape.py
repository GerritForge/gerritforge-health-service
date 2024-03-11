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
import time
import schedule

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prometheus Scraper")
    parser.add_argument("url", help="prometheus URL to scrape")
    parser.add_argument("--bearer-token", help="Bearer token for authentication")
    parser.add_argument("--output-csv-file", required=True, help="the full path of the output csv file")
    args = parser.parse_args()

    scraper = Scraper(args.url, args.output_csv_file, args.bearer_token)

    scraper.run()
    schedule.every(1).minutes.do(scraper.run)

    while True:
        schedule.run_pending()
        time.sleep(1)
