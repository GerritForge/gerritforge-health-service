import gym
from gym import spaces
import numpy as np


# Actions definition
def create_bitmap(state):
    pass


def run_gc(state):
    pass


def do_nothing(state):
    pass


def build_ghs_obs_space(observations):
    lower_obs_bound = {
        'system_load': 0,
        'pack_files_count': 0,
        'bitmap_miss_count': -1,
    }
    higher_obs_bound = {
        'system_load': 100,
        'pack_files_count': + np.inf,
        'bitmap_miss_count': + np.inf,
    }

    low = np.array([lower_obs_bound[o] for o in observations])
    high = np.array([higher_obs_bound[o] for o in observations])
    shape = (len(observations),)
    # Define a 3D continuous space with ranges [0, 100], [0, inf], [-1, inf]
    # https://gymnasium.farama.org/api/spaces/fundamental/#box
    return gym.spaces.Box(low, high, shape)


class GHSEnv(gym.Env):

    def __init__(self):
        super(GHSEnv, self).__init__()

        self.log = None
        self.state = {}

        self.actions = [do_nothing, run_gc, create_bitmap]
        # https://gymnasium.farama.org/api/spaces/fundamental/#discrete
        self.action_space = gym.spaces.Discrete(len(self.actions))

        self.observations = ['system_load', 'pack_files_count', 'bitmap_miss_count']
        self.observation_space = build_ghs_obs_space(self.observations)

    def observation(self):
        return np.array([self.state[o] for o in self.observations])

    def step(self, action):
        reward = 0
        # Don't do anything if system load is high
        if self.state['system_load'] >= 80:
            do_nothing(self.state)
            return self.observation(), reward, False, False, {}

        # Do selected action
        self.actions[action](self.state)
        self.log += f'Chosen action: {self.actions[action].__name__}\n'

        # Need to calculate the reward here

        return self.observation(), reward, False, False, {}

    def reset(self):
        self.state = {
            'system_load': 0,
            'pack_files_count': 2,
            'bitmap_miss_count': 0
        }
        # Not sure if we need to consider run a GC when resetting the environment
        # run_gc(self.state)
        return np.array([self.state[o] for o in self.observations])

    def render(self, mode=None):
        print(self.log)
        self.log = ''
