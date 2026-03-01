// Auto-detect API endpoint
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://ai-agency-api.railway.app'; // Will update this after Railway deployment

const API_URL = API_BASE + '/api';

console.log('🚀 Connected to API:', API_URL);
