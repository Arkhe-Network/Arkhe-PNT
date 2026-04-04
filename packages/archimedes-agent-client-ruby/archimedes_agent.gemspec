Gem::Specification.new do |s|
  s.name        = 'archimedes_agent'
  s.version     = '1.0.0'
  s.summary     = 'Ruby client for Archimedes-Ω coherence agent'
  s.description = 'A Ruby wrapper for the Archimedes-Ω REST service.'
  s.authors     = ['Arkhe Consortium']
  s.email       = 'opensource@arkhe.network'
  s.homepage    = 'https://github.com/Arkhe-Network/Arkhe-PNT'
  s.license     = 'MIT'
  s.files       = Dir.glob('lib/**/*.rb')
  s.require_paths = ['lib']
  s.add_runtime_dependency 'httparty', '~> 0.21'
end
