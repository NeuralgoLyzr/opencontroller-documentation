# syntax=docker/dockerfile:1
# The documentation as a container: the site exported by Mintlify's CLI
# (pre-rendered pages, nothing of Mintlify's at runtime), served by nginx as
# an unprivileged user with the rules the export asks for (docker/nginx.conf).
# A cell runs it beside the console where the internet is not at hand, and
# the console's sidebar links to it.

FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS export
WORKDIR /site
# Pinned with the preview's and CI's (README).
RUN npm i -g mint@4.2.1184
COPY . .
# Installing OpenController is for the hosted site alone: a cell's copy drops self-host/ and its tab.
RUN rm -rf self-host && node -e 'const fs = require("fs"); const d = JSON.parse(fs.readFileSync("docs.json", "utf8")); \
      for (const v of d.navigation.versions) v.tabs = v.tabs.filter((t) => t.tab !== "Self-host"); \
      fs.writeFileSync("docs.json", JSON.stringify(d, null, 2) + "\n")'
# The export reaches Mintlify to render, so the build needs the network;
# the result does not.
RUN mint export --base-path /docs --output /tmp/docs.zip && mkdir /out && unzip -q /tmp/docs.zip -d /out \
    && rm -rf /out/serve.js "/out/Start Docs.command" "/out/Start Docs.bat" /out/docker
# Each page as Markdown, for the page menu's Copy page and View as Markdown.
RUN sh docker/markdown.sh /site /out
# A cell serves the site under /docs on the console's own address: --base-path
# moves the site's links, and these are the two it does not. style.css names its
# font from the root, and the sidebar's "Open the console" is the console here.
RUN find /out -type f \( -name '*.html' -o -name '*.css' \) -exec sed -i \
      -e 's#"/fonts/JetBrainsMono#"/docs/fonts/JetBrainsMono#g' \
      -e 's#https://preview\.opencontroller\.sh#/#g' {} +
# The site runs where nothing else can be reached: a page that names a font
# elsewhere, or our own console, fails the build, rather than a customer's browser.
RUN elsewhere=$(find /out -type f \( -name '*.html' -o -name '*.txt' -o -name '*.css' \) -exec grep -lE '"/fonts/|https?://(fonts\.(googleapis|gstatic)\.com|preview\.opencontroller\.sh)' {} +); \
    if [ -n "$elsewhere" ]; then echo "addresses elsewhere in:" $elsewhere >&2; exit 1; fi

# nginx 1.30.8 fixes the HTTP/2, HTTP/3, resolver and mail-proxy flaws
# disclosed on 2026-11-18 (CVE-2026-123007, CVE-2026-123633 and others).
# The unprivileged image has no build of it yet, so the official one is
# made unprivileged here as that image does it: no user directive, the
# pid and temp files under /tmp, its config writable by the nginx user
# (uid 101) for the start-up scripts, and that uid to run as.
FROM nginx:1.30.8-alpine@sha256:8eb04fe3b385090e9aa02961f77398ad09b6bf33ab07f6669a5bb7acce22c0d3
RUN sed -i -e '/^user /d' -e 's,^pid .*,pid /tmp/nginx.pid;,' /etc/nginx/nginx.conf \
    && printf '%s\n' 'client_body_temp_path /tmp/client_temp;' 'proxy_temp_path /tmp/proxy_temp;' \
         'fastcgi_temp_path /tmp/fastcgi_temp;' 'uwsgi_temp_path /tmp/uwsgi_temp;' 'scgi_temp_path /tmp/scgi_temp;' \
         > /etc/nginx/conf.d/00-unprivileged.conf \
    && chown -R 101:0 /var/cache/nginx /etc/nginx \
    && chmod -R g+w /var/cache/nginx /etc/nginx
USER 101
LABEL org.opencontainers.image.title="opencontroller-documentation" \
      org.opencontainers.image.source="https://github.com/NeuralgoLyzr/opencontroller-documentation"
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/gate.sh /docker-entrypoint.d/40-gate.sh
COPY docker/locked.html /usr/share/nginx/locked/_locked.html
COPY --from=export /out /usr/share/nginx/html/docs
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 CMD wget -qO /dev/null http://127.0.0.1:8080/healthz || exit 1
