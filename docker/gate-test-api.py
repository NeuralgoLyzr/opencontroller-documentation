"""A stand-in for the cell's API: /v1/me answers by the cookie, and counts the asks."""
import http.server, sys

asks = {"n": 0}

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/asks":
            body = str(asks["n"]).encode()
            self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        asks["n"] += 1
        cookie = self.headers.get("Cookie", "")
        leaked = self.headers.get("Authorization") or self.headers.get("X-API-Key")
        code = 401
        if self.path == "/auth/config":
            code = 503 if "s=locked" in cookie else 200
        elif leaked:
            code = 500  # a header credential must never arrive
        elif "s=good" in cookie:
            code = 200
        elif "s=denied" in cookie:
            code = 403
        elif "s=locked" in cookie:
            code = 503
        self.send_response(code); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self, *a): pass

http.server.ThreadingHTTPServer(("0.0.0.0", int(sys.argv[1])), H).serve_forever()
