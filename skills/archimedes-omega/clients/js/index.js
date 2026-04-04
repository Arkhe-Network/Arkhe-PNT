// index.js
const axios = require('axios');

class ArchimedesClient {
  constructor(baseURL = 'http://localhost:8080') {
    this.client = axios.create({ baseURL });
  }

  async analyze() {
    const response = await this.client.post('/analyze');
    return response.data;
  }

  async simulateSU2(request) {
    const response = await this.client.post('/simulate/su2', request);
    return response.data;
  }
}

module.exports = { ArchimedesClient };
