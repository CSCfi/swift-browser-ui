FROM python:3.7-alpine3.9 as BACKEND

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && rm -rf /var/cache/apk/*

COPY requirements.txt /root/swift_request/requirements.txt
COPY setup.py /root/swift_request/setup.py
COPY swift_sharing_request /root/swift_request/swift_sharing_request

RUN pip install --upgrade pip\
    && pip install -r /root/swift_request/requirements.txt \
    && pip install /root/swift_request

FROM python:3.7-alpine3.9

RUN apk add --no-cache --update bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/swift-sharing-request"

COPY --from=BACKEND usr/local/lib/python3.7 usr/local/lib/python3.7/

COPY --from=BACKEND /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BACKEND /usr/local/bin/swift-sharing-request /usr/local/bin

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

RUN addgroup -g 1001 swiftrequest && \
    adduser -D -u 1001 --disabled-password --no-create-home -G swiftrequest swiftrequest

USER swiftrequest

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
