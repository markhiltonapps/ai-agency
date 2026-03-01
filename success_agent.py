#!/usr/bin/env python3
"""
Client Success Agent for AI Website Design Agency
Handles post-payment client communication and project delivery
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuccessAgent:
    """Manages client communication and project delivery"""
    
    def __init__(self):
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
    
    def start_project(self, lead_id: str) -> Dict:
        """
        Triggered when payment confirmed.
        Initialize project folder, send welcome message to client
        
        Returns:
            {status, project_folder, welcome_sent, client_channel, timestamp}
        """
        try:
            # Load lead
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                return {"status": "error", "error": "Lead not found"}
            
            # Create project folder
            projects_dir = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/clients")
            projects_dir.mkdir(parents=True, exist_ok=True)
            project_folder = projects_dir / lead_id
            project_folder.mkdir(exist_ok=True)
            
            # Create project manifest
            manifest = {
                "lead_id": lead_id,
                "business_name": lead['business_name'],
                "contact_name": lead.get('contact_name'),
                "contact_email": lead['contact_email'],
                "contact_phone": lead.get('contact_phone'),
                "preferred_channel": lead.get('client_preferred_channel', 'email'),
                "status": "project_started",
                "created_at": datetime.utcnow().isoformat(),
                "design_requirements": {
                    "industry": lead.get('industry'),
                    "color_preference": None,
                    "additional_pages": [],
                    "features_requested": []
                },
                "deliverables": {
                    "homepage": False,
                    "services_page": False,
                    "about_page": False,
                    "contact_page": False,
                    "blog": False,
                    "mobile_responsive": False
                }
            }
            
            with open(project_folder / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Update lead status
            self._update_lead(lead_id, status='design_in_progress')
            
            # Prepare welcome message
            welcome_msg = self._generate_welcome_message(lead)
            
            # Route message to preferred channel (for now, log intent)
            client_channel = lead.get('client_preferred_channel', 'email')
            logger.info(f"[SUCCESS] Sending welcome via {client_channel} to {lead['contact_email']}")
            
            return {
                "status": "success",
                "lead_id": lead_id,
                "project_folder": str(project_folder),
                "welcome_message": welcome_msg,
                "client_channel": client_channel,
                "client_email": lead['contact_email'],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to start project for {lead_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _generate_welcome_message(self, lead: Dict) -> str:
        """Generate personalized welcome message"""
        return f"""
Hi {lead.get('contact_name', 'there')},

🎉 Your website redesign is officially starting!

Here's what happens next:
1. We'll send you a design kickoff questionnaire (should take 10 min)
2. You'll review the initial mockups (3-5 days)
3. We'll refine based on your feedback
4. Final website goes live (2-4 weeks total)

Your project folder is ready, and we're excited to get started. Expect the questionnaire in your inbox within 24 hours.

Questions? Just reply to this message.

Excited to show you what's possible,
Ninja Concepts
"""
    
    def send_status_update(self, lead_id: str, message: str, channel: str = None) -> Dict:
        """Send project status update to client"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                return {"status": "error", "error": "Lead not found"}
            
            # Use provided channel or client preference
            client_channel = channel or lead.get('client_preferred_channel', 'email')
            
            # Log intent to send (actual sending handled by message tool or email service)
            logger.info(f"[UPDATE] Sending {client_channel} to {lead['contact_email']}: {message[:50]}...")
            
            return {
                "status": "queued",
                "lead_id": lead_id,
                "channel": client_channel,
                "client_email": lead['contact_email'],
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to send update for {lead_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def deliver_design(self, lead_id: str, design_url: str) -> Dict:
        """Send completed design to client"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            lead = None
            for l in data.get('leads', []):
                if l['id'] == lead_id:
                    lead = l
                    break
            
            if not lead:
                return {"status": "error", "error": "Lead not found"}
            
            delivery_msg = f"""
Hi {lead.get('contact_name', 'there')},

Your new website is ready! 🚀

Live preview: {design_url}

Take a look and let us know if you'd like any adjustments. We're here to make sure it's perfect.

You can:
- View the full site
- Test on mobile
- Send feedback
- Request modifications

Reply here with any thoughts!

Cheers,
Ninja Concepts
"""
            
            # Update lead status
            self._update_lead(lead_id, status='design_delivered')
            
            return {
                "status": "success",
                "lead_id": lead_id,
                "design_url": design_url,
                "delivery_message": delivery_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to deliver design for {lead_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
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


def main():
    """Example usage"""
    agent = SuccessAgent()
    
    # Example: start project for paid lead
    result = agent.start_project('lead_001')
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
