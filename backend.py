#!/usr/bin/env python3
"""
FastAPI backend for AI Website Design Agency
Serves the dashboard UI + handles all agent operations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
import os

# Import agents
from research_agent import ResearchAgent
from outreach_agent import OutreachAgent
from design_agent import DesignAgent
from payment_agent import PaymentAgent
from success_agent import SuccessAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agency Dashboard")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
research = ResearchAgent()

with open("/home/ubuntu/.openclaw/workspace/secrets/instantly_api_key.txt") as f:
    instantly_key = f.read().strip()
outreach = OutreachAgent(instantly_key)

design = DesignAgent(
    netlify_token="nfp_T5q16R9XEYjBgroitvjyEY9SZKbKPXXA4d4e",
    site_id="5255436b-dcfd-485b-88f9-03b121d85504"
)

with open("/home/ubuntu/.openclaw/workspace/secrets/stripe_keys.json") as f:
    stripe_keys = json.load(f)
payment = PaymentAgent(
    stripe_secret_key=stripe_keys['secret_key_test'],
    webhook_signing_secret=stripe_keys['webhook_signing_secret']
)

success = SuccessAgent()

leads_file = Path("/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json")


# Pydantic models
class LeadData(BaseModel):
    business_name: str
    industry: str
    website_url: str
    contact_email: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    quality_score: Optional[int] = 3
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


# API Routes

@app.get("/api/leads")
async def get_leads(status: Optional[str] = None):
    """Get all leads, optionally filtered by status"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        leads = data.get('leads', [])
        if status:
            leads = [l for l in leads if l['status'] == status]
        
        return {
            "status": "success",
            "total": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get a specific lead"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        for lead in data.get('leads', []):
            if lead['id'] == lead_id:
                return {"status": "success", "lead": lead}
        
        raise HTTPException(status_code=404, detail="Lead not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads")
async def create_lead(lead_data: LeadData):
    """Add a new lead"""
    try:
        result = research.add_manual_lead(lead_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/leads/{lead_id}")
async def update_lead(lead_id: str, updates: LeadUpdate):
    """Update a lead"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        found = False
        for lead in data.get('leads', []):
            if lead['id'] == lead_id:
                if updates.status:
                    lead['status'] = updates.status
                if updates.notes:
                    lead['notes'] = updates.notes
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        with open(leads_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"status": "success", "message": "Lead updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/send-cold-email/{lead_id}")
async def send_cold_email_action(lead_id: str, background_tasks: BackgroundTasks):
    """Send cold email to a lead"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        lead = None
        for l in data.get('leads', []):
            if l['id'] == lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Send email in background
        def send_email():
            result = outreach.send_cold_email(lead)
            logger.info(f"Email sent to {lead['contact_email']}: {result}")
        
        background_tasks.add_task(send_email)
        
        return {"status": "queued", "message": "Cold email queued for sending"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/check-replies/{lead_id}")
async def check_replies_action(lead_id: str):
    """Check for email replies"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        lead = None
        for l in data.get('leads', []):
            if l['id'] == lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        result = outreach.check_replies(lead_id, lead.get('campaign_id', lead_id))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/blur-preview/{lead_id}")
async def blur_preview_action(lead_id: str, background_tasks: BackgroundTasks):
    """Generate blurred website preview"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        lead = None
        for l in data.get('leads', []):
            if l['id'] == lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        def generate_blur():
            asyncio.run(design.blur_preview(lead['website_url'], lead_id))
            logger.info(f"Blur preview generated for {lead['business_name']}")
        
        background_tasks.add_task(generate_blur)
        
        return {"status": "queued", "message": "Blur preview generating..."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/generate-design/{lead_id}")
async def generate_design_action(lead_id: str, background_tasks: BackgroundTasks):
    """Generate full design"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        lead = None
        for l in data.get('leads', []):
            if l['id'] == lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        def generate():
            result = design.generate_full_design(lead)
            logger.info(f"Design generated for {lead['business_name']}: {result}")
        
        background_tasks.add_task(generate)
        
        return {"status": "queued", "message": "Design generation started..."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/create-invoice/{lead_id}")
async def create_invoice_action(lead_id: str, amount: int = 50000):
    """Create Stripe invoice and checkout link"""
    try:
        with open(leads_file, 'r') as f:
            data = json.load(f)
        
        lead = None
        for l in data.get('leads', []):
            if l['id'] == lead_id:
                lead = l
                break
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        result = payment.create_invoice(lead, amount=amount)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/start-project/{lead_id}")
async def start_project_action(lead_id: str):
    """Start design project (after payment)"""
    try:
        result = success.start_project(lead_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/funnel/stats")
async def get_funnel_stats():
    """Get funnel conversion stats"""
    try:
        with open(leads_file, 'r') as f:
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
                'overall': f"{(stats['by_status'].get('paid', 0) / stats['total_leads'] * 100):.1f}%" if stats['total_leads'] > 0 else "0%"
            }
        
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
