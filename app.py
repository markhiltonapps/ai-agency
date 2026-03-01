#!/usr/bin/env python3
"""
Lightweight HTTP server for AI Agency Dashboard
Uses only stdlib (no external dependencies)
"""

import json
import threading
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging
import sys
import os

# Add current dir to path for imports
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/projects/ai-agency')

from research_agent import ResearchAgent
from outreach_agent import OutreachAgent
from design_agent import DesignAgent
from payment_agent import PaymentAgent
from success_agent import SuccessAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize agents
research = ResearchAgent()

with open("/home/ubuntu/.openclaw/workspace/secrets/instantly_api_key.txt") as f:
    instantly_key = f.read().strip()
outreach = OutreachAgent(instantly_key)

design = DesignAgent(
    netlify_token="nfp_T5q16R9XEYjBgroitvjyEY9SZKbKPXXA4d4e",
    site_id="5255436b-dcfd-485b-88f9-03b121d85504"
)

with open("/home/ubuntu/.openclaw/workspace/secrets/stripe_keys.json") as f:
    stripe_keys = json.load(f)
payment = PaymentAgent(
    stripe_secret_key=stripe_keys['secret_key_test'],
    webhook_signing_secret=stripe_keys['webhook_signing_secret']
)

success = SuccessAgent()

leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard API"""
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        query_string = urlparse(self.path).query
        
        try:
            # CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Route handlers
            if path == '/api/leads':
                status = parse_qs(query_string).get('status', [None])[0]
                self._get_leads(status)
            
            elif path.startswith('/api/leads/'):
                lead_id = path.split('/')[-1]
                self._get_lead(lead_id)
            
            elif path == '/api/funnel/stats':
                self._get_stats()
            
            elif path == '/api/health':
                self._health_check()
            
            elif path == '/':
                self._serve_frontend()
            
            else:
                self.send_error(404)
        
        except Exception as e:
            logger.error(f"GET error: {str(e)}")
            self.send_error(500)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Route handlers
            if path == '/api/leads':
                self._create_lead(body)
            
            elif path.startswith('/api/actions/send-cold-email/'):
                lead_id = path.split('/')[-1]
                self._send_cold_email(lead_id)
            
            elif path.startswith('/api/actions/check-replies/'):
                lead_id = path.split('/')[-1]
                self._check_replies(lead_id)
            
            elif path.startswith('/api/actions/blur-preview/'):
                lead_id = path.split('/')[-1]
                self._blur_preview(lead_id)
            
            elif path.startswith('/api/actions/generate-design/'):
                lead_id = path.split('/')[-1]
                self._generate_design(lead_id)
            
            elif path.startswith('/api/actions/create-invoice/'):
                lead_id = path.split('/')[-1]
                query_string = urlparse(self.path).query
                amount = parse_qs(query_string).get('amount', ['50000'])[0]
                self._create_invoice(lead_id, int(amount))
            
            elif path.startswith('/api/actions/start-project/'):
                lead_id = path.split('/')[-1]
                self._start_project(lead_id)
            
            else:
                self.send_error(404)
        
        except Exception as e:
            logger.error(f"POST error: {str(e)}")
            self._json_response({"error": str(e)})
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PATCH')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_PATCH(self):
        """Handle PATCH requests"""
        path = urlparse(self.path).path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if path.startswith('/api/leads/'):
                lead_id = path.split('/')[-1]
                self._update_lead(lead_id, body)
        
        except Exception as e:
            logger.error(f"PATCH error: {str(e)}")
            self._json_response({"error": str(e)})
    
    def _json_response(self, data):
        """Send JSON response"""
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _serve_frontend(self):
        """Serve HTML frontend"""
        try:
            frontend_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/frontend.html")
            with open(frontend_file, 'r') as f:
                html = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_error(500)
    
    def _get_leads(self, status=None):
        """Get all leads"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            leads = data.get('leads', [])
            if status:
                leads = [l for l in leads if l['status'] == status]
            
            self._json_response({
                "status": "success",
                "total": len(leads),
                "leads": leads
            })
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _get_lead(self, lead_id):
        """Get single lead"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            for lead in data.get('leads', []):
                if lead['id'] == lead_id:
                    self._json_response({"status": "success", "lead": lead})
                    return
            
            self._json_response({"error": "Lead not found"})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _get_stats(self):
        """Get funnel stats"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            leads = data.get('leads', [])
            
            stats = {
                'total_leads': len(leads),
                'by_status': {},
                'conversion_rates': {}
            }
            
            for status in ['found', 'cold_sent', 'replied', 'design_ready', 'invoice_sent', 'paid', 'design_in_progress', 'design_delivered']:
                count = len([l for l in leads if l['status'] == status])
                stats['by_status'][status] = count
            
            if stats['total_leads'] > 0:
                cold_sent = max(stats['by_status'].get('cold_sent', 1), 1)
                replied = max(stats['by_status'].get('replied', 1), 1)
                
                stats['conversion_rates'] = {
                    'cold_to_replied': f"{(stats['by_status'].get('replied', 0) / cold_sent * 100):.1f}%",
                    'replied_to_paid': f"{(stats['by_status'].get('paid', 0) / replied * 100):.1f}%",
                    'overall': f"{(stats['by_status'].get('paid', 0) / stats['total_leads'] * 100):.1f}%"
                }
            
            self._json_response({"status": "success", "stats": stats})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _health_check(self):
        """Health check"""
        self._json_response({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
    
    def _create_lead(self, body):
        """Create new lead"""
        try:
            lead_data = json.loads(body)
            result = research.add_manual_lead(lead_data)
            self._json_response(result)
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _update_lead(self, lead_id, body):
        """Update lead"""
        try:
            updates = json.loads(body)
            
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            found = False
            for lead in data.get('leads', []):
                if lead['id'] == lead_id:
                    for key, value in updates.items():
                        if value:
                            lead[key] = value
                    found = True
                    break
            
            if not found:
                self._json_response({"error": "Lead not found"})
                return
            
            with open(leads_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self._json_response({"status": "success"})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _send_cold_email(self, lead_id):
        """Send cold email"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                self._json_response({"error": "Lead not found"})
                return
            
            # Send in background thread
            def send():
                result = outreach.send_cold_email(lead)
                logger.info(f"Email sent to {lead['contact_email']}: {result}")
            
            threading.Thread(target=send, daemon=True).start()
            
            self._json_response({"status": "queued", "message": "Cold email queued for sending"})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _check_replies(self, lead_id):
        """Check for email replies"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                self._json_response({"error": "Lead not found"})
                return
            
            result = outreach.check_replies(lead_id, lead.get('campaign_id', lead_id))
            self._json_response(result)
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _blur_preview(self, lead_id):
        """Generate blur preview"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                self._json_response({"error": "Lead not found"})
                return
            
            def generate():
                import asyncio
                try:
                    asyncio.run(design.blur_preview(lead['website_url'], lead_id))
                except:
                    logger.warning("Design preview may not have generated (Playwright not available in test)")
            
            threading.Thread(target=generate, daemon=True).start()
            
            self._json_response({"status": "queued", "message": "Blur preview generating..."})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _generate_design(self, lead_id):
        """Generate full design"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                self._json_response({"error": "Lead not found"})
                return
            
            def generate():
                result = design.generate_full_design(lead)
                logger.info(f"Design generated for {lead['business_name']}: {result}")
            
            threading.Thread(target=generate, daemon=True).start()
            
            self._json_response({"status": "queued", "message": "Design generation started..."})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _create_invoice(self, lead_id, amount):
        """Create invoice"""
        try:
            with open(leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                self._json_response({"error": "Lead not found"})
                return
            
            result = payment.create_invoice(lead, amount=amount)
            self._json_response(result)
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def _start_project(self, lead_id):
        """Start design project"""
        try:
            result = success.start_project(lead_id)
            self._json_response(result)
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=5000):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    logger.info(f"🚀 Dashboard running at http://localhost:{port}")
    logger.info(f"API endpoint: http://localhost:{port}/api")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    import os
    port = int(os.getenv('PORT', 5000))
    run_server(port)
