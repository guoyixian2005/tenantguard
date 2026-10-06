"""
Vercel Serverless Function: /api/checkout
Creates a Stripe Checkout Session for TenantGuard AI plans:
- single: $9.99 (Single verification scan)
- pack3: $19.99 (Applicant 3-Pack)
- pro: $29.00/month (Pro Landlord Monthly)

Zero external dependencies (uses standard library urllib).
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Stripe API Keys
# Read securely from Vercel Environment Variables
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
DOMAIN_HOST = os.environ.get("DOMAIN_HOST", "https://www.comilla.world")



class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Support both GET /api/checkout?plan=single and POST
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        plan = params.get("plan", ["single"])[0]
        self._create_checkout_session(plan)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                plan = payload.get("plan", "single")
            else:
                plan = "single"
            self._create_checkout_session(plan)
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _create_checkout_session(self, plan: str):
        try:
            success_url = f"{DOMAIN_HOST}/?status=success&session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{DOMAIN_HOST}/#pricing"

            if plan == "pack3":
                post_fields = {
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "mode": "payment",
                    "payment_method_types[0]": "card",
                    "line_items[0][price_data][currency]": "usd",
                    "line_items[0][price_data][unit_amount]": "1999",  # $19.99
                    "line_items[0][price_data][product_data][name]": "TenantGuard AI — Applicant 3-Pack",
                    "line_items[0][price_data][product_data][description]": "3 complete document audits. Compare top applicants side-by-side. Credits never expire.",
                    "line_items[0][quantity]": "1",
                }
            elif plan == "pro":
                post_fields = {
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "mode": "subscription",
                    "payment_method_types[0]": "card",
                    "line_items[0][price_data][currency]": "usd",
                    "line_items[0][price_data][unit_amount]": "2900",  # $29.00
                    "line_items[0][price_data][recurring][interval]": "month",
                    "line_items[0][price_data][product_data][name]": "TenantGuard AI — Pro Landlord Monthly",
                    "line_items[0][price_data][product_data][description]": "5 audits included each month + priority support.",
                    "line_items[0][quantity]": "1",
                }
            else:  # Default: single
                post_fields = {
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "mode": "payment",
                    "payment_method_types[0]": "card",
                    "line_items[0][price_data][currency]": "usd",
                    "line_items[0][price_data][unit_amount]": "999",  # $9.99
                    "line_items[0][price_data][product_data][name]": "TenantGuard AI — Single Verification Scan",
                    "line_items[0][price_data][product_data][description]": "Full forensic document audit, FICA tax recalculation, and official landlord report.",
                    "line_items[0][quantity]": "1",
                }

            encoded_data = urllib.parse.urlencode(post_fields).encode("utf-8")
            auth_str = base64.b64encode(f"{STRIPE_SECRET_KEY}:".encode("utf-8")).decode("utf-8")

            req = urllib.request.Request(
                "https://api.stripe.com/v1/checkout/sessions",
                data=encoded_data,
                headers={
                    "Authorization": f"Basic {auth_str}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                method="POST"
            )

            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read().decode("utf-8")
                stripe_res = json.loads(resp_body)
                checkout_url = stripe_res.get("url")
                session_id = stripe_res.get("id")

                self._send_json(200, {
                    "url": checkout_url,
                    "session_id": session_id,
                    "plan": plan
                })

        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = err_body
            self._send_json(http_err.code, {"error": f"Stripe API error: {err_msg}"})
        except Exception as e:
            self._send_json(500, {"error": f"Internal server error: {str(e)}"})

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
