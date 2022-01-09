#!/bin/bash

if [[ -z "${TZ}" ]]; then
  echo "Setting timezone to ${TZ}"
  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
fi

cd /chiadog

. ./venv/bin/activate

python3 main.py --config ${config_dir}
