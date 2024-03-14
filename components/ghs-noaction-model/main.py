import numpy as np
from gerrit_env import GerritEnv
import configparser
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), 
                                                                                                      logging.FileHandler('/tmp/ghs-noaction-model.log', mode='a')])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GHS no action model")
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
    config = configparser.ConfigParser()
    # Read the configuration file
    config.read(args.config)

    env = GerritEnv(gerritUrl=config["General"]["gerrit_url"],
                    prometheus_bearer_token=config["General"]["prometheus_bearer_token"],
                    repositoryName=config["General"]["repository_name"],
                    gitRepositoryPath=config["General"]["git_repository_path"], 
                    actionsJarPath=config["General"]["actions_jar_path"])
       
    num_episodes = int(config[args.mode]["num_episodes"])

    state = str(env.get_current_state())
    for i in range(num_episodes):
        action = 0 # Always do no-action

        logging.info("executing action %s, episonde %d", action, i)
        # Take action and observe reward and next state
        s,reward = env.step(action=action)
        next_state = str(s)
        logging.info("reward generated for action: %s, reward:%d",action,reward)

        # Move to next state
        state = next_state
