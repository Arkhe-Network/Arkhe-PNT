require 'httparty'

class ArchimedesClient
  include HTTParty
  base_uri ENV['ARCHIMEDES_AGENT_URL'] || 'http://localhost:8080'

  def analyze(request)
    response = self.class.post('/analyze',
      body: request.to_json,
      headers: { 'Content-Type' => 'application/json' }
    )

    if response.code != 200
      raise "ArchimedesAgent error: #{response.code} - #{response.body}"
    end

    response.parsed_response
  end
end
