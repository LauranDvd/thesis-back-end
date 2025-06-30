# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-slim-bullseye AS builder

WORKDIR /app-service

# RUN apk update && apk add gcc musl-dev linux-headers && apk --no-cache add curl
RUN apt update && apt -y install curl

RUN apt-get upgrade -y && \
    apt-get install -y git

COPY app-service/requirements.txt /app-service
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ADD https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh /tmp
RUN chmod +x /tmp/elan-init.sh && /tmp/elan-init.sh -y

ENV PATH="${PATH}:/root/.elan/bin"

COPY app-service/ /app-service
COPY shared/ /shared

EXPOSE 5000

ENTRYPOINT ["python3"]
#CMD ["import sys"]
#CMD ["sys.path.append('../shared')"]

CMD ["app.py"]

FROM builder as dev-envs

#RUN <<EOF
#apk update
#apk add git
#EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

COPY --from=gloursdocker/docker / /
