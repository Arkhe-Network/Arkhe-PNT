const https = require('https');
https.get('https://raw.githubusercontent.com/score-technologies/score-vision/main/README.md', (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', async () => {
    const { logger } = await import('../../server/logger.ts');
    logger.info(data);
  });
});
