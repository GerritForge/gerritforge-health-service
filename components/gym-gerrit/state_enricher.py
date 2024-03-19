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


class HydrationNotPossible(RuntimeError):
    def __init__(self, msg: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class StateEnricher:
    __number_of_decimals = 1
    __required_metrics = {
        "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_",
        "plugins_git_repo_metrics_numberoflooseobjects_",
        "plugins_git_repo_metrics_numberofpackedobjects_",
        "plugins_git_repo_metrics_numberoflooserefs_",
        "plugins_git_repo_metrics_numberofpackedrefs_",
    }

    def __init__(self, state: dict, repository_name):
        self.state = state
        self.repository_name = repository_name
        self.required_metrics_keys = self._metrics_with_repository(
            StateEnricher.__required_metrics
        )

    @staticmethod
    def normalize(value, max_value):
        return 100 * float(value) / float(max_value)

    @staticmethod
    def discretize_pct(value_pct, number_of_decimals):
        return round(value_pct / 100, number_of_decimals)

    def hydrate(self, number_of_decimals=__number_of_decimals):
        """Hydrates the retrieved state with normalized and discretized values of the required metrics.

        Args:
            number_of_decimals (_type_, optional): rounding factor. Defaults to __number_of_decimals.

        Raises:
            HydrationNotPossible: when required metrics are not evident in the state. The exception\n
            message contains the list of missing metrics.
        """
        missing_keys = {
            key for key in self.required_metrics_keys if key not in self.state
        }
        if missing_keys:
            raise HydrationNotPossible(f"Missing metrics: {missing_keys}")

        total_number_of_objects = (
            self.state[
                "plugins_git_repo_metrics_numberoflooseobjects_" + self.repository_name
            ]
            + self.state[
                "plugins_git_repo_metrics_numberofpackedobjects_" + self.repository_name
            ]
        )

        self.state["bitmap_index_misses_pct"] = round(
            self.normalize(
                self.state[
                    "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_"
                    + self.repository_name
                ],
                total_number_of_objects,
            ),
            0,
        )

        loose_objects_pct = self.normalize(
            self.state[
                "plugins_git_repo_metrics_numberoflooseobjects_" + self.repository_name
            ],
            total_number_of_objects,
        )
        self.state["loose_objects_pct"] = loose_objects_pct

        self.state["loose_objects_discretised"] = self.discretize_pct(
            loose_objects_pct, number_of_decimals
        )

        total_number_of_refs = (
            self.state[
                "plugins_git_repo_metrics_numberoflooserefs_" + self.repository_name
            ]
            + self.state[
                "plugins_git_repo_metrics_numberofpackedrefs_" + self.repository_name
            ]
        )

        self.state["loose_refs_discretised"] = self.discretize_pct(
            self.normalize(
                self.state[
                    "plugins_git_repo_metrics_numberoflooserefs_" + self.repository_name
                ],
                total_number_of_refs,
            ),
            number_of_decimals,
        )

    def _metrics_with_repository(self, metrics: set[str]):
        return [f"{key}{self.repository_name}" for key in metrics]
