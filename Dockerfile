FROM python:3.10-slim

LABEL org.opencontainers.image.source="https://github.com/martomi/chiadog"

ENV CHIADOG_CONFIG_DIR=/root/.chiadog/config.yaml
ENV TZ=UTC

WORKDIR /chiadog
COPY requirements.txt /chiadog
RUN python3 -m venv venv \
&& . ./venv/bin/activate \
&& pip3 install -r requirements.txt

COPY . /chiadog

ENTRYPOINT ["/chiadog/entrypoint.sh"]
