import http from 'http';
import { logger } from './server/logger.js';

const req = http.request({
  hostname: 'localhost',
  port: 3000,
  path: '/api/x402/moltx-handshake',
  method: 'POST',
}, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => logger.info('Response: ' + data));
});

req.on('error', (e) => logger.error(e.message));
req.end();
