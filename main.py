#!/usr/bin/env python3
"""
AI Agency Dashboard - Ready for Replit
Just paste this entire project into Replit and press Run
"""

import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Leads database (embedded for Replit)
LEADS_DATA = {
    "leads": [
        {
            "id": "379d5ece",
            "business_name": "ABC Plumbing Services",
            "industry": "plumbing",
            "website_url": "https://abc-plumbing.com",
            "contact_email": "owner@abc-plumbing.com",
            "contact_name": "John Smith",
            "contact_phone": "713-555-0101",
            "quality_score": 2,
            "status": "found",
            "created_at": "2026-03-01T18:01:35.884760",
            "cold_email_sent_at": None,
            "first_reply_at": None,
            "blurred_preview_sent_at": None,
            "full_design_sent_at": None,
            "invoice_sent_at": None,
            "stripe_session_id": None,
            "payment_confirmed_at": None,
            "client_preferred_channel": "email",
            "notes": "Website looks 2005-era, no mobile design"
        },
        {
            "id": "eaf3c8f4",
            "business_name": "Smith HVAC",
            "industry": "hvac",
            "website_url": "https://smith-hvac.net",
            "contact_email": "info@smith-hvac.net",
            "contact_name": "Mike Johnson",
            "contact_phone": "713-555-0202",
            "quality_score": 3,
            "status": "found",
            "created_at": "2026-03-01T18:01:35.885131",
            "cold_email_sent_at": None,
            "first_reply_at": None,
            "blurred_preview_sent_at": None,
            "full_design_sent_at": None,
            "invoice_sent_at": None,
            "stripe_session_id": None,
            "payment_confirmed_at": None,
            "client_preferred_channel": "email",
            "notes": "Dated design, poor SEO, contact form broken"
        },
        {
            "id": "655235d0",
            "business_name": "Green Landscaping",
            "industry": "landscaping",
            "website_url": "https://greenlandscape.biz",
            "contact_email": "green@greenlandscape.biz",
            "contact_name": "Sarah Lee",
            "contact_phone": "713-555-0303",
            "quality_score": 4,
            "status": "found",
            "created_at": "2026-03-01T18:01:35.886300",
            "cold_email_sent_at": None,
            "first_reply_at": None,
            "blurred_preview_sent_at": None,
            "full_design_sent_at": None,
            "invoice_sent_at": None,
            "stripe_session_id": None,
            "payment_confirmed_at": None,
            "client_preferred_channel": "email",
            "notes": "Basic HTML, no testimonials, outdated photos"
        }
    ]
}


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            
            if path == '/':
                self._serve_frontend()
            elif path == '/api/leads':
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self._json_response({"status": "success", "total": len(LEADS_DATA["leads"]), "leads": LEADS_DATA["leads"]})
            elif path == '/api/funnel/stats':
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self._get_stats()
            elif path == '/api/health':
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self._json_response({"status": "ok"})
            else:
                self.send_error(404)
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_error(500)
    
    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if path == '/api/leads':
                self._create_lead(body)
            elif path.startswith('/api/actions/send-cold-email/'):
                lead_id = path.split('/')[-1]
                self._json_response({"status": "success", "message": "Email queued"})
            else:
                self._json_response({"status": "ok"})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _json_response(self, data):
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _serve_frontend(self):
        frontend_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agency Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }
        .header { background: linear-gradient(135deg, #0070f3 0%, #0051ba 100%); color: white; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .header h1 { font-size: 28px; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 20px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
        .tab-button { padding: 12px 20px; background: none; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; transition: all 0.2s; }
        .tab-button.active { color: #0070f3; border-bottom-color: #0070f3; }
        .tab-button:hover { color: #0070f3; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .metric-card h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .metric-card .value { font-size: 32px; font-weight: bold; color: #0070f3; }
        .leads-table { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f9f9f9; padding: 15px; text-align: left; font-weight: 600; font-size: 13px; color: #666; border-bottom: 1px solid #eee; }
        td { padding: 15px; border-bottom: 1px solid #eee; font-size: 13px; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; background: #f0f0f0; color: #666; }
        .btn { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; font-size: 11px; font-weight: 600; color: #666; }
        .btn:hover { border-color: #0070f3; color: #0070f3; background: #f0f7ff; }
        .form { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); max-width: 600px; }
        .form h2 { margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 13px; color: #666; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; }
        .success { background: #d1e7dd; color: #0f5132; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ AI Agency Dashboard</h1>
        <p>Website Redesign Pipeline - Find, Outreach, Design, Convert</p>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('dashboard')">Dashboard</button>
            <button class="tab-button" onclick="switchTab('leads')">Leads</button>
            <button class="tab-button" onclick="switchTab('add-lead')">+ Add Lead</button>
        </div>

        <div id="dashboard" class="tab-content active">
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Leads</h3>
                    <div class="value" id="total-leads">3</div>
                </div>
                <div class="metric-card">
                    <h3>Cold Sent</h3>
                    <div class="value" id="cold-sent">0</div>
                </div>
                <div class="metric-card">
                    <h3>Replied</h3>
                    <div class="value" id="replied">0</div>
                </div>
                <div class="metric-card">
                    <h3>Paid</h3>
                    <div class="value" id="paid">0</div>
                </div>
            </div>
        </div>

        <div id="leads" class="tab-content">
            <div class="leads-table">
                <table>
                    <thead>
                        <tr>
                            <th>Business</th>
                            <th>Contact</th>
                            <th>Industry</th>
                            <th>Quality</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="leads-tbody">
                    </tbody>
                </table>
            </div>
        </div>

        <div id="add-lead" class="tab-content">
            <div class="form">
                <h2>Add New Lead</h2>
                <div id="form-message"></div>
                <div class="form-group">
                    <label>Business Name</label>
                    <input type="text" id="business_name" placeholder="ABC Plumbing">
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" id="contact_email" placeholder="owner@example.com">
                </div>
                <button class="btn" onclick="submitNewLead()" style="width: 100%; padding: 12px; background: #0070f3; color: white; border: none;">
                    Add Lead
                </button>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '';
        
        function switchTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
            if (name === 'leads') loadLeads();
        }
        
        async function loadLeads() {
            const resp = await fetch('/api/leads');
            const data = await resp.json();
            const tbody = document.getElementById('leads-tbody');
            tbody.innerHTML = '';
            data.leads.forEach(lead => {
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${lead.business_name}</strong></td>
                        <td>${lead.contact_email}</td>
                        <td>${lead.industry}</td>
                        <td>${lead.quality_score}/10</td>
                        <td><span class="status-badge">${lead.status}</span></td>
                        <td><button class="btn" onclick="alert('📧 Send email to ' + '${lead.contact_email}')">📧 Email</button></td>
                    </tr>
                `;
            });
        }
        
        async function submitNewLead() {
            const name = document.getElementById('business_name').value;
            const email = document.getElementById('contact_email').value;
            if (!name || !email) { alert('Fill in required fields'); return; }
            
            await fetch('/api/leads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ business_name: name, contact_email: email, industry: 'other', website_url: 'https://example.com', quality_score: 3 })
            });
            
            document.getElementById('business_name').value = '';
            document.getElementById('contact_email').value = '';
            document.getElementById('form-message').innerHTML = '<div class="success">✅ Lead added!</div>';
            setTimeout(() => { document.querySelector('[onclick="switchTab(\\'leads\\')"]').click(); }, 1000);
        }
        
        loadLeads();
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(frontend_html.encode())
    
    def _get_stats(self):
        leads = LEADS_DATA.get('leads', [])
        stats = {
            'total_leads': len(leads),
            'by_status': {},
            'conversion_rates': {'cold_to_replied': '0%', 'replied_to_paid': '0%', 'overall': '0%'}
        }
        self._json_response({"status": "success", "stats": stats})
    
    def _create_lead(self, body):
        try:
            lead_data = json.loads(body)
            import hashlib
            lead_id = hashlib.md5(f"{lead_data['business_name']}_{lead_data['contact_email']}".encode()).hexdigest()[:8]
            new_lead = {
                'id': lead_id,
                'business_name': lead_data['business_name'],
                'industry': lead_data.get('industry', 'other'),
                'website_url': lead_data.get('website_url', ''),
                'contact_email': lead_data['contact_email'],
                'contact_name': lead_data.get('contact_name', ''),
                'contact_phone': lead_data.get('contact_phone', ''),
                'quality_score': lead_data.get('quality_score', 3),
                'status': 'found',
                'created_at': datetime.utcnow().isoformat(),
                'cold_email_sent_at': None,
                'first_reply_at': None,
                'client_preferred_channel': 'email',
                'notes': ''
            }
            LEADS_DATA['leads'].append(new_lead)
            self._json_response({"status": "success", "lead_id": lead_id})
        except Exception as e:
            self._json_response({"error": str(e)})
    
    def log_message(self, format, *args):
        pass


def run_server(port=5000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"🚀 Dashboard running on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    run_server(port)
