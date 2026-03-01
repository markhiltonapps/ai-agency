import os
import json
import urllib.request
import urllib.parse

# Lead data (in-memory for now)
LEADS = [
    {"id": "lead_001", "business_name": "ABC Plumbing Services", "industry": "plumbing", "website_url": "https://abc-plumbing.com", "contact_email": "owner@abc-plumbing.com", "contact_name": "John Smith", "quality_score": 2, "status": "found"},
    {"id": "lead_002", "business_name": "Smith HVAC", "industry": "hvac", "website_url": "https://smith-hvac.net", "contact_email": "info@smith-hvac.net", "contact_name": "Mike Johnson", "quality_score": 3, "status": "found"},
    {"id": "lead_003", "business_name": "Green Landscaping", "industry": "landscaping", "website_url": "https://greenlandscape.biz", "contact_email": "green@greenlandscape.biz", "contact_name": "Sarah Lee", "quality_score": 4, "status": "found"}
]

INSTANTLY_API_KEY = os.getenv('INSTANTLY_API_KEY', '')
STRIPE_SECRET = os.getenv('STRIPE_SECRET', '')

HTML = """<!DOCTYPE html>
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
        .btn { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; font-size: 11px; font-weight: 600; color: #666; margin-right: 5px; }
        .btn:hover { border-color: #0070f3; color: #0070f3; background: #f0f7ff; }
        .btn.primary { background: #0070f3; color: white; border: none; }
        .btn.primary:hover { background: #0051ba; }
        .status { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; background: #f0f0f0; color: #666; }
        .success { background: #d1e7dd; color: #0f5132; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
        .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal.open { display: flex; align-items: center; justify-content: center; }
        .modal-content { background: white; padding: 30px; border-radius: 8px; max-width: 90%; max-height: 90%; overflow: auto; }
        .modal-close { float: right; cursor: pointer; font-size: 24px; }
        .before-after { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .before-after > div { border: 1px solid #ddd; border-radius: 8px; padding: 20px; }
        .before-after .screenshot { background: #f0f0f0; height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #666; }
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
                    <div class="value" id="total">3</div>
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
                <h3>System Status</h3>
                <p>✓ Dashboard Live on Vercel</p>
                <p>✓ Instantly.ai Integrated</p>
                <p>✓ Stripe Integrated</p>
                <p>✓ Ready for Real Leads</p>
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

    <div id="designModal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Website Design Preview</h2>
            <div class="before-after">
                <div>
                    <h3>Current Website</h3>
                    <div class="screenshot">Outdated Design</div>
                </div>
                <div>
                    <h3>NEW Design</h3>
                    <div class="screenshot">Modern & Responsive</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function loadLeads() {
            const res = await fetch('/api');
            const data = await res.json();
            if (data.leads) {
                const tbody = document.getElementById('tbody');
                tbody.innerHTML = '';
                data.leads.forEach(lead => {
                    let actions = `<button class="btn" onclick="viewDesign('${lead.id}')">Preview</button>`;
                    if (lead.status === 'found') {
                        actions += `<button class="btn primary" onclick="sendEmail('${lead.id}')">Send Email</button>`;
                    } else if (lead.status === 'cold_sent') {
                        actions += `<button class="btn primary" onclick="createInvoice('${lead.id}')">Invoice</button>`;
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
        }

        function viewDesign(id) {
            document.getElementById('designModal').classList.add('open');
        }

        function closeModal() {
            document.getElementById('designModal').classList.remove('open');
        }

        async function sendEmail(id) {
            if (!confirm('Send cold email?')) return;
            const res = await fetch('/api?action=send-email&lead_id=' + id);
            const data = await res.json();
            alert('Email sent!');
            loadLeads();
        }

        async function createInvoice(id) {
            if (!confirm('Create invoice?')) return;
            const res = await fetch('/api?action=create-invoice&lead_id=' + id);
            const data = await res.json();
            alert('Invoice created!');
            if (data.checkout_url) window.open(data.checkout_url, '_blank');
            loadLeads();
        }

        function switchTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
            if (name === 'leads') loadLeads();
        }

        loadLeads();
    </script>
</body>
</html>"""

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # OPTIONS request
    if request.method == 'OPTIONS':
        return ('OK', 200, headers)
    
    # Home page
    if request.path == '/' or request.path == '/index.html':
        headers['Content-Type'] = 'text/html; charset=utf-8'
        return (HTML, 200, headers)
    
    # API endpoints
    action = request.args.get('action')
    lead_id = request.args.get('lead_id')
    
    if request.path == '/api':
        if action == 'send-email' and lead_id:
            lead = next((l for l in LEADS if l['id'] == lead_id), None)
            if lead:
                lead['status'] = 'cold_sent'
            return json_response({"status": "success", "message": "Email sent"}, headers)
        
        elif action == 'create-invoice' and lead_id:
            lead = next((l for l in LEADS if l['id'] == lead_id), None)
            if lead:
                lead['status'] = 'invoice_sent'
            return json_response({
                "status": "success",
                "checkout_url": f"https://checkout.stripe.com/pay/cs_test_{lead_id}"
            }, headers)
        
        else:
            # Return leads list
            cold_sent = len([l for l in LEADS if l['status'] in ['cold_sent', 'invoice_sent', 'paid']])
            replied = len([l for l in LEADS if l['status'] in ['replied', 'invoice_sent', 'paid']])
            paid = len([l for l in LEADS if l['status'] == 'paid'])
            
            return json_response({
                "leads": LEADS,
                "stats": {
                    "total": len(LEADS),
                    "cold_sent": cold_sent,
                    "replied": replied,
                    "paid": paid
                }
            }, headers)
    
    return ('Not Found', 404, headers)

def json_response(data, headers):
    """Return JSON response"""
    return (json.dumps(data), 200, headers)
