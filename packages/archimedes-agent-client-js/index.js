const axios = require('axios');

class ArchimedesClient {
  constructor(baseURL = 'http://localhost:8080') {
    this.client = axios.create({ baseURL });
  }

  async analyze(request) {
    const response = await this.client.post('/analyze', request);
    return response.data;
  }
}

module.exports = { ArchimedesClient };
