from gerrit_env import GerritEnv

if __name__ == "__main__":
    env = GerritEnv(gerritUrl="http://localhost:8080",
                    prometheus_bearer_token="token",
                    repositoryName="ghs-test",
                    gitRepositoryPath="/Users/syntonyze/ginstall/gerrit-3.9/git/ghs-test.git",
                    actionsJarPath="/Users/syntonyze/dev/source/gerritforge-health-service/components/actions-executor/target/actions-executor-1.0-SNAPSHOT-jar-with-dependencies.jar")

    env.step(0)