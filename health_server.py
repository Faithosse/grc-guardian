"""
GRC Guardian - Health Check Endpoint
For Antigravity deployment verification
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "agent": "grc-guardian",
                "version": "1.0.0",
                "agents": ["orchestrator", "compliance", "risk", "audit"],
                "mcp_servers": ["grc-mcp-server"],
                "skills": ["check-compliance", "assess-risk", "run-audit", "full-assessment", "interactive-mode"]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_health_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    run_health_server(port)