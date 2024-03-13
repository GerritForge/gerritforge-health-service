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

import os
import requests
from prometheus_client.parser import text_string_to_metric_families
import csv
import time
from enum import Enum
import json


class Mode(Enum):
    batch = "batch"
    snapshot = "snapshot"


class Scraper:
    __system_metrics = {"proc_cpu_num_cores", "proc_cpu_system_load", "proc_cpu_usage"}
    __metrics_prefixes = {
        "plugins_git_repo_metrics_",
        "plugins_gerrit_per_repo_metrics_collector_ghs_",
    }

    def __init__(
        self,
        mode: Mode,
        repository,
        prometheus_url,
        output_csv_file=None,
        bearer_token=None,
    ):
        self.mode = mode
        self.repository = repository
        self.url = prometheus_url
        self.output_csv_file = output_csv_file
        self.bearer_token = bearer_token

    def fetch_data(self):
        try:
            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

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
            samples = {}
            for family in text_string_to_metric_families(data.decode("utf-8")):

                for sample in family.samples:
                    if sample.name in Scraper.__system_metrics or (
                        sample.name.startswith(tuple(Scraper.__metrics_prefixes))
                        and sample.name.endswith(self.repository)
                    ):
                        samples[sample.name] = sample.value

            sorted_keys = sorted(samples.keys())
            sorted_keys.insert(0, "timestamp")
            samples["timestamp"] = scraping_time
            return (sorted_keys, samples)

        except Exception as e:
            print(f"Failed to parse data: {e}")

    def store_metrics_as_csv(self, keys, values):
        add_header = False if os.path.exists(self.output_csv_file) else True
        with open(self.output_csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            if add_header:
                writer.writerow(keys)
                add_header = False
            writer.writerow(values)

    def run(self):
        scraping_time = int(time.time())
        if self.mode == Mode.batch:
            self.__batch(scraping_time)
        else:
            self.__snapshot(scraping_time)

    def __batch(self, scraping_time):
        print(f" * * * Scraping: {self.url}")
        data = self.fetch_data()
        if data:
            (sorted_keys, samples) = self.parse_data(data, scraping_time)
            sorted_values = [samples[key] for key in sorted_keys]
            self.store_metrics_as_csv(sorted_keys, sorted_values)
        else:
            print("No data to parse.")

    def __snapshot(self, scraping_time):
        data = self.fetch_data()
        if data:
            (_, samples) = self.parse_data(data, scraping_time)
            jsonSamples = json.dumps(samples)
            print(jsonSamples)
            return jsonSamples
        else:
            print("{}")
            return json.dumps("{}")
