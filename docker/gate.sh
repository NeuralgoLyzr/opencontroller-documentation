#!/bin/sh
# The documentation is held to the cell's sign-in and to its license. It is
# static pages, so it can check neither itself: every request asks the
# cell's API first. The files written here are nginx.conf's includes.
#
# With SESSION_API_URL (the chart sets it), the API is asked who the visitor
# is, with the cookies their browser sent (GET /v1/me). Signed in, the page
# is served. Not signed in, or signed in without access, they are sent to
# the console to sign in. A locked API answers 503, and the page says the
# cell is locked. An API that is down cannot say who anyone is, so nothing
# is served until it answers. A good answer is remembered for 30 seconds,
# so a page's files do not each ask, and a refusal for 5.
#
# With LICENSE_API_URL alone, only the license is asked (GET /auth/config):
# anyone who reaches the address reads the pages, a locked cell shows the
# locked page, and an API that is down does not stop the pages.
#
# With neither, as in local development, nothing is asked.
set -eu

locked() {
    cat <<'LOCKED'
error_page 403 =503 /_locked.html;
location = /_locked.html {
    internal;
    root /usr/share/nginx/locked;
    add_header Cache-Control "no-store" always;
}
location @oc_locked {
    return 403;
}
LOCKED
}

if [ -n "${SESSION_API_URL:-}" ]; then
    cat > /tmp/oc-gate-all.conf <<'GATE'
auth_request /_session;
GATE
    {
        locked
        cat <<SERVER
error_page 401 = @oc_sign_in;
location @oc_sign_in {
    add_header Cache-Control "no-store" always;
    return 302 /;
}
location = /_session {
    internal;
    proxy_pass ${SESSION_API_URL%/}/v1/me;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    # Only the browser's cookies say who it is: a credential in a header is
    # the console's to send, never a page's.
    proxy_set_header Authorization "";
    proxy_set_header X-API-Key "";
    proxy_connect_timeout 2s;
    proxy_read_timeout 3s;
    proxy_cache oc_session;
    proxy_cache_key "\$http_cookie";
    proxy_cache_valid 200 30s;
    proxy_cache_valid 401 403 5s;
    proxy_ignore_headers Set-Cookie Cache-Control Expires Vary;
    proxy_hide_header Set-Cookie;
    proxy_intercept_errors on;
    error_page 503 = @oc_locked;
    error_page 400 401 403 404 500 502 504 = @oc_signed_out;
}
location @oc_signed_out {
    return 401;
}
SERVER
    } > /tmp/oc-gate-server.conf
    exit 0
fi

[ -n "${LICENSE_API_URL:-}" ] || exit 0

cat > /tmp/oc-gate-pages.conf <<'GATE'
auth_request /_license;
GATE
{
    locked
    cat <<SERVER
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
location @oc_unknown {
    return 204;
}
SERVER
} > /tmp/oc-gate-server.conf
