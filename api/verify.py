"""
Vercel Serverless Function: /api/verify
Accepts POST request with JSON payload:
{
    "filename": "applicant.pdf",
    "file_base64": "..."
}
Returns JSON verification report with Risk Score, Red Flags, and Clean Signals.
"""
import json
import base64
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path to load src modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src import TenantGuardAnalyzer, ReportGenerator


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Enable CORS for pre-flight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Health check endpoint
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "status": "healthy",
            "service": "TenantGuard AI Forensic Audit Engine",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_error(400, "Empty request body.")
                return

            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            filename = payload.get("filename", "uploaded_document.pdf")
            file_base64 = payload.get("file_base64", "")

            if not file_base64:
                self._send_error(400, "Missing 'file_base64' in payload.")
                return

            # Strip data URL prefix if present (e.g. data:application/pdf;base64,...)
            if "," in file_base64:
                file_base64 = file_base64.split(",", 1)[1]

            file_bytes = base64.b64decode(file_base64)

            # Execute forensic analysis
            analyzer = TenantGuardAnalyzer()
            result = analyzer.analyze_bytes(file_bytes, filename=filename)

            report_dict = ReportGenerator.to_dict(result)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(report_dict, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self._send_error(500, f"Analysis failed: {str(e)}")

    def _send_error(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        err_payload = {"error": message, "code": code}
        self.wfile.write(json.dumps(err_payload).encode("utf-8"))
