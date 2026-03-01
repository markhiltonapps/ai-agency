#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        html = """<html><head><title>AI Agency</title><style>body{font-family:sans-serif;background:#f5f5f5;color:#333;margin:0;padding:0}.header{background:linear-gradient(135deg,#0070f3,#0051ba);color:white;padding:40px;text-align:center}.container{max-width:1200px;margin:0 auto;padding:40px}.card{background:white;padding:20px;border-radius:8px;margin:20px 0;box-shadow:0 1px 3px rgba(0,0,0,0.1)}.value{font-size:32px;font-weight:bold;color:#0070f3}</style></head><body><div class="header"><h1>AI Agency Dashboard</h1><p>Live and Working!</p></div><div class="container"><div class="card"><h2>Dashboard Status</h2><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px"><div><h3>Total Leads</h3><div class="value">3</div></div><div><h3>Cold Sent</h3><div class="value">0</div></div><div><h3>Replied</h3><div class="value">0</div></div><div><h3>Paid</h3><div class="value">0</div></div></div></div><div class="card"><h2>Status</h2><p>Your dashboard is live and running!</p></div></div></body></html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        return

port = int(os.getenv('PORT', 5000))
server = HTTPServer(('0.0.0.0', port), MyHandler)
print(f'Running on port {port}')
server.serve_forever()
