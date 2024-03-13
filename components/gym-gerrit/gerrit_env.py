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
        print("Current metrics")
        print(current_metrics)

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
        print("New metrics")
        print(new_metrics)
        
        observation = np.array([np.float32(new_metrics[o]) for o in self.observations])

        #Add truncated
        return observation, 1

    def get_current_state(self):
        state = self._get_state()
        return np.array([np.float32(state[o]) for o in self.observations])


    def _get_state(self):
        # #TODO ignore lines with -1 in all fields
        state_json = self.scraper.run()
        state = json.loads(state_json)

        # Mutates the state
        StateEnricher(state, self.sanitized_repo_name).hydrate()

        return state