import gymnasium as gym
import subprocess
from git import Repo
import git
import shutil
import numpy as np
from gymnasium import spaces
import os
from scraper import Scraper,Mode
import json
from state_enricher import StateEnricher
import datetime
import logging
from git import GitConfigParser

class GerritEnv(gym.Env):
    episode_counter = 0
    start_timestamp = str(datetime.datetime.now().timestamp())

    def __init__(self, gerritUrl, gitRepositoryPath, repositoryName, actionsJarPath, prometheus_bearer_token, username, password):
        prometheus_url = f"http://{gerritUrl}/plugins/metrics-reporter-prometheus/metrics"
        self.gerritUrl = gerritUrl
        self.gitRepositoryPath = gitRepositoryPath
        self.actionsJarPath = actionsJarPath
        self.repositoryName = repositoryName
        self.username = username
        self.password = password
        self.sanitized_repo_name = self.__sanitize_repository_name(repositoryName)
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

        self.observations = ["bitmap_index_misses_pct",
            "loose_objects_discretised",
            "loose_refs_discretised"]

        self._action_to_reward = {
            0: 1,
            1: 0,
            2: 0.8
        }

        self._reward_weights = {
            "bitmap_index_misses_pct": 1/3,
            "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_"+self.sanitized_repo_name: 1/3,
            "action": 1/3
        }

        self.observation_space = self.build_ghs_obs_space(self.observations)


    def build_ghs_obs_space(self, observations):
        lower_obs_bound = {
            "bitmap_index_misses_pct":0,
            "loose_objects_discretised":0,
            "loose_refs_discretised":0
        }
        higher_obs_bound = {
            "bitmap_index_misses_pct":100,
            "loose_objects_discretised":1,
            "loose_refs_discretised":1
        }

        low = np.array([lower_obs_bound[o] for o in observations])
        high = np.array([higher_obs_bound[o] for o in observations])
        shape = (len(observations),)
        return gym.spaces.Box(low, high, shape)

    def step(self, action):
        self.episode_counter += 1
        current_metrics = self._get_state()

        temporaryRepoDirectory = "/tmp/"+self.repositoryName
        if os.path.exists(temporaryRepoDirectory):
            shutil.rmtree(temporaryRepoDirectory)
        action_name = self._action_to_action_name[action]
        logging.info("executing action %s, episode number %d",action_name, self.episode_counter)
        java_command = ['java', '-jar', self.actionsJarPath, action_name, self.gitRepositoryPath]
        process = subprocess.Popen(java_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish and capture output
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
           logging.error("error occured while running the action %s, return code: %d, message:%s", 
                        action_name, process.returncode, stderr.decode('utf-8'))
        else:
            logging.info("action %s executed successfuly", action_name)
        
        git.Repo.clone_from(f"http://{self.username}:{self.password}@{self.gerritUrl}/a/"+self.repositoryName, temporaryRepoDirectory)

        if os.path.exists(temporaryRepoDirectory):
            shutil.rmtree(temporaryRepoDirectory)

        new_metrics = self._get_state()
    
        new_state = [new_metrics[o] for o in self.observations]
        current_state = [current_metrics[o] for o in self.observations]
        reward = self._calc_reward(current_metrics, action, new_metrics)

        self.dump_step(new_state, current_state, action, reward)
        return new_state, reward

    def dump_step(self, new_state, current_state, action, reward):
        step_str = ",".join([str(self.episode_counter)] + [",".join(map(str, new_state))] + [",".join(map(str,current_state))] + [str(action), str(reward)])
        logging.info("step executed successfuly. Result:%s", step_str)
        with open("/tmp/state_dump_" + str(self.start_timestamp) + ".csv", 'a') as file:
          file.write(step_str + "\n")

    def get_current_state(self):
        state = self._get_state()
        return  [state[o] for o in self.observations]

    def _calc_reward(self, pre, action, post):
        assert(pre.keys() == post.keys())

        return self._reward_search_for_reuse(pre, post) + self._reward_bitmap_misses(pre, post) + self._reward_action(action)

    def _reward_search_for_reuse(self, pre, post):
        key = 'plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_'+self.sanitized_repo_name

        pre_bucket = self._search_for_reuse_bucket(pre[key])
        post_bucket = self._search_for_reuse_bucket(post[key])

        bucket_delta = pre_bucket - post_bucket

        # When bucket jump is negative or non-existent, no cookie
        reward = 0
        if bucket_delta == 1:
            # One bucket of improvement, small cookie
            reward = 0.5
        elif bucket_delta == 2:
            # Maximum improvement, large cookie
            reward = 1

        return reward * self._reward_weights[key]

    def _search_for_reuse_bucket(self, millis):
        # TODO: Make configurable or extract from jgit config
        millis_max = 60000*5
        cp1 = 1000
        cp2 = 60000

        bucket = 2
        if millis < cp1:
            bucket = 0
        elif millis < cp2:
            bucket = 1

        return bucket

    def _reward_bitmap_misses(self, pre, post):
        key = 'bitmap_index_misses_pct'

        # Default no cookie
        reward = 0
        if pre[key] < 0:
            # Had no bitmap and now have bitmap, cookie size proportional to
            # effectiveness of bitmap
            if post[key] >= 0:
                reward = 1-post[key]

        elif post[key] < 0:
            # Had bitmap, but lost it, therefore, no cookie
            # TODO: If actions include removal of bitmap, reconsider this
            reward = 0

        else:
            # Had bitmap, and still have bitmap
            delta = pre[key] - post[key]

            if delta < 0:
                # Things got worse, so no cookie
                reward = 0
            elif delta == 0:
                # No effective change, small cookie
                reward = 0.2
            else:
                # Things got better, large cookie (regardless of the magnitude of
                # the improvement)
                reward = 1

        return reward * self._reward_weights[key]

    def _reward_action(self, action):
        key = 'action'

        # TODO: Compute actual reward of action?

        return self._action_to_reward[action] * self._reward_weights[key]

    def _get_state(self):
        # #TODO ignore lines with -1 in all fields
        state_json = self.scraper.run()
        state = json.loads(state_json)

        # Mutates the state
        StateEnricher(state, self.sanitized_repo_name).hydrate()
        return state

    def __sanitize_repository_name(self, repository_name: str):
        return repository_name.replace("-", "_").replace("/", "_").lower()

