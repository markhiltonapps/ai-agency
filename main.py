#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        .header p { opacity: 0.9; font-size: 14px; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 20px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
        .tab-button { padding: 12px 20px; background: none; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; }
        .tab-button.active { color: #0070f3; border-bottom-color: #0070f3; }
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
        .btn { padding: 6px 12px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; font-size: 11px; font-weight: 600; color: #666; }
        .btn:hover { border-color: #0070f3; color: #0070f3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ AI Agency Dashboard</h1>
        <p>Website Redesign Pipeline - LIVE!</p>
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
                    <div class="value">3</div>
                </div>
                <div class="metric-card">
                    <h3>Cold Sent</h3>
                    <div class="value">0</div>
                </div>
                <div class="metric-card">
                    <h3>Replied</h3>
                    <div class="value">0</div>
                </div>
                <div class="metric-card">
                    <h3>Paid</h3>
                    <div class="value">0</div>
                </div>
            </div>
            <div class="metric-card">
                <h3 style="margin-bottom: 15px;">✅ Dashboard is LIVE!</h3>
                <p>Your AI Agency backend is running successfully on Railway.</p>
                <p style="margin-top: 15px; color: #666; font-size: 13px;">
                    Ready to manage your website redesign pipeline, send cold emails, process Stripe payments, and track client projects.
                </p>
            </div>
        </div>

        <div id="leads" class="tab-content">
            <div class="leads-table">
                <table>
                    <thead>
                        <tr>
                            <th>Business</th>
                            <th>Email</th>
                            <th>Industry</th>
                            <th>Quality</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>ABC Plumbing Services</strong></td>
                            <td>owner@abc-plumbing.com</td>
                            <td>plumbing</td>
                            <td>2/10</td>
                            <td>found</td>
                        </tr>
                        <tr>
                            <td><strong>Smith HVAC</strong></td>
                            <td>info@smith-hvac.net</td>
                            <td>hvac</td>
                            <td>3/10</td>
                            <td>found</td>
                        </tr>
                        <tr>
                            <td><strong>Green Landscaping</strong></td>
                            <td>green@greenlandscape.biz</td>
                            <td>landscaping</td>
                            <td>4/10</td>
                            <td>found</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function switchTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML.encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Server running on port {port}')
    server.serve_forever()
