import gymnasium as gym
import subprocess
from git import Repo
import shutil
import numpy as np
from gymnasium import spaces
import os

class GerritEnv(gym.Env):
    def __init__(self, gerritUrl, gitRepositoryPath, repositoryName, actionsJarPath):
        self.gerritUrl = gerritUrl
        self.gitRepositoryPath = gitRepositoryPath
        self.actionsJarPath = actionsJarPath
        self.repositoryName = repositoryName

        self.action_space = spaces.Discrete(3)

        self._action_to_action_name = {
            0: "NothingAction",
            1: "BitmapGenerationAction",
            2: "PackRefsAction",
        }

        
        self.observations = ["plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses",
                             "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse",
                             "plugins_git_repo_metrics_numberofbitmaps",
                             "plugins_git_repo_metrics_numberofdirectories",
                             "plugins_git_repo_metrics_numberofemptydirectories",
                             "plugins_git_repo_metrics_numberoffiles",
                             "plugins_git_repo_metrics_numberofkeepfiles",
                             "plugins_git_repo_metrics_numberoflooseobjects",
                             "plugins_git_repo_metrics_numberoflooserefs",
                             "plugins_git_repo_metrics_numberofpackedobjects",
                             "plugins_git_repo_metrics_numberofpackedrefs",
                             "plugins_git_repo_metrics_numberofpackfiles",
                             "plugins_git_repo_metrics_sizeoflooseobjects",
                             "plugins_git_repo_metrics_sizeofpackedobjects",
                             "proc_cpu_num_cores",
                             "proc_cpu_system_load",
                             "proc_cpu_usage"]
  
        self.observation_space = self.build_ghs_obs_space(self.observations)

    def build_ghs_obs_space(self, observations):
        lower_obs_bound = {
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses":-1,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse":-1,
            "plugins_git_repo_metrics_numberofbitmaps":0,
            "plugins_git_repo_metrics_numberofdirectories":0,
            "plugins_git_repo_metrics_numberofemptydirectories":0,
            "plugins_git_repo_metrics_numberoffiles":0,
            "plugins_git_repo_metrics_numberofkeepfiles":0,
            "plugins_git_repo_metrics_numberoflooseobjects":0,
            "plugins_git_repo_metrics_numberoflooserefs":0,
            "plugins_git_repo_metrics_numberofpackedobjects":0,
            "plugins_git_repo_metrics_numberofpackedrefs":0,
            "plugins_git_repo_metrics_numberofpackfiles":0,
            "plugins_git_repo_metrics_sizeoflooseobjects":0,
            "plugins_git_repo_metrics_sizeofpackedobjects":0,
            "proc_cpu_num_cores":0,
            "proc_cpu_system_load":0,
            "proc_cpu_usage":0,
        }
        higher_obs_bound = {
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses":+ np.inf,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse":+ np.inf,
            "plugins_git_repo_metrics_numberofbitmaps":+ np.inf,
            "plugins_git_repo_metrics_numberofdirectories":+ np.inf,
            "plugins_git_repo_metrics_numberofemptydirectories":+ np.inf,
            "plugins_git_repo_metrics_numberoffiles":+ np.inf,
            "plugins_git_repo_metrics_numberofkeepfiles":+ np.inf,
            "plugins_git_repo_metrics_numberoflooseobjects":+ np.inf,
            "plugins_git_repo_metrics_numberoflooserefs":+ np.inf,
            "plugins_git_repo_metrics_numberofpackedobjects":+ np.inf,
            "plugins_git_repo_metrics_numberofpackedrefs":+ np.inf,
            "plugins_git_repo_metrics_numberofpackfiles":+ np.inf,
            "plugins_git_repo_metrics_sizeoflooseobjects":+ np.inf,
            "plugins_git_repo_metrics_sizeofpackedobjects":+ np.inf,
            "proc_cpu_num_cores":+ np.inf,
            "proc_cpu_system_load":+ np.inf,
            "proc_cpu_usage":+ np.inf,
        }

        low = np.array([lower_obs_bound[o] for o in observations])
        high = np.array([higher_obs_bound[o] for o in observations])
        shape = (len(observations),)
        return gym.spaces.Box(low, high, shape)

    def step(self, action):
        #TODO scrape metrics before action

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

        #TODO scrape metrics after action
        observation = self._get_state()
        #Add truncated
        return observation, 1

    def get_current_state(self):
        return self._get_state()


    def _get_state(self):
        # #TODO ignore lines with -1 in all fields
        # #TODO scrape metrics to get the current state
        # #timestamp,plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses,plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_test_repo,plugins_git_repo_metrics_combinedrefssha1_test_repo,plugins_git_repo_metrics_numberofbitmaps_test_repo,plugins_git_repo_metrics_numberofdirectories_test_repo,plugins_git_repo_metrics_numberofemptydirectories_test_repo,plugins_git_repo_metrics_numberoffiles_test_repo,plugins_git_repo_metrics_numberofkeepfiles_test_repo,plugins_git_repo_metrics_numberoflooseobjects_test_repo,plugins_git_repo_metrics_numberoflooserefs_test_repo,plugins_git_repo_metrics_numberofpackedobjects_test_repo,plugins_git_repo_metrics_numberofpackedrefs_test_repo,plugins_git_repo_metrics_numberofpackfiles_test_repo,plugins_git_repo_metrics_sizeoflooseobjects_test_repo,plugins_git_repo_metrics_sizeofpackedobjects_test_repo,proc_cpu_num_cores,proc_cpu_system_load,proc_cpu_usage
        # return np.array([1710252846,10.0,5.0,7.0,3.0,1.0,16.0,0.0,0.0,2.0,84.0,1.0,7.0,0.0,6075.0,10.0,3.0615234375,62.549751])

        state = {'plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses': 10.0, 
                'plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse': 5.0,  
                'plugins_git_repo_metrics_numberofbitmaps': 7.0, 
                'plugins_git_repo_metrics_numberofdirectories': 3.0, 
                'plugins_git_repo_metrics_numberofemptydirectories': 1.0, 
                'plugins_git_repo_metrics_numberoffiles': 16.0, 
                'plugins_git_repo_metrics_numberofkeepfiles': 0.0, 
                'plugins_git_repo_metrics_numberoflooseobjects': 0.0, 
                'plugins_git_repo_metrics_numberoflooserefs': 2.0, 
                'plugins_git_repo_metrics_numberofpackedobjects': 84.0, 
                'plugins_git_repo_metrics_numberofpackedrefs': 1.0, 
                'plugins_git_repo_metrics_numberofpackfiles': 7.0, 
                'plugins_git_repo_metrics_sizeoflooseobjects': 0.0, 
                'plugins_git_repo_metrics_sizeofpackedobjects': 6075.0, 
                'proc_cpu_num_cores': 10.0, 
                'proc_cpu_system_load': 3.0615234375, 
                'proc_cpu_usage': 62.549751}
        return np.array([state[o] for o in self.observations])
