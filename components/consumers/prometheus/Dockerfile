FROM python:3

WORKDIR /usr/src/scraper

COPY scrape.py scraper.py requirements.txt ./
RUN touch /tmp/metrics.csv && python -m pip install virtualenv
RUN virtualenv -p python3 ghs-prometheus-consumer
RUN . ghs-prometheus-consumer/bin/activate
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "./scrape.py" ]
