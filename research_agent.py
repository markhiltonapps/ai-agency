#!/usr/bin/env python3
"""
Research Agent for AI Website Design Agency
Finds service businesses with poor websites
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """Finds and scores potential leads"""
    
    def __init__(self):
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
    
    def add_manual_lead(self, business_data: Dict) -> Dict:
        """
        Add a manually researched lead to the database
        
        Args:
            business_data: {
                business_name,
                industry,
                website_url,
                contact_email,
                contact_name,
                contact_phone,
                quality_score (1-10)
            }
        
        Returns:
            {status, lead_id, timestamp}
        """
        try:
            # Load existing leads
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            # Generate unique lead ID
            lead_id = hashlib.md5(
                f"{business_data['business_name']}_{business_data['contact_email']}".encode()
            ).hexdigest()[:8]
            
            # Create lead object
            lead = {
                'id': lead_id,
                'business_name': business_data['business_name'],
                'industry': business_data.get('industry', 'service'),
                'website_url': business_data['website_url'],
                'contact_email': business_data['contact_email'],
                'contact_name': business_data.get('contact_name'),
                'contact_phone': business_data.get('contact_phone'),
                'quality_score': business_data.get('quality_score', 3),  # Default: poor
                'status': 'found',
                'created_at': datetime.utcnow().isoformat(),
                'cold_email_sent_at': None,
                'first_reply_at': None,
                'blurred_preview_sent_at': None,
                'full_design_sent_at': None,
                'invoice_sent_at': None,
                'stripe_session_id': None,
                'payment_confirmed_at': None,
                'client_preferred_channel': business_data.get('client_preferred_channel', 'email'),
                'notes': business_data.get('notes', '')
            }
            
            # Add to leads
            data['leads'].append(lead)
            
            # Save
            with open(self.leads_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Added lead: {business_data['business_name']} (score: {lead['quality_score']}/10)")
            
            return {
                "status": "success",
                "lead_id": lead_id,
                "business_name": business_data['business_name'],
                "industry": business_data.get('industry'),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to add lead: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_leads_by_status(self, status: str = None) -> Dict:
        """List all leads, optionally filtered by status"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            leads = data.get('leads', [])
            
            if status:
                leads = [l for l in leads if l['status'] == status]
            
            return {
                "status": "success",
                "total": len(leads),
                "leads": leads,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to list leads: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def score_website_quality(self, website_url: str) -> int:
        """
        Estimate website quality (1-10, lower = worse = better target)
        
        In full version, would check:
        - Mobile responsiveness
        - Page speed
        - Design age (outdated tech signals)
        - SEO signals
        - Content freshness
        
        For MVP, return placeholder
        """
        # Placeholder: random quality score for testing
        return 3  # Poor quality (good target)


def main():
    """Example usage"""
    agent = ResearchAgent()
    
    # Example: add some test leads
    test_leads = [
        {
            'business_name': 'ABC Plumbing Services',
            'industry': 'plumbing',
            'website_url': 'https://abc-plumbing.com',
            'contact_email': 'owner@abc-plumbing.com',
            'contact_name': 'John Smith',
            'contact_phone': '713-555-0101',
            'quality_score': 2,
            'notes': 'Website looks 2005-era, no mobile design'
        },
        {
            'business_name': 'Smith HVAC',
            'industry': 'hvac',
            'website_url': 'https://smith-hvac.net',
            'contact_email': 'info@smith-hvac.net',
            'contact_name': 'Mike Johnson',
            'contact_phone': '713-555-0202',
            'quality_score': 3,
            'notes': 'Dated design, poor SEO, contact form broken'
        },
        {
            'business_name': 'Green Landscaping',
            'industry': 'landscaping',
            'website_url': 'https://greenlandscape.biz',
            'contact_email': 'green@greenlandscape.biz',
            'contact_name': 'Sarah Lee',
            'contact_phone': '713-555-0303',
            'quality_score': 4,
            'notes': 'Basic HTML, no testimonials, outdated photos'
        }
    ]
    
    for lead_data in test_leads:
        result = agent.add_manual_lead(lead_data)
        print(json.dumps(result, indent=2))
    
    # List all leads
    print("\n--- All Leads ---")
    all_leads = agent.list_leads_by_status()
    print(json.dumps(all_leads, indent=2))


if __name__ == "__main__":
    main()
