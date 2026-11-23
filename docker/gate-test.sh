#!/bin/sh
# Tries the built image's gate (gate.sh) against a stand-in for the cell's API
# (gate-test-api.py, which answers by the cookie): who reads the pages with
# the sign-in asked, with the license alone, and with neither.
#
#   sh docker/gate-test.sh <image>
set -eu
image=${1:?the image to try}
here=$(cd "$(dirname "$0")" && pwd)
net=oc-gate-test-$$
api=oc-gate-test-api-$$
web=oc-gate-test-web-$$
port=${GATE_TEST_PORT:-18089}
site=http://127.0.0.1:$port
failed=0

cleanup() {
    docker rm -f "$api" "$web" >/dev/null 2>&1 || true
    docker network rm "$net" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker network create "$net" >/dev/null
docker run -d --name "$api" --network "$net" -v "$here/gate-test-api.py:/api.py:ro" python:3.12-alpine python /api.py 9000 >/dev/null

# serve starts the image with the environment given, and waits for it.
serve() {
    docker rm -f "$web" >/dev/null 2>&1 || true
    docker run -d --name "$web" --network "$net" -p "$port:8080" "$@" "$image" >/dev/null
    for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
        if curl -s -o /dev/null -m 2 "$site/healthz"; then return 0; fi
        sleep 1
    done
    echo "the image did not start" >&2
    docker logs "$web" >&2
    exit 1
}

# expect <what> <status and location> <curl arguments>
expect() {
    what=$1 want=$2
    shift 2
    got=$(curl -s -o /dev/null -m 8 -w '%{http_code} %{redirect_url}' "$@" | sed 's/ $//')
    if [ "$got" = "$want" ]; then
        echo "ok    $what"
    else
        echo "FAIL  $what: got '$got', want '$want'"
        failed=1
    fi
}

asks() { docker exec "$api" wget -qO- http://127.0.0.1:9000/asks; }

page=$site/docs/
asset=$(docker run --rm --entrypoint sh "$image" -c 'cd /usr/share/nginx/html && find docs/_mintlify -type f -name "*.js" | head -1')
[ -n "$asset" ] || { echo "the image has no script to ask for" >&2; exit 1; }
asset=$site/$asset
home="$site/"

echo "The sign-in asked"
serve -e SESSION_API_URL="http://$api:9000"
expect "probes are answered without it"           "200"       "$site/healthz"
expect "a page, not signed in, goes to sign in"   "302 $home" "$page"
expect "a script, not signed in, goes to sign in" "302 $home" "$asset"
expect "a page, signed in"                        "200"       -b s=good "$page"
expect "a script, signed in"                      "200"       -b s=good "$asset"
expect "a page, signed in without access"         "302 $home" -b s=denied "$page"
expect "a page, the cell locked"                  "503"       -b s=locked "$page"
expect "a credential in a header is not a sign-in" "302 $home" -H "Authorization: Bearer x" "$page"
expect "nor carried to the API beside a cookie"   "200"       -b s=good -H "X-API-Key: x" "$page"
before=$(asks)
for _ in 1 2 3 4 5; do curl -s -o /dev/null -b s=good "$page"; done
if [ "$(asks)" = "$before" ]; then echo "ok    a sign-in is remembered, not asked again"; else echo "FAIL  a remembered sign-in was asked again"; failed=1; fi
docker stop "$api" >/dev/null
expect "the API down, nobody is let in"           "302 $home" -b s=unseen "$page"
docker start "$api" >/dev/null

echo "The license alone"
serve -e LICENSE_API_URL="http://$api:9000"
expect "a page, not signed in"                    "200"       "$page"
expect "a script, not signed in"                  "200"       "$asset"
expect "a page, the cell locked"                  "503"       -b s=locked "$page"
docker stop "$api" >/dev/null
expect "the API down, the pages stay"             "200"       "$page"
docker start "$api" >/dev/null

echo "Neither"
serve
expect "a page"                                   "200"       "$page"

exit "$failed"
