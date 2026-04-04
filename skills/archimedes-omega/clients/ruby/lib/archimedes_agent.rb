# lib/archimedes_agent.rb
require 'httparty'
require 'json'

class ArchimedesClient
  include HTTParty

  def initialize(base_uri = 'http://localhost:8080')
    @base_uri = base_uri
  end

  def analyze(request)
    response = self.class.post("#{@base_uri}/analyze", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def simulate_su2(request)
    response = self.class.post("#{@base_uri}/simulate/su2", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def simulate_sl3z(request)
    response = self.class.post("#{@base_uri}/simulate/sl3z", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def simulate_wstate(request)
    response = self.class.post("#{@base_uri}/simulate/wstate", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def detect_peaks(request)
    response = self.class.post("#{@base_uri}/detect/peaks", body: request.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def check_teleportation_resource(phases, coherence, nodes = 3, loss_prob = 0.2)
    payload = { phases: phases, coherence: coherence, nodes: nodes, loss_probability: loss_prob }
    response = self.class.post("#{@base_uri}/analyze/teleportation-resource", body: payload.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end

  def optimize_combined_protocol(lipus, drug)
    payload = { lipus: lipus, drug: drug }
    response = self.class.post("#{@base_uri}/therapy/combined-protocol", body: payload.to_json, headers: { 'Content-Type' => 'application/json' })
    response.parsed_response
  end
end
