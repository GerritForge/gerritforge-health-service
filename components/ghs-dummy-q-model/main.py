import torch
import numpy as np
from gerrit_env import GerritEnv

# Q-learning parameters
learning_rate = 0.1
discount_factor = 0.9
epsilon = 0.1
num_episodes = 1000

# Initialize Q-table
Q = {}

env = GerritEnv(gerritUrl="http://localhost:8080",
                prometheus_bearer_token="token",
                repositoryName="gerrit",
                gitRepositoryPath="/home/maczech/development/workspace/gerrit_testsite/git/gerrit.git", 
                actionsJarPath="/home/maczech/development/ghs/workspace/gerritforge-health-service/components/actions-executor/target/actions-executor-1.0-SNAPSHOT-jar-with-dependencies.jar")

state = tuple(env.get_current_state())
# Q-learning algorithm
for i in range(num_episodes):
        # Initial state
        # Epsilon-greedy action selection
        if np.random.rand() < epsilon:
            action = np.random.randint(3)  # Two actions: 0 and 1
        else:
            if state not in Q:
                Q[state] = [0, 0]  # Initialize Q-values for the state
            action = np.argmax(Q[state])
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
        # Update Q-value using Q-learning update rule
        if next_state not in Q:
            Q[next_state] = [0, 0]  # Initialize Q-values for the next state
        max_next_Q = max(Q[next_state])
        Q[state][action] += learning_rate * (reward + discount_factor * max_next_Q - Q[state][action])

        # Move to next state
        state = next_state
