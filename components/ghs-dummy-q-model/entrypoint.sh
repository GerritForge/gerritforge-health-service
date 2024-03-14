#!/bin/bash

cat config.ini.template | envsubst > config.ini
python3 ./main.py
