#!/usr/bin/env python3
"""
Outreach Agent for AI Website Design Agency
Integrates with Instantly.ai API to send cold emails and track replies
"""

import json
import requests
import base64
import hashlib
import hmac
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutreachAgent:
    """Handles cold email outreach via Instantly.ai API"""
    
    def __init__(self, api_key: str, domain: str = "neatoventures.com", sender_email: str = "outreach@neatoventures.com"):
        self.api_key = api_key
        self.domain = domain
        self.sender_email = sender_email
        self.base_url = "https://api.instantly.ai/api/v1"
        self.headers = self._build_headers()
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
    
    def _build_headers(self) -> Dict:
        """Build auth headers for Instantly.ai API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_cold_email(self, lead: Dict, mockup_url: Optional[str] = None) -> Dict:
        """
        Send cold email to prospect with blurred mockup preview
        
        Args:
            lead: {business_name, website_url, contact_email, quality_score}
            mockup_url: URL to blurred preview (optional, can be added later)
        
        Returns:
            {status, campaign_id, email_id, timestamp, error}
        """
        try:
            subject = f"{lead['business_name']} — I redesigned your website"
            
            # Build email body
            body = self._generate_email_body(lead, mockup_url)
            
            # Prepare payload for Instantly.ai
            payload = {
                "email": lead['contact_email'],
                "first_name": lead.get('contact_name', 'there').split()[0],
                "from_email": self.sender_email,
                "from_name": "Ninja Concepts",
                "subject": subject,
                "body": body,
                "campaign_id": lead['id'],  # Use lead ID as campaign marker
                "tags": ["cold_outreach", "website_redesign"]
            }
            
            # Call Instantly.ai API (flexible endpoint - assumes /send or /campaigns/{id}/send)
            response = requests.post(
                f"{self.base_url}/campaigns/send",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                # Fallback to alternative endpoint if first fails
                response = requests.post(
                    f"{self.base_url}/emails/send",
                    json=payload,
                    headers=self.headers,
                    timeout=10
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Update leads.json with sent status
            self._update_lead_status(
                lead['id'],
                status="cold_sent",
                cold_email_sent_at=datetime.utcnow().isoformat()
            )
            
            return {
                "status": "sent",
                "lead_id": lead['id'],
                "campaign_id": result.get('campaign_id', lead['id']),
                "email_id": result.get('email_id'),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to send email to {lead['contact_email']}: {str(e)}")
            return {
                "status": "error",
                "lead_id": lead['id'],
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _generate_email_body(self, lead: Dict, mockup_url: Optional[str] = None) -> str:
        """Generate compelling cold email body"""
        
        mockup_cta = f'<a href="{mockup_url}" style="background: #0070f3; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; margin-top: 20px;">See Blurred Preview</a>' if mockup_url else ""
        
        return f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">

<p>Hi there,</p>

<p>I've been analyzing {lead['business_name']}'s web presence, and I see a huge opportunity.</p>

<p>Your current website has the basics, but it's leaving money on the table:</p>
<ul>
<li>Outdated design (potential clients bounce immediately)</li>
<li>Poor mobile experience</li>
<li>Weak conversion optimization</li>
</ul>

<p><strong>Here's the good news:</strong> I've already redesigned your entire site. Clean, modern, mobile-first. Built to convert.</p>

<p>Rather than pitch you for 20 minutes, I'll show you instead. The preview below is blurred—you'll see the full design once you're interested.</p>

{mockup_cta}

<p>If it resonates, we can talk about implementation. Cost is reasonable ($500+), timeline is fast (2-4 weeks), and the result speaks for itself.</p>

<p>What do you think?</p>

<p>—<br/>
Ninja Concepts<br/>
AI-Powered Website Redesign<br/>
neatoventures.com</p>

</body>
</html>
"""
    
    def check_replies(self, lead_id: str, campaign_id: str) -> Dict:
        """
        Poll Instantly.ai for replies to a sent email
        
        Returns:
            {status, reply_count, latest_reply, timestamp}
        """
        try:
            # Fetch campaign/email stats (flexible endpoint)
            response = requests.get(
                f"{self.base_url}/campaigns/{campaign_id}/replies",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 404:
                # Try alternative endpoint
                response = requests.get(
                    f"{self.base_url}/emails/{campaign_id}/replies",
                    headers=self.headers,
                    timeout=10
                )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('replies', []):
                latest_reply = data['replies'][0]  # Most recent reply
                
                # Update lead status
                self._update_lead_status(
                    lead_id,
                    status="replied",
                    first_reply_at=datetime.utcnow().isoformat()
                )
                
                return {
                    "status": "reply_detected",
                    "lead_id": lead_id,
                    "reply_count": len(data['replies']),
                    "latest_reply": latest_reply.get('body', ''),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "status": "no_reply",
                "lead_id": lead_id,
                "reply_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to check replies for {lead_id}: {str(e)}")
            return {
                "status": "error",
                "lead_id": lead_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _update_lead_status(self, lead_id: str, status: str, **kwargs):
        """Update lead status in leads.json"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            for lead in data.get('leads', []):
                if lead['id'] == lead_id:
                    lead['status'] = status
                    for key, value in kwargs.items():
                        lead[key] = value
                    break
            
            with open(self.leads_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to update lead {lead_id}: {str(e)}")


def main():
    """Example usage"""
    api_key = open("/home/ubuntu/.openclaw/workspace/secrets/instantly_api_key.txt").read().strip()
    agent = OutreachAgent(api_key)
    
    # Example: send email to first lead
    with open("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json", 'r') as f:
        data = json.load(f)
        if data['leads']:
            lead = data['leads'][0]
            result = agent.send_cold_email(lead)
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
