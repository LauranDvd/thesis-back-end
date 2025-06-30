# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-slim-bullseye AS builder

WORKDIR /model-inference-service

#RUN apk update && apk add gcc musl-dev linux-headers

RUN apt update && apt -y install curl

RUN apt-get upgrade -y && \
    apt-get install -y git

COPY model-inference-service/requirements.txt /model-inference-service
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ADD https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh /tmp
RUN chmod +x /tmp/elan-init.sh && /tmp/elan-init.sh -y

ENV PATH="${PATH}:/root/.elan/bin"
# . is the shell equivalent for SOURCE; assuming HOME is root
# RUN lake

COPY model-inference-service/ /model-inference-service
COPY shared/ /shared

ENTRYPOINT ["python3"]
#CMD ["import sys"]
#CMD ["sys.path.append('../shared')"]

CMD ["worker.py"]

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
