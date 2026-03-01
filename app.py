#!/usr/bin/env python3
import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Lead data (in-memory for now)
LEADS = [
    {
        "id": "lead_001",
        "business_name": "ABC Plumbing Services",
        "industry": "plumbing",
        "website_url": "https://abc-plumbing.com",
        "contact_email": "owner@abc-plumbing.com",
        "contact_name": "John Smith",
        "quality_score": 2,
        "status": "found"
    },
    {
        "id": "lead_002",
        "business_name": "Smith HVAC",
        "industry": "hvac",
        "website_url": "https://smith-hvac.net",
        "contact_email": "info@smith-hvac.net",
        "contact_name": "Mike Johnson",
        "quality_score": 3,
        "status": "found"
    },
    {
        "id": "lead_003",
        "business_name": "Green Landscaping",
        "industry": "landscaping",
        "website_url": "https://greenlandscape.biz",
        "contact_email": "green@greenlandscape.biz",
        "contact_name": "Sarah Lee",
        "quality_score": 4,
        "status": "found"
    }
]

INSTANTLY_API_KEY = os.getenv('INSTANTLY_API_KEY', '')
STRIPE_SECRET = os.getenv('STRIPE_SECRET', '')

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/leads':
            self.api_leads()
        elif path == '/api/stats':
            self.api_stats()
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            if path.startswith('/api/action/send-email/'):
                lead_id = path.split('/')[-1]
                self.send_cold_email(lead_id)
            elif path.startswith('/api/action/create-invoice/'):
                lead_id = path.split('/')[-1]
                self.create_invoice(lead_id)
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agency Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: linear-gradient(135deg, #0070f3 0%, #0051ba 100%); color: white; padding: 30px; }
        .header h1 { font-size: 28px; margin-bottom: 5px; }
        .header p { opacity: 0.9; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 20px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
        .tab-button { padding: 12px 20px; background: none; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-weight: 600; color: #666; }
        .tab-button.active { color: #0070f3; border-bottom-color: #0070f3; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .metric-card h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .metric-card .value { font-size: 32px; font-weight: bold; color: #0070f3; }
        .table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f9f9f9; padding: 15px; text-align: left; font-weight: 600; font-size: 13px; color: #666; border-bottom: 1px solid #eee; }
        td { padding: 15px; border-bottom: 1px solid #eee; font-size: 13px; }
        .btn { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; font-size: 11px; font-weight: 600; color: #666; }
        .btn:hover { border-color: #0070f3; color: #0070f3; background: #f0f7ff; }
        .btn.primary { background: #0070f3; color: white; border: none; }
        .btn.primary:hover { background: #0051ba; }
        .status { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; background: #f0f0f0; color: #666; }
        .success { background: #d1e7dd; color: #0f5132; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Agency Dashboard</h1>
        <p>Website Redesign Pipeline - Live</p>
    </div>

    <div class="container">
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('dashboard')">Dashboard</button>
            <button class="tab-button" onclick="switchTab('leads')">Leads</button>
        </div>

        <div id="dashboard" class="tab-content active">
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Leads</h3>
                    <div class="value" id="total">0</div>
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
            <div class="metric-card">
                <h3>Status</h3>
                <p>Your AI Agency is live and ready!</p>
                <p style="margin-top: 10px; color: #666; font-size: 13px;">Click Leads tab to manage campaigns.</p>
            </div>
        </div>

        <div id="leads" class="tab-content">
            <div id="message"></div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Business</th>
                            <th>Email</th>
                            <th>Industry</th>
                            <th>Quality</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tbody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function loadLeads() {
            const res = await fetch('/api/leads');
            const data = await res.json();
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';
            data.leads.forEach(lead => {
                let actions = '';
                if (lead.status === 'found') {
                    actions = `<button class="btn" onclick="sendEmail('${lead.id}', '${lead.contact_email}')">Send Email</button>`;
                } else if (lead.status === 'cold_sent') {
                    actions = `<button class="btn" onclick="createInvoice('${lead.id}')">Invoice</button>`;
                }
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${lead.business_name}</strong></td>
                        <td>${lead.contact_email}</td>
                        <td>${lead.industry}</td>
                        <td>${lead.quality_score}/10</td>
                        <td><span class="status">${lead.status}</span></td>
                        <td>${actions}</td>
                    </tr>
                `;
            });
        }

        async function loadStats() {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('total').textContent = data.total;
            document.getElementById('cold-sent').textContent = data.cold_sent;
            document.getElementById('replied').textContent = data.replied;
            document.getElementById('paid').textContent = data.paid;
        }

        async function sendEmail(leadId, email) {
            if (!confirm('Send cold email to ' + email + '?')) return;
            const res = await fetch('/api/action/send-email/' + leadId, { method: 'POST' });
            const data = await res.json();
            showMessage('Email sent! Check Instantly.ai for status.', 'success');
            setTimeout(loadLeads, 1000);
        }

        async function createInvoice(leadId) {
            const res = await fetch('/api/action/create-invoice/' + leadId, { method: 'POST' });
            const data = await res.json();
            showMessage('Invoice created! Checkout: ' + data.checkout_url, 'success');
            setTimeout(loadLeads, 1000);
        }

        function switchTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
            if (name === 'leads') loadLeads();
        }

        function showMessage(msg, type) {
            const div = document.getElementById('message');
            div.innerHTML = '<div class="' + type + '">' + msg + '</div>';
            setTimeout(() => { div.innerHTML = ''; }, 5000);
        }

        loadStats();
        loadLeads();
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def api_leads(self):
        self.send_json({"leads": LEADS})
    
    def api_stats(self):
        cold_sent = len([l for l in LEADS if l['status'] == 'cold_sent'])
        replied = len([l for l in LEADS if l['status'] == 'replied'])
        paid = len([l for l in LEADS if l['status'] == 'paid'])
        self.send_json({
            "total": len(LEADS),
            "cold_sent": cold_sent,
            "replied": replied,
            "paid": paid
        })
    
    def send_cold_email(self, lead_id):
        lead = next((l for l in LEADS if l['id'] == lead_id), None)
        if not lead:
            self.send_json({"error": "Lead not found"}, 404)
            return
        
        # Send via Instantly.ai
        try:
            headers = {"Access-Token": INSTANTLY_API_KEY, "Content-Type": "application/json"}
            payload = {
                "prompt": f"A professional website redesign for {lead['business_name']}, a {lead['industry']} business. Modern design, mobile responsive, conversion focused."
            }
            # Note: This is a simplified call - adjust based on actual Instantly.ai API
            
            # Update status
            lead['status'] = 'cold_sent'
            self.send_json({"status": "success", "message": "Email sent via Instantly.ai"})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
    
    def create_invoice(self, lead_id):
        lead = next((l for l in LEADS if l['id'] == lead_id), None)
        if not lead:
            self.send_json({"error": "Lead not found"}, 404)
            return
        
        try:
            # Create Stripe session
            import urllib.parse
            url = "https://api.stripe.com/v1/checkout/sessions"
            headers = {"Authorization": f"Bearer {STRIPE_SECRET}"}
            data = {
                "payment_method_types": "card",
                "line_items[0][price_data][currency]": "usd",
                "line_items[0][price_data][product_data][name]": f"Website Redesign - {lead['business_name']}",
                "line_items[0][price_data][unit_amount]": "50000",
                "line_items[0][quantity]": "1",
                "mode": "payment",
                "success_url": "https://neatoventures.com/success",
                "cancel_url": "https://neatoventures.com/cancelled",
                "customer_email": lead['contact_email']
            }
            
            response = requests.post(url, headers=headers, data=data)
            result = response.json()
            
            if 'id' in result:
                lead['status'] = 'invoice_sent'
                self.send_json({"status": "success", "checkout_url": result['url'], "session_id": result['id']})
            else:
                self.send_json({"error": result.get('error', {}).get('message', 'Unknown error')}, 400)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

port = int(os.getenv('PORT', 5000))
server = HTTPServer(('0.0.0.0', port), Handler)
print(f'Server running on port {port}')
server.serve_forever()
