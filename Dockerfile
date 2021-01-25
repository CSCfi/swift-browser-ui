FROM python:3.8-alpine3.12 as BACKEND

RUN apk add --update \
    && apk add --no-cache build-base curl-dev linux-headers bash git\
    && apk add --no-cache libressl-dev libffi-dev\
    && rm -rf /var/cache/apk/*

COPY requirements.txt /root/swift_sharing/requirements.txt
COPY setup.py /root/swift_sharing/setup.py
COPY swift_x_account_sharing /root/swift_sharing/swift_x_account_sharing

RUN pip install --upgrade pip\
    && pip install -r /root/swift_sharing/requirements.txt \
    && pip install /root/swift_sharing

FROM python:3.8-alpine3.12

RUN apk add --no-cache --update bash

LABEL maintainer "CSC Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.vcs-url="https://github.com/CSCFI/swift-x-account-sharing"

COPY --from=BACKEND /usr/local/lib/python3.8 /usr/local/lib/python3.8/

COPY --from=BACKEND /usr/local/bin/gunicorn /usr/local/bin/

COPY --from=BACKEND /usr/local/bin/swift-x-account-sharing /usr/local/bin

RUN mkdir -p /app

WORKDIR /app

COPY ./deploy/app.sh /app/app.sh

RUN chmod +x /app/app.sh

RUN addgroup -g 1001 swiftsharing && \
    adduser -D -u 1001 --disabled-password --no-create-home -G swiftsharing swiftsharing

USER swiftsharing

ENTRYPOINT ["/bin/sh", "-c", "/app/app.sh"]
