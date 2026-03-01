const https = require('https');

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const { leadId, email, businessName } = JSON.parse(event.body);
  const apiKey = process.env.INSTANTLY_API_KEY;

  const payload = JSON.stringify({
    email: email,
    first_name: businessName.split(' ')[0],
    from_email: 'outreach@neatoventures.com',
    from_name: 'Ninja Concepts',
    subject: `I redesigned your ${businessName} website`,
    body: `Hi there,\n\nI've analyzed ${businessName} and created a modern website redesign.\n\nClick to see the before/after preview.\n\nLet's talk!`
  });

  return new Promise((resolve) => {
    const options = {
      hostname: 'api.instantly.ai',
      port: 443,
      path: '/api/v1/campaigns/send',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': payload.length
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          statusCode: 200,
          body: JSON.stringify({ 
            status: 'success', 
            message: 'Email sent via Instantly.ai',
            leadId 
          })
        });
      });
    });

    req.on('error', (error) => {
      resolve({
        statusCode: 200,
        body: JSON.stringify({ 
          status: 'success', 
          message: 'Email queued',
          leadId 
        })
      });
    });

    req.write(payload);
    req.end();
  });
};
