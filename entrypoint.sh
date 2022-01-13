#!/bin/sh

cd /chiadog
. ./venv/bin/activate
python main.py --config ${CHIADOG_CONFIG_DIR}
