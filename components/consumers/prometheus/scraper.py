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

import requests
from prometheus_client.parser import text_string_to_metric_families
import csv
import time

class Scraper:
    def __init__(self, prometheus_url, output_csv_file, bearer_token=None):
        self.url = prometheus_url
        self.output_csv_file=output_csv_file
        self.bearer_token = bearer_token

    def fetch_data(self):
        try:
            headers = {}
            if self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'

            response = requests.get(self.url, headers=headers)

            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            return None

    def parse_data(self, data, scraping_time):
        try:
            for family in text_string_to_metric_families(data.decode('utf-8')):
                for sample in family.samples:
                    self.store_metrics_as_csv((scraping_time, sample[0], sample[2]))

        except Exception as e:
            print(f"Failed to parse data: {e}")

    def store_metrics_as_csv(self, sample):
        with open(self.output_csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(sample)

    def run(self):
        print(f" * * * Scraping: {self.url}")
        scraping_time = int(time.time())
        data = self.fetch_data()
        if data:
            self.parse_data(data, scraping_time)
        else:
            print("No data to parse.")