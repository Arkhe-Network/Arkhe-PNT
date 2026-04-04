using System;
using System.Threading.Tasks;
using RestSharp;
using Newtonsoft.Json;

namespace Arkhe.ArchimedesAgent
{
    public class ArchimedesClient
    {
        private readonly RestClient _client;
        public ArchimedesClient(string baseUrl) => _client = new RestClient(baseUrl);

        public async Task<string> AnalyzeAsync()
        {
            var req = new RestRequest("/analyze", Method.Post);
            var response = await _client.ExecuteAsync(req);
            return response.Content;
        }

        public async Task<string> SimulateSU2Async(object request)
        {
            var req = new RestRequest("/simulate/su2", Method.Post);
            req.AddJsonBody(request);
            var response = await _client.ExecuteAsync(req);
            return response.Content;
        }
    }
}
