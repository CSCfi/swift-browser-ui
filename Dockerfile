FROM python:3.7-alpine3.12 as BACKEND

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && rm -rf /var/cache/apk/*

COPY requirements.txt /root/swift_upload_runner/requirements.txt
COPY setup.py /root/swift_upload_runner/setup.py
COPY swift_upload_runner /root/swift_upload_runner/swift_upload_runner

RUN pip install --upgrade pip\
    && pip install -r /root/swift_upload_runner/requirements.txt \
    && pip install /root/swift_upload_runner

FROM python:3.7-alpine3.12

RUN apk add --no-cache --update bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/swift-upload-runner"

COPY --from=BACKEND /usr/local/lib/python3.7 /usr/local/lib/python3.7/

COPY --from=BACKEND /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BACKEND /usr/local/bin/swift-upload-runner /usr/local/bin

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

RUN adduser --disabled-password --no-create-home swiftrunner
USER swiftrunner

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
