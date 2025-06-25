# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.12-alpine AS builder

WORKDIR /app-service

RUN apk update && apk add gcc musl-dev linux-headers

COPY app-service/requirements.txt /app-service
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY app-service/ /app-service
COPY shared/ /shared

EXPOSE 5000

ENTRYPOINT ["python3"]
#CMD ["import sys"]
#CMD ["sys.path.append('../shared')"]

CMD ["app.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

COPY --from=gloursdocker/docker / /
