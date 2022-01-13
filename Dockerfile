FROM python:3.10-slim

ENV CHIADOG_CONFIG_DIR=/root/.chiadog/config.yaml
ENV TZ=UTC

COPY . /chiadog
WORKDIR /chiadog
RUN python3 -m venv venv \
&& . ./venv/bin/activate \
&& pip3 install -r requirements.txt

ENTRYPOINT ["/chiadog/entrypoint.sh"]
