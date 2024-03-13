import gymnasium as gym
import subprocess
from git import Repo
import shutil
import numpy as np
from gymnasium import spaces
import os
from scraper import Scraper,Mode
import json
from state_enricher import StateEnricher

class GerritEnv(gym.Env):
    def __init__(self, gerritUrl, gitRepositoryPath, repositoryName, actionsJarPath, prometheus_bearer_token):
        prometheus_url = gerritUrl+"/plugins/metrics-reporter-prometheus/metrics"
        self.gerritUrl = gerritUrl
        self.gitRepositoryPath = gitRepositoryPath
        self.actionsJarPath = actionsJarPath
        self.repositoryName = repositoryName
        self.sanitized_repo_name = repositoryName.replace("-", "_")
        self.scraper =  Scraper(mode=Mode.snapshot,
                                repository=self.sanitized_repo_name,
                                prometheus_url=prometheus_url,
                                bearer_token=prometheus_bearer_token)
        self.action_space = spaces.Discrete(3)

        self._action_to_action_name = {
            0: "NothingAction",
            1: "BitmapGenerationAction",
            2: "PackRefsAction",
        }

        self.observations = ["plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_"+self.sanitized_repo_name,
                             "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofbitmaps_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofdirectories_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofemptydirectories_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberoffiles_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofkeepfiles_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberoflooseobjects_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberoflooserefs_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofpackedobjects_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofpackedrefs_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_numberofpackfiles_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_sizeoflooseobjects_"+self.sanitized_repo_name,
                             "plugins_git_repo_metrics_sizeofpackedobjects_"+self.sanitized_repo_name,
                             "proc_cpu_num_cores",
                             "proc_cpu_system_load",
                             "proc_cpu_usage"]

        self._action_to_weight = {
            0: 0,
            1: 1,
            2: 0.2
        }

        self._cost_weights = {
            "bitmap_index_misses_pct": 1/3,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_"+self.sanitized_repo_name: 1/3,
            "action": 1/3
        }

        self.observation_space = self.build_ghs_obs_space(self.observations)

    def build_ghs_obs_space(self, observations):
        lower_obs_bound = {
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_"+self.sanitized_repo_name:-1,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_"+self.sanitized_repo_name:-1,
            "plugins_git_repo_metrics_numberofbitmaps_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofdirectories_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofemptydirectories_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberoffiles_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofkeepfiles_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberoflooseobjects_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberoflooserefs_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofpackedobjects_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofpackedrefs_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_numberofpackfiles_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_sizeoflooseobjects_"+self.sanitized_repo_name:0,
            "plugins_git_repo_metrics_sizeofpackedobjects_"+self.sanitized_repo_name:0,
            "proc_cpu_num_cores":0,
            "proc_cpu_system_load":0,
            "proc_cpu_usage":0,
        }
        higher_obs_bound = {
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_"+self.sanitized_repo_name:+ np.inf,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofbitmaps_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofdirectories_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofemptydirectories_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberoffiles_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofkeepfiles_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberoflooseobjects_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberoflooserefs_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofpackedobjects_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofpackedrefs_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_numberofpackfiles_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_sizeoflooseobjects_"+self.sanitized_repo_name:+ np.inf,
            "plugins_git_repo_metrics_sizeofpackedobjects_"+self.sanitized_repo_name:+ np.inf,
            "proc_cpu_num_cores":+ np.inf,
            "proc_cpu_system_load":+ np.inf,
            "proc_cpu_usage":+ np.inf,
        }

        low = np.array([lower_obs_bound[o] for o in observations])
        high = np.array([higher_obs_bound[o] for o in observations])
        shape = (len(observations),)
        return gym.spaces.Box(low, high, shape)

    def step(self, action):
        current_metrics = self._get_state()

        temporaryRepoDirectory = "/tmp/"+self.repositoryName
        if os.path.exists(temporaryRepoDirectory):
            shutil.rmtree(temporaryRepoDirectory)
        action_name = self._action_to_action_name[action]
        print(action_name)
        java_command = ['java', '-jar', self.actionsJarPath, action_name, self.gitRepositoryPath]
        process = subprocess.Popen(java_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish and capture output
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print("Error occurred while running the JAR file:")
            print(stderr.decode('utf-8'))
        else:
            print("Java JAR file executed successfully:")
            print(stdout.decode('utf-8'))

        Repo.clone_from(self.gerritUrl+"/"+self.repositoryName, temporaryRepoDirectory)

        if os.path.exists(temporaryRepoDirectory):
            shutil.rmtree(temporaryRepoDirectory)

        new_metrics = self._get_state()
    
        #Add truncated
        return new_metrics, self._calc_reward(current_metrics, action, new_metrics)

    def get_current_state(self):
        state = self._get_state()
        return state

    def _calc_reward(self, pre, action, post):
        assert(pre.keys() == post.keys())

        return self._cost_search_for_reuse(pre, post) + self._cost_bitmap_misses(pre, post) + self._cost_action(action)

    def _cost_search_for_reuse(self, pre, post):
        key = 'plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_'+self.sanitized_repo_name
        millis = post[key]

        # TODO: Make configurable or extract from jgit config
        millis_max = 60000*5 
        cp1 = 1000
        cp2 = 60000

        weight = None
        if millis < cp1:
            weight = 0
        elif millis < cp2:
            weight = 0.2
        else:
            weight = 1

        cost = None
        if millis >= millis_max:
            cost = 1
        else:
            cost = weight * (post[key] / millis_max)

        return cost * self._cost_weights[key]

    def _cost_bitmap_misses(self, pre, post):
        key = 'bitmap_index_misses_pct'

        # TODO: Deltas?

        return post[key] * self._cost_weights[key]

    def _cost_action(self, action):
        key = 'action'

        # TODO: Compute actual cost of action?

        return self._action_to_weight[action] * self._cost_weights[key]

    def _get_state(self):
        # #TODO ignore lines with -1 in all fields
        state_json = self.scraper.run()
        state = json.loads(state_json)

        # Mutates the state
        StateEnricher(state, self.sanitized_repo_name).hydrate()
        return state
