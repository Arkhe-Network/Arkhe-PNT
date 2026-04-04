# lib/archimedes_agent.rb
require 'httparty'
require 'json'

class ArchimedesClient
  include HTTParty

  def initialize(base_uri = 'http://localhost:8080')
    @base_uri = base_uri
  end

  def analyze
    response = self.class.post("#{@base_uri}/analyze", headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def simulate_su2(request)
    response = self.class.post("#{@base_uri}/simulate/su2", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end
end
