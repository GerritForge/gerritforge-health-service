import torch
import numpy as np
from gerrit_env import GerritEnv

num_episodes = 1000

env = GerritEnv(gerritUrl="http://localhost:8080",
                prometheus_bearer_token="token",
                repositoryName="gerrit",
                gitRepositoryPath="/home/maczech/development/workspace/gerrit_testsite/git/gerrit.git", 
                actionsJarPath="/home/maczech/development/ghs/workspace/gerritforge-health-service/components/actions-executor/target/actions-executor-1.0-SNAPSHOT-jar-with-dependencies.jar")

state = tuple(env.get_current_state())
for i in range(num_episodes):
        action = 0 # Always do no-action

        print("Action")
        print(action)

        # Take action and observe reward and next state
        s,reward = env.step(action=action)
        print("Reward:")
        print(reward)

        print("Old state:")
        print(state)

        next_state = tuple(s)
        print("New state:")
        print(next_state)

        # Move to next state
        state = next_state
