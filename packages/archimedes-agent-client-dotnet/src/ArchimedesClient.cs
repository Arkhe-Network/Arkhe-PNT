using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using RestSharp;

namespace Arkhe.ArchimedesAgent
{
    public class ArchimedesClient
    {
        private readonly RestClient _client;

        public ArchimedesClient(string baseUrl)
        {
            _client = new RestClient(baseUrl);
        }

        public async Task<Dictionary<string, object>> AnalyzeAsync(Dictionary<string, object> request)
        {
            var restRequest = new RestRequest("/analyze", Method.Post);
            restRequest.AddJsonBody(request);

            var response = await _client.ExecuteAsync(restRequest);
            if (!response.IsSuccessful)
            {
                throw new HttpRequestException($"Unexpected response: {response.StatusCode}");
            }

            return JsonConvert.DeserializeObject<Dictionary<string, object>>(response.Content);
        }
    }
}
