from gerrit_env import GerritEnv
import configparser
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(), 
                                                                                                      logging.FileHandler('/tmp/ghs-noaction-model.log', mode='a')])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="GHS schedule model")
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

    action_frequency = int(num_episodes / 20)

    state = str(env.get_current_state())
    # Q-learning algorithm
    for i in range(num_episodes):
            if i % (action_frequency * 2) == 0:
                action = 1
            elif i % action_frequency == 0:
                action = 2
            else:
                action = 0

            logging.info("executing action %s, episode %d", action, i)
            # Take action and observe reward and next state
            next_state,reward = env.step(action=action)
            logging.info("reward generated for action: %s, reward:%d",action,reward)

            # Move to next state
            state = str(next_state)
