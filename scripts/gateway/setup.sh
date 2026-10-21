#!/usr/bin/env sh
# Sets the gateway up for the docs assistant, and fills assistant.js in.
#
#   GATEWAY=https://gateway.example.com DOCS_ORIGIN=https://docs.example.com \
#   PROVIDER=anthropic MODEL=claude-haiku-5-5 scripts/gateway/setup.sh
#
# Optional: ADMIN_TOKEN (bearer for the management API), BUDGET (dollars per
# day, default 5), RPM (requests per minute, default 30).
#
# It creates, in order: the system prompt in the prompt repository; a
# browser virtual key allowed one provider and model, with the budget and
# rate limit; a policy on that key that refuses any call not carrying the
# prompt; a content rule on that key that blocks secrets in questions; and
# the CORS entries for the docs origin. Then it writes the gateway address,
# key, prompt id and model into assistant.js. The key value is never printed.
set -eu
: "${GATEWAY:?set GATEWAY}" "${DOCS_ORIGIN:?set DOCS_ORIGIN}" "${PROVIDER:?set PROVIDER}" "${MODEL:?set MODEL}"
BUDGET=${BUDGET:-5}; RPM=${RPM:-30}
AUTH=${ADMIN_TOKEN:+-H "Authorization: Bearer $ADMIN_TOKEN"}
here=$(cd "$(dirname "$0")/../.." && pwd)

api() { # method path [json]
  if [ $# -gt 2 ]; then
    curl -sS -f -X "$1" "$GATEWAY$2" $AUTH -H 'Content-Type: application/json' -d "$3"
  else
    curl -sS -f -X "$1" "$GATEWAY$2" $AUTH
  fi
}
field() { python3 -c 'import json,sys; d=json.load(sys.stdin)
for k in sys.argv[1].split("."):
    d=d[k] if isinstance(d,dict) else d[int(k)]
print(d)' "$1"; }
jsonstr() { python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'; }

api GET /api/providers | grep -q "\"name\":\"$PROVIDER\"" || { echo "the gateway has no provider named $PROVIDER; add it with its key first" >&2; exit 1; }

echo "1/5 the system prompt"
text=$(jsonstr < "$here/scripts/gateway/prompt.md")
prompt_id=$(api POST /api/prompt-repo/prompts '{"name":"docs-assistant"}' | field prompt.id 2>/dev/null \
  || api GET /api/prompt-repo/prompts | python3 -c 'import json,sys; d=json.load(sys.stdin); print([p["id"] for p in d.get("prompts",d) if p["name"]=="docs-assistant"][0])')
api POST "/api/prompt-repo/prompts/$prompt_id/versions" "{\"commit_message\":\"the docs assistant's rules\",\"messages\":[{\"role\":\"system\",\"content\":$text}],\"model_params\":{},\"provider\":\"$PROVIDER\",\"model\":\"$MODEL\"}" >/dev/null

echo "2/5 the browser key"
vk=$(api POST /api/governance/virtual-keys "{\"name\":\"docs-assistant\",\"description\":\"The docs site's Ask the docs panel. Public by design; bounded by its budget and rate limit.\",\"provider_configs\":[{\"provider\":\"$PROVIDER\",\"allowed_models\":[\"$MODEL\"]}],\"budgets\":[{\"max_limit\":$BUDGET,\"reset_duration\":\"1d\"}],\"rate_limit\":{\"request_max_limit\":$RPM,\"request_reset_duration\":\"1m\"},\"calendar_aligned\":true}")
vk_id=$(printf '%s' "$vk" | field virtual_key.id)
vk_value=$(printf '%s' "$vk" | field virtual_key.value)

echo "3/5 the policy: only calls that carry the prompt"
api POST /api/llm-policies "{\"name\":\"docs-assistant: prompt required\",\"action\":\"deny\",\"scope\":\"virtual_key\",\"scope_id\":\"$vk_id\",\"match\":{},\"cel\":\"headers[\\\"x-bf-prompt-id\\\"] != \\\"$prompt_id\\\"\",\"reason\":\"The docs assistant answers only with its own prompt.\",\"priority\":10}" >/dev/null

echo "4/5 the content rule: no secrets in questions"
api POST /api/guardrails "{\"name\":\"docs-assistant: no secrets\",\"scope\":\"virtual_key\",\"scope_id\":\"$vk_id\",\"stages\":[\"request\"],\"provider_type\":\"regex\",\"pattern\":\"(sk-[A-Za-z0-9_-]{16,}|cpk_[A-Za-z0-9_]+|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)\",\"action\":\"block\",\"on_error\":\"fail_closed\",\"priority\":10}" >/dev/null

echo "5/5 CORS for $DOCS_ORIGIN"
cfg=$(api GET /api/config)
printf '%s' "$cfg" | DOCS_ORIGIN="$DOCS_ORIGIN" python3 -c '
import json,os,sys
d=json.load(sys.stdin); c=d["client_config"]
origins=[o for o in (c.get("allowed_origins") or []) if o!="*"]
if os.environ["DOCS_ORIGIN"] not in origins: origins.append(os.environ["DOCS_ORIGIN"])
c["allowed_origins"]=origins
headers=c.get("allowed_headers") or ["Content-Type","Authorization","X-Requested-With","X-Api-Key"]
for h in ("x-bf-vk","x-bf-prompt-id"):
    if h not in headers: headers.append(h)
c["allowed_headers"]=headers
c["enforce_auth_on_inference"]=True
print(json.dumps({"client_config":c,"framework_config":d.get("framework_config",{}),"auth_config":d.get("auth_config")}))' > /tmp/oc-gateway-config.json
api PUT /api/config @/tmp/oc-gateway-config.json >/dev/null 2>&1 || curl -sS -f -X PUT "$GATEWAY/api/config" $AUTH -H 'Content-Type: application/json' --data-binary @/tmp/oc-gateway-config.json >/dev/null
rm -f /tmp/oc-gateway-config.json

echo "writing assistant.js"
VK="$vk_value" PID="$prompt_id" python3 - "$here/assistant.js" "$GATEWAY" "$PROVIDER/$MODEL" <<'PY'
import os,re,sys
p,gateway,model=sys.argv[1:]
s=open(p).read()
for k,v in (("gateway",gateway),("key",os.environ["VK"]),("promptId",os.environ["PID"]),("model",model)):
    s=re.sub(r'(\n  %s: )"[^"]*"' % k, r'\1"%s"' % v, s, count=1)
open(p,'w').write(s)
PY
echo "done: key $vk_id, prompt $prompt_id. The key value is in assistant.js only."
