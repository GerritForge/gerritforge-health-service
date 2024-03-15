import numpy as np
from gerrit_env import GerritEnv
import argparse
import configparser
import json
import sys
import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), 
                                                                                                      logging.FileHandler('/tmp/ghs-q-model.log', mode='a')])


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

    # Q status function file
    q_status_file = config["General"]["q_output_dir"] + "/q_status_" + str(datetime.datetime.now().timestamp()) + ".json"

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
                    actionsJarPath=config["General"]["actions_jar_path"],
                    username=config["General"]["username"],
                    password=config["General"]["password"]
                    )

    state = str(env.get_current_state())
    # Q-learning algorithm
    while True:
            # Initial state
            # Epsilon-greedy action selection
            if state not in Q:
                    Q[state] = [0, 0, 0]  # Initialize Q-values for the state
            if np.random.rand() < epsilon:
                action = np.random.randint(3)  # Two actions: 0 and 1
            else:
                action = np.argmax(Q[state])
            logging.info("action taken by model: %s",action)
            # Take action and observe reward and next state
            s,reward = env.step(action=action)
            next_state = str(s)
            logging.info("reward generated for action: %s, reward:%s",action,reward)
            # Update Q-value using Q-learning update rule
            if next_state not in Q:
                Q[next_state] = [0, 0, 0]  # Initialize Q-values for the next state
            max_next_Q = max(Q[next_state])
            Q[state][action] += learning_rate * (reward + discount_factor * max_next_Q - Q[state][action])

            # Move to next state
            state = next_state
            Q_string = json.dumps(Q)
            with open(q_status_file, 'w') as file:
                file.write(Q_string)
    