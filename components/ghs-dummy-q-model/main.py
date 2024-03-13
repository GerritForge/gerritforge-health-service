import torch
import numpy as np
from gerrit_env import GerritEnv
import argparse
import configparser


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GHS model")
    parser.add_argument(
        "--mode",
        required=False,
        default="Exploration"
    )
    parser.add_argument(
        "--config",
        required=False,
        default="config.ini"
    )
    
    args = parser.parse_args()
    mode = args.mode
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(args.config)

    # Q-learning parameters
    learning_rate = float(config[mode]["learning_rate"])
    discount_factor = float(config[mode]["discount_factor"])
    epsilon = float(config[mode]["epsilon"])
    num_episodes = int(config[mode]["num_episodes"])

    # Initialize Q-table
    Q = {}

    env = GerritEnv(gerritUrl=config["General"]["gerrit_url"],
                    prometheus_bearer_token=config["General"]["prometheus_bearer_token"],
                    repositoryName=config["General"]["repository_name"],
                    gitRepositoryPath=config["General"]["git_repository_path"], 
                    actionsJarPath=config["General"]["actions_jar_path"])

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
