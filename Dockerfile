# syntax=docker/dockerfile:1
# The documentation as a container: the site exported by Mintlify's CLI
# (pre-rendered pages, nothing of Mintlify's at runtime), served by
# unprivileged nginx with the rules the export asks for (docker/nginx.conf).
# A cell runs it beside the console where the internet is not at hand, and
# the console's Documentation button opens it.

FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS export
WORKDIR /site
# Pinned with the preview's and CI's (README).
RUN npm i -g mint@4.2.1084
COPY . .
# The export reaches Mintlify to render, so the build needs the network;
# the result does not.
RUN mint export --output /tmp/docs.zip && mkdir /out && unzip -q /tmp/docs.zip -d /out \
    && rm -f /out/serve.js "/out/Start Docs.command" "/out/Start Docs.bat"

FROM nginxinc/nginx-unprivileged:1.30-alpine@sha256:56b8272e43a0525f67aed68d1e0794a712d10e3e45a563e118e9a77c817e6f86
LABEL org.opencontainers.image.title="opencontroller-documentation" \
      org.opencontainers.image.source="https://github.com/NeuralgoLyzr/opencontroller-documentation"
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=export /out /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 CMD wget -qO /dev/null http://127.0.0.1:8080/ || exit 1
