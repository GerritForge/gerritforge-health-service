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


class Scraper:
    __system_metrics = {"proc_cpu_num_cores", "proc_cpu_system_load", "proc_cpu_usage"}
    __metrics_prefixes = {
        "plugins_git_repo_metrics_",
        "plugins_gerrit_per_repo_metrics_collector_ghs_",
    }
    __git_repo_metrics: set = {
        "plugins_git_repo_metrics_combinedrefssha1_",
        "plugins_git_repo_metrics_numberofbitmaps_",
        "plugins_git_repo_metrics_numberofdirectories_",
        "plugins_git_repo_metrics_numberofemptydirectories_",
        "plugins_git_repo_metrics_numberoffiles_",
        "plugins_git_repo_metrics_numberofkeepfiles_",
        "plugins_git_repo_metrics_numberoflooseobjects_",
        "plugins_git_repo_metrics_numberoflooserefs_",
        "plugins_git_repo_metrics_numberofpackedobjects_",
        "plugins_git_repo_metrics_numberofpackedrefs_",
        "plugins_git_repo_metrics_numberofpackfiles_",
        "plugins_git_repo_metrics_sizeoflooseobjects_",
        "plugins_git_repo_metrics_sizeofpackedobjects_",
    }
    __git_per_repo_metrics = {
        "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_",
        "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_",
    }
    __all_metrics_number = (
        len(__system_metrics)
        + len(__git_repo_metrics)
        + len(__git_per_repo_metrics)
        + 1  # for timestamp
    )

    def __init__(
        self,
        repository,
        prometheus_url,
        output_csv_file=None,
        bearer_token=None,
    ):
        self.repository = repository.lower()
        self.url = prometheus_url
        self.output_csv_file = output_csv_file
        self.bearer_token = bearer_token
        self.mertics_keys = Scraper.__system_metrics.union(
            self._metrics_with_repository(Scraper.__git_repo_metrics)
        ).union(self._metrics_with_repository(Scraper.__git_per_repo_metrics))

    def _fetch_data(self):
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

    def _parse_data(self, data, scraping_time):
        try:
            samples = {}
            for family in text_string_to_metric_families(data.decode("utf-8")):

                for sample in family.samples:
                    lower_name = sample.name.lower()
                    if lower_name in Scraper.__system_metrics or (
                        lower_name.startswith(tuple(Scraper.__metrics_prefixes))
                        and lower_name.endswith(self.repository)
                    ):
                        samples[lower_name] = sample.value

            samples_keys = samples.keys()
            samples_with_none_values = {
                key: samples[key] if key in samples_keys else None
                for key in self.mertics_keys
            }
            sorted_keys = sorted(samples_with_none_values.keys())
            sorted_keys.insert(0, "timestamp")
            samples_with_none_values["timestamp"] = scraping_time
            samples_with_none_values.items()
            return (sorted_keys, samples_with_none_values)

        except Exception as e:
            print(f"Failed to parse data: {e}")

    def _store_metrics_as_csv(self, keys, values):
        add_header = False if os.path.exists(self.output_csv_file) else True
        with open(self.output_csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            if add_header:
                writer.writerow(keys)
                add_header = False
            writer.writerow(values)

    def scrape_to_csv(self, scraping_time=int(time.time())):
        """Collects metrics and stores them to as CSV to the provided file.

        Args:
            scraping_time (_type_, optional): collection time. Defaults to int(time.time()).
        """
        print(f" * * * Scraping: {self.url}")
        data = self._fetch_data()
        if data:
            (sorted_keys, samples) = self._parse_data(data, scraping_time)
            sorted_values = [samples[key] for key in sorted_keys]
            self._store_metrics_as_csv(sorted_keys, sorted_values)
        else:
            print("No data to parse.")

    def scrape_to_dict(
        self, scraping_time=int(time.time())
    ) -> tuple[dict[str, float], bool]:
        """Collects metrics and returns them as dict with infromation if all\n
        metrics were collected.

        Args:
            scraping_time (_type_, optional): collection time. Defaults to int(time.time()).

        Returns:
            `tuple[dict[str,float], bool]`: metrics dictionary (name, value) turned to dict and\n
            `True` if all metrics were collected, `False` if some were missing
        """
        data = self._fetch_data()
        if data:
            (_, samples) = self._parse_data(data, scraping_time)
            existing_samples = self._only_existing_metrics(samples)
            return (
                existing_samples,
                len(existing_samples) == Scraper.__all_metrics_number,
            )
        else:
            return ({}, False)

    def _metrics_with_repository(self, metrics: set[str]):
        return [f"{key}{self.repository}" for key in metrics]

    def _only_existing_metrics(self, metrics: set[str, None | float]):
        return {
            key: value for key, value in metrics.items() if metrics[key] is not None
        }
