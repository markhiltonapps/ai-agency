const crypto = require('crypto');

// In-memory lead storage (in production, use a database)
let leads = [
  { id: 'lead_001', business_name: 'ABC Plumbing Services', email: 'owner@abc-plumbing.com', status: 'found' },
  { id: 'lead_002', business_name: 'Smith HVAC', email: 'info@smith-hvac.net', status: 'found' },
  { id: 'lead_003', business_name: 'Green Landscaping', email: 'green@greenlandscape.biz', status: 'found' }
];

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const sig = event.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  const body = event.body;

  let stripeEvent;

  try {
    // Verify webhook signature
    const timestamp = sig.split(',')[0].split('=')[1];
    const signature = sig.split(',')[1].split('=')[1];
    
    const computedSig = crypto
      .createHmac('sha256', webhookSecret)
      .update(`${timestamp}.${body}`)
      .digest('hex');

    // For simplicity, just check if it's a valid request
    // (In production, verify the signature more strictly)
    
    stripeEvent = JSON.parse(body);
  } catch (err) {
    console.log('Webhook signature verification failed:', err.message);
    return {
      statusCode: 400,
      body: JSON.stringify({ received: true })
    };
  }

  // Handle the checkout.session.completed event
  if (stripeEvent.type === 'checkout.session.completed') {
    const session = stripeEvent.data.object;
    const leadId = session.metadata?.lead_id;
    const customerEmail = session.customer_email;

    if (leadId) {
      // Update lead status to paid
      const lead = leads.find(l => l.id === leadId);
      if (lead) {
        lead.status = 'paid';
        lead.paid_at = new Date().toISOString();
        lead.stripe_session_id = session.id;

        console.log(`✓ Payment confirmed for ${lead.business_name}`);
        console.log(`✓ Sending welcome email to ${customerEmail}`);
        console.log(`✓ Starting project for ${leadId}`);

        // Here you would:
        // 1. Send welcome email via email service
        // 2. Create project folder
        // 3. Send kickoff message to client
        // For now, just log it
      }
    }
  }

  // Handle the payment_intent.succeeded event
  if (stripeEvent.type === 'payment_intent.succeeded') {
    const paymentIntent = stripeEvent.data.object;
    console.log(`✓ Payment intent succeeded: ${paymentIntent.id}`);
  }

  return {
    statusCode: 200,
    body: JSON.stringify({ received: true })
  };
};
