// In-memory lead storage
let leads = [
  { id: 'lead_001', business_name: 'ABC Plumbing Services', industry: 'plumbing', website_url: 'https://abc-plumbing.com', contact_email: 'owner@abc-plumbing.com', quality_score: 2, status: 'found' },
  { id: 'lead_002', business_name: 'Smith HVAC', industry: 'hvac', website_url: 'https://smith-hvac.net', contact_email: 'info@smith-hvac.net', quality_score: 3, status: 'found' },
  { id: 'lead_003', business_name: 'Green Landscaping', industry: 'landscaping', website_url: 'https://greenlandscape.biz', contact_email: 'green@greenlandscape.biz', quality_score: 4, status: 'found' }
];

exports.handler = async (event) => {
  return {
    statusCode: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      leads: leads,
      stats: {
        total: leads.length,
        cold_sent: leads.filter(l => l.status === 'cold_sent').length,
        replied: leads.filter(l => l.status === 'replied').length,
        paid: leads.filter(l => l.status === 'paid').length
      }
    })
  };
};
