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


class StateEnricher:

    def __init__(self, state: dict, repository_name):
        self.state = state
        self.repository_name = repository_name

    @staticmethod
    def normalize(value, max_value):
        return 100 * float(value) / float(max_value)

    def hydrate(self):
        total_number_of_objects = (
            self.state[
                "plugins_git_repo_metrics_numberoflooseobjects_" + self.repository_name
            ]
            + self.state[
                "plugins_git_repo_metrics_numberofpackedobjects_" + self.repository_name
            ]
        )

        self.state["bitmap_index_misses_pct"] = self.normalize(
            self.state[
                "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_"
                + self.repository_name
            ],
            total_number_of_objects,
        )

        self.state["loose_objects_pct"] = self.normalize(
            self.state[
                "plugins_git_repo_metrics_numberoflooserefs_" + self.repository_name
            ],
            total_number_of_objects,
        )
