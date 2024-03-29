FROM openjdk:11

RUN apt-get update && \
    apt-get install -y python3-pip gettext-base && \
    apt-get clean

# Set the working directory inside the container
WORKDIR /usr/src/ghs-q-model

# Copy the necessary files into the container
COPY ghs-dummy-q-model/main.py ghs-dummy-q-model/entrypoint.sh ghs-dummy-q-model/config.ini.template ghs-dummy-q-model/requirements.txt ./

# Copy directories
COPY gym-gerrit gym-gerrit
COPY consumers/prometheus prometheus
COPY actions-executor/target/actions-executor-1.0-SNAPSHOT-jar-with-dependencies.jar ./actions-executor.jar


# Install virtualenv
RUN python3 -m pip install virtualenv

# Create and activate virtual environment
RUN virtualenv -p python3 venv
RUN /bin/bash -c "source venv/bin/activate"

# Install dependencies
RUN pip install -e prometheus
RUN pip install -e gym-gerrit
RUN pip install -r requirements.txt

RUN useradd -u 1000 -ms /bin/bash gerrit

RUN chown -R gerrit.gerrit .

USER gerrit

ENTRYPOINT [ "./entrypoint.sh" ]
