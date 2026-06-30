import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get("PORT", 8000))
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

class CortexHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def end_headers(self):
        super().end_headers()

    def log_message(self, format, *args):
        sys.stdout.write(f"[CORTEX Python Server] {self.address_string()} - {format%args}\n")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CortexHTTPRequestHandler) as httpd:
        print(f"[CORTEX] Python Sovereign Kernel Server running on http://localhost:{PORT}")
        print(f"[CORTEX] Anergy level minimal. Reality: C5-REAL")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[CORTEX] Server terminated by operator.")
