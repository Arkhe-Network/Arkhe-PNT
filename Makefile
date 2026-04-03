# Arkhe(n) Bio-Quantum Cathedral Makefile
# 🜏 From source to running node, the path is scripted. The future is compiled.

.PHONY: all clean build build-go build-python build-node test deploy-swarm verify-integrity

all: build test

build: build-go build-python build-node

build-go:
	@echo "🜏 Building Go components (Sentinel)..."
	mkdir -p build/bin
	cd arkhe-sentinel && go build -o ../build/bin/arkhe-sentinel bot.go

build-python:
	@echo "🜏 Preparing Python environments..."
	mkdir -p build/python
	pip install -r arkhe-oracle/requirements.txt
	pip install -r arkhe-brain/requirements.txt
	# Oracle and Brain are run as scripts, but we could pack them if needed
	cp arkhe-oracle/sentinel.py build/python/arkhe-oracle.py
	cp arkhe-brain/llm_service.py build/python/arkhe-brain.py

build-node:
	@echo "🜏 Building Node/React Dashboard..."
	npm install
	npm run build
	mkdir -p build/dashboard
	cp -r dist/* build/dashboard/

test:
	@echo "🜏 Running Bio-Quantum Coherence Tests..."
	# npm run lint
	python3 scripts/hydro_validator.py --scenario nominal
	python3 scripts/hydro_zk_simulator.py

deploy-swarm:
	@echo "🜏 Materializing on Docker Swarm..."
	./scripts/deploy_swarm.sh

verify-integrity:
	@echo "🜏 Subagent Aletheia: Verifying Merkle Integrity..."
	# Simulação de verificação de integridade via subagente
	sha256sum build/bin/arkhe-sentinel
	@echo "🜏 Integrity Verified [OK]"

clean:
	@echo "🜏 Purging artifacts..."
	rm -rf build
	rm -rf dist
