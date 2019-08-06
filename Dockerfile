FROM python:3.7-alpine3.9 as BUILD

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && rm -rf /var/cache/apk/*

COPY requirements.txt /root/swift_ui/requirements.txt
COPY setup.py /root/swift_ui/setup.py
COPY swift_browser_ui /root/swift_ui/swift_browser_ui
COPY swift_browser_ui_frontend /root/swift_ui/swift_browser_ui_frontend

RUN pip install --upgrade pip && \
    pip install -r /root/swift_ui/requirements.txt && \
    pip install /root/swift_ui

FROM python:3.7-alpine3.9

RUN apk add --no-cache --update bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/swift-browser-ui"

COPY --from=BUILD usr/local/lib/python3.7/ usr/local/lib/python3.7/

COPY --from=BUILD /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BUILD /usr/local/bin/swift-browser-ui /usr/local/bin/

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
