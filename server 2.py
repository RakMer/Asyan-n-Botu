import json
import os
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_NAME = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
APP_TITLE = os.environ.get("OPENROUTER_APP_TITLE", "Kardesime Ozel Bot")
APP_URL = os.environ.get("OPENROUTER_APP_URL", "http://localhost:8000")


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow the front-end to call the proxy from the browser.
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        try:
            if self.path != "/api/chat":
                self.send_error(404, "Not Found")
                return

            if not API_KEY:
                self._send_error_json(500, "Missing OPENROUTER_API_KEY")
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length else b""
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_error_json(400, "Invalid JSON")
                return

            if "model" not in payload:
                payload["model"] = MODEL_NAME

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": APP_URL,
                "X-Title": APP_TITLE,
            }

            req = Request(
                OPENROUTER_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )

            try:
                with urlopen(req) as resp:
                    body = resp.read()
                    status = resp.getcode()
                    self._send_raw_json(status, body)
            except HTTPError as exc:
                body = exc.read()
                payload = self._safe_json(body)
                if isinstance(payload, dict):
                    self._send_json(exc.code, payload)
                else:
                    self._send_error_json(exc.code, f"Upstream HTTP {exc.code}")
            except URLError as exc:
                self._send_error_json(502, f"Upstream connection error: {exc}")
        except Exception as exc:
            traceback.print_exc()
            self._send_error_json(500, f"Proxy error: {exc}")

    def _send_raw_json(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _send_error_json(self, status, message):
        self._send_json(status, {"error": {"message": message}})

    def _safe_json(self, body):
        if not body:
            return None
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None


def run():
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
