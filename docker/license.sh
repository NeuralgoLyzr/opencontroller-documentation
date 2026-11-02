#!/bin/sh
# The documentation is held to the cell's license. It is static pages, so it
# cannot check a signed license itself: with LICENSE_API_URL (the chart sets
# it), every page asks the cell's API first. A locked API answers 503, and the
# page says the cell is locked. An API that is down or restarting says nothing
# about the license, and the pages keep serving. Without LICENSE_API_URL, as
# in local development, nothing is asked. The files are nginx.conf's includes.
set -eu
[ -n "${LICENSE_API_URL:-}" ] || exit 0

cat > /tmp/oc-license-gate.conf <<'GATE'
auth_request /_license;
GATE

cat > /tmp/oc-license-server.conf <<SERVER
error_page 403 =503 /_locked.html;
location = /_locked.html {
    internal;
    root /usr/share/nginx/locked;
    add_header Cache-Control "no-store" always;
}
location = /_license {
    internal;
    proxy_pass ${LICENSE_API_URL%/}/auth/config;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_connect_timeout 2s;
    proxy_read_timeout 3s;
    proxy_intercept_errors on;
    error_page 503 = @oc_locked;
    error_page 400 401 403 404 500 502 504 = @oc_unknown;
}
location @oc_locked {
    return 403;
}
location @oc_unknown {
    return 204;
}
SERVER
