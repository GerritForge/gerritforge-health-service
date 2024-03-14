from gerrit_env import GerritEnv

# Parameters
num_episodes = 1000
action_frequency = int(num_episodes / 20)

env = GerritEnv(gerritUrl="http://localhost:8080",
                prometheus_bearer_token="token",
                repositoryName="gerrit",
                gitRepositoryPath="/home/maczech/development/workspace/gerrit_testsite/git/gerrit.git", 
                actionsJarPath="/home/maczech/development/ghs/workspace/gerritforge-health-service/components/actions-executor/target/actions-executor-1.0-SNAPSHOT-jar-with-dependencies.jar")

state = tuple(env.get_current_state())
# Q-learning algorithm
for i in range(num_episodes):
        if i % (action_frequency * 2) == 0:
            action = 1
        elif i % action_frequency == 0:
            action = 2
        else:
            action = 0

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
