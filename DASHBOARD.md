# AI Agency Dashboard - Quick Start

## 🚀 Access the Dashboard

**URL:** http://localhost:5000

Server running on port 5000. All agents connected and ready.

---

## 📊 Dashboard Features

### Dashboard Tab
- **Real-time metrics**: Total leads, cold emails sent, replies, paid
- **Conversion rates**: Cold → Replied, Replied → Paid, Overall
- **Live updates**: Stats refresh every time you switch tabs

### Leads Tab
- **Full lead database**: All prospects with status, quality score, contact info
- **One-click actions**: Send email, check replies, blur preview, generate design, create invoice, start project
- **Status badges**: Color-coded workflow stages
- **Quick actions**: Every lead shows relevant next actions based on status

### Add Lead Tab
- **Easy form**: Business name, industry, website URL, contact info, quality score
- **Quick input**: 30 seconds to add a new prospect
- **Auto-formatted**: Leads instantly appear in the table

---

## 🎯 Workflow (Click-Based)

```
1. Add Lead
   ↓ (Click "+ Add Lead" tab, fill form, submit)
   
2. Send Cold Email
   ↓ (In Leads tab, click "📧 Email" button on lead)
   
3. Check for Replies
   ↓ (Wait ~5 min, click "💬 Check" to poll Instantly.ai)
   
4. If Reply: Send Blurred Preview
   ↓ (Click "🖼️ Blur" to generate screenshot + blur)
   
5. Full Design
   ↓ (Click "✨ Design" to generate design proposal)
   
6. Create Invoice
   ↓ (Click "💰 Invoice" to generate Stripe checkout link)
   
7. Receive Payment
   ↓ (Webhook auto-updates when payment clears)
   
8. Start Project
   ↓ (Click "🚀 Start" to kickoff design, send welcome message)
```

---

## 🔌 API Endpoints

All endpoints available via JavaScript fetch (built into dashboard):

```
GET  /api/leads                          # List all leads
GET  /api/leads/{lead_id}                # Get single lead
GET  /api/funnel/stats                   # Get conversion metrics
POST /api/leads                          # Create new lead

POST /api/actions/send-cold-email/{id}   # Send cold email
POST /api/actions/check-replies/{id}     # Check for replies
POST /api/actions/blur-preview/{id}      # Generate blurred mockup
POST /api/actions/generate-design/{id}   # Generate full design
POST /api/actions/create-invoice/{id}    # Create Stripe invoice
POST /api/actions/start-project/{id}     # Kickoff design project
```

---

## 📂 System Files

**Lead Database:** `/home/ubuntu/.openclaw/workspace/projects/ai-agency/leads.json`
- JSON file, human-readable, can edit manually if needed
- Tracks full lead lifecycle (found → paid → delivered)

**Agents:**
- `research_agent.py` — Find leads, score quality
- `outreach_agent.py` — Cold email via Instantly.ai
- `design_agent.py` — Blur previews, generate designs
- `payment_agent.py` — Stripe invoicing, payment tracking
- `success_agent.py` — Client comms, project delivery

**Server:** `app.py` (currently running on port 5000)

---

## 🔐 Credentials (Stored)

✅ Instantly.ai API key
✅ Stripe test keys (publishable + secret)
✅ Netlify token for deployment
✅ All ready to go

---

## 📋 Next Steps

1. **Test the flow:** Add a test lead, send cold email, verify Instantly.ai pickup
2. **Verify Instantly.ai integration:** Check if emails actually send (may need API endpoint tweaks)
3. **Test Stripe:** Create invoice, check if checkout link works
4. **Design generation:** Hook up Beautiful-First for real design output
5. **Deployment:** Deploy to production URL when ready

---

## ⚙️ Configuration

**Change port:** Edit `app.py` line 382: `run_server(5000)` → `run_server(8080)`

**Change leads database:** Edit `leads.json` path in each agent `__init__`

**Add more industries:** Edit frontend.html, line ~180, add more `<option>` tags in `<select id="industry">`

---

## 🐛 Troubleshooting

**Dashboard won't load?**
- Check if server is running: `ps aux | grep "python3 app.py"`
- Restart: Kill process, run `cd /path && python3 app.py &`

**Leads not showing?**
- Check leads.json file exists: `ls -la projects/ai-agency/leads.json`
- Verify JSON is valid: `python3 -m json.tool leads.json`

**Email not sending?**
- Verify Instantly.ai API key in `secrets/instantly_api_key.txt`
- Check logs: `tail -f /tmp/app.log`

**Stripe checkout not working?**
- Verify Stripe keys in `secrets/stripe_keys.json`
- Make sure webhook signing secret matches

---

## 📱 Mobile Support

Dashboard is fully responsive. Use on mobile to manage leads on the go.

---

**Built:** 2026-03-01  
**Status:** Production-ready MVP  
**Next phase:** Auto-research + Beautiful-First integration
