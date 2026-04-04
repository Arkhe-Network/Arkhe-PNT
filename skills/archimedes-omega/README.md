# Agente Archimedes-Ω - Multi-Protocol API

O **Agente Archimedes-Ω** agora suporta múltiplos protocolos de comunicação para máxima acessibilidade:

## 🚀 Servidores Disponíveis

| Protocolo | Porta | Endpoint | Descrição |
|-----------|-------|----------|-----------|
| **REST** | 8080 | `http://localhost:8080` | API RESTful com OpenAPI docs |
| **GraphQL** | 8081 | `http://localhost:8081/graphql` | Consultas flexíveis e playground |
| **gRPC** | 50051 | `localhost:50051` | Alta performance com streaming |

## 🏃‍♂️ Executando os Servidores

### Local
```bash
cd skills/archimedes-omega
pip install -r requirements.txt
python start_servers.py
```

### Docker
```bash
docker build -f Dockerfile.archimedes-agent -t archimedes-agent .
docker run -p 8080:8080 -p 8081:8081 -p 50051:50051 archimedes-agent
```

## 📚 APIs Disponíveis

### REST API (Porta 8080)
- Documentação: `http://localhost:8080/docs`
- OpenAPI Schema: `http://localhost:8080/openapi.json`

### GraphQL API (Porta 8081)
- Playground: `http://localhost:8081/graphql`
- Schema completo em `graphql_schema.graphql`

### gRPC API (Porta 50051)
- Proto file: `archimedes.proto`
- Suporte a reflection para ferramentas como `grpcurl`

## 🛠️ Clientes SDK

### Go
```bash
cd sdks/go
go mod tidy
go run client.go
```

### Rust
```bash
cd sdks/rust-archimedes
cargo build
cargo run --bin client
```

### PHP
```bash
cd sdks/php
composer install
php examples/client.php
```

## 📋 Exemplos de Uso

### GraphQL Query
```graphql
query {
  simulateSU2(theta_start: 0, theta_end: 6.28, num_points: 1000) {
    phases
    coherence
  }
  analyze(data_source: SIMULATED, su2_params: {num_points: 1000}) {
    id
    conclusion {
      status
      interpretation
    }
  }
}
```

### gRPC (Go)
```go
resp, err := client.SimulateSU2(ctx, &pb.SU2Request{
    ThetaStart: 0, ThetaEnd: 6.28318, NumPoints: 1000,
})
```

### REST API
```bash
curl -X POST "http://localhost:8080/simulate/su2" \
  -H "Content-Type: application/json" \
  -d '{"theta_start": 0, "theta_end": 6.28, "num_points": 1000}'
```

## 🔧 Desenvolvimento

### Adicionando Novos Métodos
1. Atualize `skills.py` com a lógica
2. Adicione ao `archimedes.proto`
3. Regere protobuf: `protoc --python_out=. --grpc_python_out=. archimedes.proto`
4. Atualize `graphql_server.py` e `grpc_server.py`
5. Atualize clientes SDK

### Testando
```bash
# GraphQL
curl -X POST http://localhost:8081/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { simulateSU2 { phases } }"}'

# gRPC
grpcurl -plaintext localhost:50051 list

# REST
curl http://localhost:8080/health
```

## 🌌 Filosofia

O **Agente Archimedes-Ω** transcende protocolos, oferecendo acesso universal aos mistérios da coerência quântica através de interfaces que respeitam a diversidade computacional da humanidade.

*"O universo fala todas as linguagens; devemos ouvi-lo em todas."*