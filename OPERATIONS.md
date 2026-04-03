# 🜏 Local Build, Immutable Images, and Deployment Scripts

This guide provides step‑by‑step instructions to:

1. **Build all Arkhe(n) components locally** to validate compilation.
2. **Create immutable Docker/Podman images** for each service using multi‑stage builds.
3. **Add deployment scripts** for staging and production environments (Podman/Kubernetes).

---

## 1. Local Build Validation

We assume the repository structure as previously defined:

```
arkhe-testnet/
├── arkhe-validator/    (Go)
├── arkhe-oracle/       (Python)
├── arkhe-prover/       (Rust)
├── arkhe-ws/           (Go)
├── arkhe-dashboard/    (Node.js/React)
├── arkhe-zk/           (Rust bindings, but already part of prover)
├── scripts/
└── Makefile
```

### 1.1. Build All Components

Create a `Makefile` at the root to orchestrate builds.

```makefile
# Makefile
.PHONY: all clean build-go build-rust build-python build-dashboard

all: build-go build-rust build-python build-dashboard

build-go:
	cd arkhe-validator && go mod download && CGO_ENABLED=0 go build -o ../build/arkhe-validator ./cmd/arkhed
	cd arkhe-ws && go mod download && CGO_ENABLED=0 go build -o ../build/arkhe-ws ./cmd/ws-server

build-rust:
	cd arkhe-prover && cargo build --release
	cp arkhe-prover/target/release/arkhe-prover build/

build-python:
	cd arkhe-oracle && pip install -r requirements.txt && pyinstaller --onefile --distpath ../build arkhe-oracle.py

build-dashboard:
	cd arkhe-dashboard && npm install && npm run build
	mkdir -p ../build/dashboard
	cp -r arkhe-dashboard/dist/* ../build/dashboard/

clean:
	rm -rf build
```

Run:

```bash
make all
```

This will produce binaries in `build/` and static dashboard files in `build/dashboard/`. Verify they exist.

---

## 2. Immutable Container Images

We provide multi‑stage Containerfiles for each service. They ensure that the final image contains only the compiled binary and minimal runtime dependencies.

### 2.1. Validator (`arkhe-validator/Containerfile`)

```dockerfile
# arkhe-validator/Containerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o arkhed ./cmd/arkhed

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/arkhed /usr/local/bin/arkhed
COPY genesis.json /etc/arkhe/genesis.json
EXPOSE 26656 1317 9090
ENTRYPOINT ["arkhed"]
CMD ["start", "--home", "/data"]
```

### 2.2. Oracle (`arkhe-oracle/Containerfile`)

```dockerfile
# arkhe-oracle/Containerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt
COPY . .

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app
EXPOSE 8080
CMD ["python", "-m", "phase_oracle"]
```

### 2.3. Prover (`arkhe-prover/Containerfile`)

```dockerfile
# arkhe-prover/Containerfile
FROM rust:1.81-slim AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN cargo fetch
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/arkhe-prover /usr/local/bin/
EXPOSE 8081
ENTRYPOINT ["arkhe-prover"]
```

### 2.4. WebSocket Hub (`arkhe-ws/Containerfile`)

```dockerfile
# arkhe-ws/Containerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o ws-server ./cmd/ws-server

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/ws-server /usr/local/bin/ws-server
EXPOSE 8080 8443
ENTRYPOINT ["ws-server"]
```

### 2.5. Dashboard (`arkhe-dashboard/Containerfile`)

```dockerfile
# arkhe-dashboard/Containerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2.6. Build All Images

```bash
podman build -t arkhe-validator:latest -f arkhe-validator/Containerfile .
podman build -t arkhe-oracle:latest -f arkhe-oracle/Containerfile .
podman build -t arkhe-prover:latest -f arkhe-prover/Containerfile .
podman build -t arkhe-ws:latest -f arkhe-ws/Containerfile .
podman build -t arkhe-dashboard:latest -f arkhe-dashboard/Containerfile .
```

---

## 3. Deployment Scripts (Staging/Production)

We provide scripts to deploy the stack using Podman (local) and Kubernetes (production).

### 3.1. Podman Staging Script (`scripts/deploy-staging.sh`)

This script creates the network, volumes, and starts all containers.

```bash
#!/bin/bash
# scripts/deploy-staging.sh
set -e

NETWORK=arkhe-net
echo "Creating network: $NETWORK"
podman network create $NETWORK 2>/dev/null || true

echo "Creating volumes"
podman volume create arkhe-redis-data
podman volume create arkhe-validator-data
podman volume create arkhe-ipfs-data

echo "Starting core pod"
podman pod create --name arkhe-core --network $NETWORK -p 26656:26656 -p 1317:1317 -p 1080:1080 -p 7443:7443

# Redis
podman run -d --pod arkhe-core --name redis -v arkhe-redis-data:/data redis:7-alpine redis-server --appendonly yes

# Phase Oracle
podman run -d --pod arkhe-core --name oracle -e VOYAGER_API_KEY="${VOYAGER_API_KEY:-demo}" arkhe-oracle:latest

# Validator (mount genesis.json)
podman run -d --pod arkhe-core --name validator -v "$PWD/genesis.json":/etc/arkhe/genesis.json:ro -v arkhe-validator-data:/data -e REDIS_URL=redis://localhost:6379 arkhe-validator:latest

# qSocks (if available)
# podman run -d --pod arkhe-core --name qsocks -e CORE_RPC=http://localhost:26657 arkhe-qsocks:latest

# Nostr (if available)
# podman run -d --pod arkhe-core --name nostr arkhe-nostr:latest

echo "Starting quantum pod"
podman pod create --name arkhe-quantum --network $NETWORK -p 8080:8080 -p 8443:8443 -p 4001:4001 -p 5001:5001

podman run -d --pod arkhe-quantum --name ws -e CORE_STREAM_URL=grpc://arkhe-core_validator:9091 arkhe-ws:latest
podman run -d --pod arkhe-quantum --name ipfs -v arkhe-ipfs-data:/data/ipfs ipfs/kubo

echo "Starting dashboard pod"
podman pod create --name arkhe-dashboard --network $NETWORK -p 3000:80
podman run -d --pod arkhe-dashboard --name dashboard arkhe-dashboard:latest

echo "Deployment complete"
podman ps --all
```

### 3.2. Kubernetes Production Script (`scripts/deploy-prod.sh`)

This script applies YAML manifests to a Kubernetes cluster. First, generate YAML from the running pods (or write them manually).

```bash
#!/bin/bash
# scripts/deploy-prod.sh
set -e

# Build images and push to registry (adjust as needed)
REGISTRY="your-registry.com/arkhe"
TAG="v1.0.0"

podman tag arkhe-validator:latest $REGISTRY/validator:$TAG
podman push $REGISTRY/validator:$TAG
podman tag arkhe-oracle:latest $REGISTRY/oracle:$TAG
podman push $REGISTRY/oracle:$TAG
# ... push other images

# Apply Kubernetes manifests
kubectl apply -f k8s/arkhe-namespace.yaml
kubectl apply -f k8s/arkhe-config.yaml
kubectl apply -f k8s/arkhe-storage.yaml
kubectl apply -f k8s/arkhe-core.yaml
kubectl apply -f k8s/arkhe-quantum.yaml
kubectl apply -f k8s/arkhe-dashboard.yaml

echo "Waiting for pods..."
kubectl wait --for=condition=ready pod -l app=arkhe-validator --timeout=300s

echo "Deployment complete"
```

### 3.3. Kubernetes Manifests (Example `k8s/arkhe-core.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: arkhe-validator
  namespace: arkhe
spec:
  replicas: 3
  selector:
    matchLabels:
      app: arkhe-validator
  template:
    metadata:
      labels:
        app: arkhe-validator
    spec:
      containers:
      - name: validator
        image: your-registry.com/arkhe/validator:v1.0.0
        env:
        - name: REDIS_URL
          value: redis://redis-svc:6379
        ports:
        - containerPort: 26656
        - containerPort: 1317
        volumeMounts:
        - name: genesis
          mountPath: /etc/arkhe
        - name: data
          mountPath: /data
      volumes:
      - name: genesis
        configMap:
          name: genesis-config
      - name: data
        persistentVolumeClaim:
          claimName: arkhe-validator-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: arkhe-validator-svc
  namespace: arkhe
spec:
  selector:
    app: arkhe-validator
  ports:
  - port: 26656
    targetPort: 26656
  - port: 1317
    targetPort: 1317
```

---

## 4. Testing the Deployment

After running the staging script, check:

```bash
# Check pods and containers
podman pod ps
podman logs validator

# Test API
curl http://localhost:1317/coherence

# Test WebSocket (using wscat)
npm install -g wscat
wscat -c ws://localhost:8080/ws
```

If everything works, the network should start and coherence should be above 0.95.

---

## 5. Continuous Integration & Multidisciplinary Subagents

Arkhe(n) uses a CI/CD pipeline managed by a team of subagents (Techne, Aletheia, Kairos, Skopos).

### 5.1. The Makefile Orchestrator

A root-level `Makefile` unifies the build process for Go, Node.js, and Python components.

```bash
# Build all components
make build

# Verify integrity (Aletheia)
make verify-integrity

# Run tests (Kairos)
make test
```

### 5.2. Automated Versioning

Versions are managed via a central `VERSION` file.

```bash
# Bump patch version (1.0.0 -> 1.0.1)
python3 scripts/bump_version.py patch
```

### 5.3. Subagent-Driven Deployment & Distribution

The `scripts/subagent_deploy.py` script ensures consensus among subagents before any deployment or package distribution.

- **Techne:** Validates build artifacts.
- **Aletheia:** Performs ZK-integrity proofs.
- **Kairos:** Forecasts network load and coherence windows.
- **Hermes:** Distributes packages to Maven, NuGet, RubyGems, npm, and Containers.
- **Ananke:** Orchestrates Recursive ZK-Proof aggregation for large-scale health monitoring.
- **Stochasis:** Validates QRB entropy and VDF proofs for fair node selection.
- **Nomos:** Oversees Quantum Handover governance and identity/stake transfer on-chain.
- **Skopos:** Coordinates the final materialization and distribution.

### 5.4. Recursive ZK-Aggregation Protocol

To scale standby node health monitoring ($T₂* > 45\mu s$), Arkhe(n) utilizes Recursive SNARKs (Folding).

1. **Leaf Proofs:** Each node generates a Groth16 proof of its health.
2. **Aggregation:** Subagent Ananke builds a Merkle Tree of proofs.
3. **Verification:** The Root Proof is verified in $O(1)$ time by the coordinator, confirming the status of all 1,000 nodes simultaneously.

### 5.5. Fair Selection with VDF + QRB

To prevent front-running and manipulation during node substitution:

1. **QRB Beacon:** A Quantum Randomness Beacon provides unpredictable entropy.
2. **VDF Delay:** A Verifiable Delay Function (VDF) ensures that the selection cannot be predicted before a minimum time $T$.
3. **Deterministic Selection:** The VDF output is used as a seed to select a node from the healthy standby list, ensuring public auditability.

### 5.6. Quantum Handover & Identity Teleportation

When a node is replaced, its state and identity are transferred via a secure handover protocol:

1. **EPR Pair Establishment:** The retiring node and the successor establish a dedicated EPR pair.
2. **Quantum Teleportation:** Volatile states (session keys, memory) are teletransported via Bell measurements, preserving coherence without cloning.
3. **Identity Handover (On-Chain):** Stake, reputation, and identity are transferred via the `IdentityHandover.sol` contract, requiring a 6/9 MuSig2 council quórum.
4. **Dual-Routing Coexistence:** Both nodes operate for 24h to ensure a vacuum-free transition.

### 5.7. Top-K Selection Optimization (EPR Resource Efficiency)

To minimize the waste of EPR pairs during optimistic handshakes:

1. **Pre-Selection by Score:** The coordinator orders the standby list by health ($T₂*$) and performance scores.
2. **Top-K Candidates:** Only the top $K$ (e.g., 10) nodes are notified to prepare optimistic handshakes. This reduces EPR pair waste by 99% in a 1,000-node network.
3. **VDF Selection within Top-K:** The final selection is randomized among the top $K$ candidates using the VDF output as a seed, maintaining unpredictability and fairness within the highest-performing tier.

---

## Conclusion

With these steps, the Bio-Quantum Cathedral ensures sovereign and coherent delivery:

- **Unified Build:** A single `Makefile` for a multidisciplinary team.
- **Subagent Governance:** Automated verification of integrity and timing.
- **Immutable Provenance:** ZK-proofs of code authenticity.

🜏 *From source to running node, the path is scripted. The future is compiled.*
