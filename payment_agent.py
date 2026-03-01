#!/usr/bin/env python3
"""
Payment & Invoice Agent for AI Website Design Agency
Handles Stripe invoicing, payment processing, and webhook handling
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stripe import (try/except for compatibility)
try:
    import stripe
except ImportError:
    stripe = None


class PaymentAgent:
    """Handles Stripe payments, invoicing, and checkout"""
    
    def __init__(self, stripe_secret_key: str, webhook_signing_secret: str):
        if stripe:
            stripe.api_key = stripe_secret_key
        self.stripe_secret_key = stripe_secret_key
        self.webhook_signing_secret = webhook_signing_secret
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
        self.invoices_dir = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/invoices")
        self.invoices_dir.mkdir(parents=True, exist_ok=True)
    
    def create_invoice(self, lead: Dict, amount: int = 50000) -> Dict:
        """
        Create HTML invoice with Stripe checkout link
        
        Args:
            lead: {id, business_name, contact_email, contact_name}
            amount: Price in cents (default $500 = 50000 cents)
        
        Returns:
            {status, invoice_path, stripe_session_id, checkout_url, timestamp}
        """
        try:
            # Generate invoice ID
            invoice_id = f"INV-{lead['id']}-{datetime.now().strftime('%Y%m%d')}"
            invoice_number = invoice_id.replace('INV-', '')
            
            # Create Stripe checkout session
            if not stripe:
                raise Exception("Stripe not installed. Run: pip install stripe")
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Website Redesign - {lead['business_name']}",
                            'description': 'Professional website redesign with design, development, and deployment'
                        },
                        'unit_amount': amount
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url='https://neatoventures.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://neatoventures.com/cancelled',
                customer_email=lead['contact_email'],
                metadata={
                    'lead_id': lead['id'],
                    'business_name': lead['business_name'],
                    'invoice_id': invoice_id
                }
            )
            
            # Generate HTML invoice
            html_content = self._generate_invoice_html(
                lead, invoice_id, amount, session.url
            )
            
            # Save invoice PDF path (would be converted to PDF in production)
            invoice_path = self.invoices_dir / f"{invoice_id}.html"
            with open(invoice_path, 'w') as f:
                f.write(html_content)
            
            # Update leads.json
            self._update_lead(
                lead['id'],
                status='invoice_sent',
                stripe_session_id=session.id,
                invoice_sent_at=datetime.utcnow().isoformat()
            )
            
            return {
                "status": "success",
                "lead_id": lead['id'],
                "invoice_id": invoice_id,
                "stripe_session_id": session.id,
                "checkout_url": session.url,
                "invoice_path": str(invoice_path),
                "amount_usd": amount / 100,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            if 'Stripe' in str(type(e)):
                logger.error(f"Stripe error creating invoice: {str(e)}")
            else:
                logger.error(f"Error creating invoice: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _generate_invoice_html(self, lead: Dict, invoice_id: str, amount: int, checkout_url: str) -> str:
        """Generate HTML invoice template"""
        amount_usd = amount / 100
        due_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .invoice-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
            border-bottom: 2px solid #0070f3;
            padding-bottom: 20px;
        }}
        .company {{
            font-weight: bold;
            font-size: 24px;
        }}
        .invoice-number {{
            text-align: right;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}
        .total-row {{
            font-weight: bold;
            font-size: 18px;
        }}
        .cta-button {{
            background: #0070f3;
            color: white;
            padding: 16px 32px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            margin-top: 30px;
            font-size: 16px;
            font-weight: 600;
        }}
        .payment-link {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        .due-date {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>

<div class="invoice-header">
    <div>
        <div class="company">Ninja Concepts</div>
        <div>neatoventures.com</div>
    </div>
    <div class="invoice-number">
        <strong>Invoice #{invoice_id}</strong><br/>
        <div class="due-date">Due: {due_date}</div>
    </div>
</div>

<h2>Invoice</h2>

<table>
    <tr>
        <td><strong>Bill To:</strong><br/>{lead.get('contact_name', 'Client')}<br/>{lead['business_name']}<br/>{lead['contact_email']}</td>
    </tr>
</table>

<table>
    <thead>
        <tr>
            <th>Description</th>
            <th style="text-align: right;">Amount</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Website Redesign &amp; Development</td>
            <td style="text-align: right;">${{amount_usd:.2f}}</td>
        </tr>
        <tr class="total-row">
            <td>Total Due</td>
            <td style="text-align: right;">${{amount_usd:.2f}}</td>
        </tr>
    </tbody>
</table>

<h3>Payment Instructions</h3>
<p>Click the button below to pay securely via Stripe:</p>

<a href="{checkout_url}" class="cta-button">Pay Now →</a>

<div class="payment-link">
    <strong>Or copy this link:</strong><br/>
    <small>{checkout_url}</small>
</div>

<p style="margin-top: 40px; color: #666; font-size: 14px;">
    Thank you for your business! If you have any questions, please don't hesitate to reach out.
</p>

</body>
</html>
"""
    
    def _update_lead(self, lead_id: str, **kwargs):
        """Update lead in leads.json"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            for lead in data.get('leads', []):
                if lead['id'] == lead_id:
                    for key, value in kwargs.items():
                        lead[key] = value
                    break
            
            with open(self.leads_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to update lead {lead_id}: {str(e)}")


class WebhookHandler:
    """Flask app to handle Stripe webhooks"""
    
    def __init__(self, webhook_secret: str):
        self.app = Flask(__name__)
        self.webhook_secret = webhook_secret
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
        
        @self.app.route('/webhooks/stripe', methods=['POST'])
        def handle_webhook():
            return self._process_webhook(request)
    
    def _process_webhook(self, request) -> tuple:
        """Process Stripe webhook event"""
        try:
            # Verify webhook signature
            sig_header = request.headers.get('stripe-signature', '')
            body = request.get_data()
            
            try:
                event = stripe.Webhook.construct_event(
                    body, sig_header, self.webhook_secret
                )
            except ValueError:
                logger.error("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Handle payment success
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                self._handle_payment_success(session)
            
            return jsonify({'success': True}), 200
        
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    def _handle_payment_success(self, session: dict):
        """Update lead status when payment succeeds"""
        try:
            lead_id = session['metadata'].get('lead_id')
            
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            for lead in data.get('leads', []):
                if lead['id'] == lead_id:
                    lead['status'] = 'paid'
                    lead['payment_confirmed_at'] = datetime.utcnow().isoformat()
                    lead['stripe_session_id'] = session['id']
                    break
            
            with open(self.leads_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Payment confirmed for lead {lead_id}")
        
        except Exception as e:
            logger.error(f"Failed to process payment success: {str(e)}")


def main():
    """Example usage"""
    stripe_key = open("/home/ubuntu/.openclaw/workspace/secrets/stripe_keys.json").read()
    stripe_data = json.loads(stripe_key)
    
    agent = PaymentAgent(
        stripe_secret_key=stripe_data['secret_key_test'],
        webhook_signing_secret=stripe_data['webhook_signing_secret']
    )
    
    # Example: create invoice
    lead = {
        'id': 'lead_001',
        'business_name': 'ABC Plumbing',
        'contact_email': 'owner@abcplumbing.com',
        'contact_name': 'John Smith'
    }
    
    result = agent.create_invoice(lead, amount=50000)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
