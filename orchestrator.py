#!/usr/bin/env python3
"""
Orchestrator for AI Website Design Agency
Coordinates flow: Research → Outreach → Design → Payment → Success
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging
import asyncio

from research_agent import ResearchAgent
from outreach_agent import OutreachAgent
from design_agent import DesignAgent
from payment_agent import PaymentAgent
from success_agent import SuccessAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgencyOrchestrator:
    """Orchestrates the entire lead-to-payment workflow"""
    
    def __init__(self):
        self.leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")
        
        # Initialize agents
        self.research = ResearchAgent()
        
        # Load credentials
        with open("/home/ubuntu/.openclaw/workspace/secrets/instantly_api_key.txt") as f:
            instantly_key = f.read().strip()
        self.outreach = OutreachAgent(instantly_key)
        
        self.design = DesignAgent(
            netlify_token="nfp_T5q16R9XEYjBgroitvjyEY9SZKbKPXXA4d4e",
            site_id="5255436b-dcfd-485b-88f9-03b121d85504"
        )
        
        with open("/home/ubuntu/.openclaw/workspace/secrets/stripe_keys.json") as f:
            stripe_keys = json.load(f)
        self.payment = PaymentAgent(
            stripe_secret_key=stripe_keys['secret_key_test'],
            webhook_signing_secret=stripe_keys['webhook_signing_secret']
        )
        
        self.success = SuccessAgent()
    
    async def process_lead(self, lead_id: str) -> Dict:
        """
        Process a single lead through the entire funnel:
        found → cold_sent → replied → design_ready → invoice_sent → paid
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
            
            status = lead['status']
            logger.info(f"Processing {lead['business_name']} (status: {status})")
            
            # Step 1: Send cold email
            if status == 'found':
                logger.info(f"→ Sending cold email to {lead['contact_email']}")
                result = self.outreach.send_cold_email(lead)
                if result['status'] == 'sent':
                    return {"status": "cold_email_sent", "lead_id": lead_id, "next_step": "waiting_for_reply"}
            
            # Step 2: Check for replies
            elif status == 'cold_sent':
                logger.info(f"→ Checking for replies from {lead['business_name']}")
                result = self.outreach.check_replies(lead_id, lead.get('campaign_id', lead_id))
                if result['status'] == 'reply_detected':
                    logger.info(f"  ✓ Got reply! Sending blurred preview...")
                    # Generate and send blurred preview
                    blur_result = await self.design.blur_preview(lead['website_url'], lead_id)
                    if blur_result['status'] == 'success':
                        return {"status": "blurred_preview_sent", "lead_id": lead_id, "mockup_url": blur_result['mockup_url']}
            
            # Step 3: If client shows interest, send full design
            elif status == 'replied':
                logger.info(f"→ Generating full design for {lead['business_name']}")
                design_result = self.design.generate_full_design(lead)
                return {"status": "design_generated", "lead_id": lead_id, "design_url": design_result.get('design_url')}
            
            # Step 4: Create invoice and send for payment
            elif status == 'design_ready':
                logger.info(f"→ Creating invoice for {lead['business_name']}")
                invoice_result = self.payment.create_invoice(lead, amount=50000)  # $500
                if invoice_result['status'] == 'success':
                    return {
                        "status": "invoice_sent",
                        "lead_id": lead_id,
                        "checkout_url": invoice_result['checkout_url']
                    }
            
            # Step 5: When payment received, start project
            elif status == 'paid':
                logger.info(f"→ Starting project for {lead['business_name']}")
                project_result = self.success.start_project(lead_id)
                return {"status": "project_started", "lead_id": lead_id}
            
            return {"status": "waiting", "lead_id": lead_id}
        
        except Exception as e:
            logger.error(f"Failed to process lead {lead_id}: {str(e)}")
            return {"status": "error", "lead_id": lead_id, "error": str(e)}
    
    async def run_pipeline(self):
        """Run the entire pipeline (check all leads for next action)"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            leads = data.get('leads', [])
            
            # Process all leads
            for lead in leads:
                result = await self.process_lead(lead['id'])
                logger.info(f"Result: {json.dumps(result)}")
                
                # Add small delay between leads to avoid rate limits
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
    
    def get_funnel_stats(self) -> Dict:
        """Return funnel analytics"""
        try:
            with open(self.leads_file, 'r') as f:
                data = json.load(f)
            
            leads = data.get('leads', [])
            
            stats = {
                'total_leads': len(leads),
                'by_status': {},
                'conversion_rates': {}
            }
            
            # Count by status
            for status in ['found', 'cold_sent', 'replied', 'design_ready', 'invoice_sent', 'paid', 'design_in_progress', 'design_delivered']:
                count = len([l for l in leads if l['status'] == status])
                stats['by_status'][status] = count
            
            # Conversion rates
            if stats['total_leads'] > 0:
                stats['conversion_rates'] = {
                    'cold_to_replied': f"{(stats['by_status'].get('replied', 0) / max(stats['by_status'].get('cold_sent', 1), 1) * 100):.1f}%",
                    'replied_to_paid': f"{(stats['by_status'].get('paid', 0) / max(stats['by_status'].get('replied', 1), 1) * 100):.1f}%",
                    'overall': f"{(stats['by_status'].get('paid', 0) / stats['total_leads'] * 100):.1f}%"
                }
            
            return stats
        
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": str(e)}


async def main():
    """Example usage"""
    orchestrator = AgencyOrchestrator()
    
    # Print funnel stats
    stats = orchestrator.get_funnel_stats()
    print("=== Funnel Stats ===")
    print(json.dumps(stats, indent=2))
    
    # Run pipeline
    print("\n=== Running Pipeline ===")
    await orchestrator.run_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
