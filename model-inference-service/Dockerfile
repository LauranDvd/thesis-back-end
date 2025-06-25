# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-slim-bullseye AS builder

WORKDIR /model-inference-service

#RUN apk update && apk add gcc musl-dev linux-headers

COPY model-inference-service/requirements.txt /model-inference-service
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

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
