# start_servers.py - Inicializa todos os servidores (REST, GraphQL, gRPC)
import threading
import time
import subprocess
import sys
import os

def start_rest_server():
    """Inicia o servidor REST (FastAPI)"""
    print("Starting REST server on port 8080...")
    try:
        from service import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    except Exception as e:
        print(f"Failed to start REST server: {e}")

def start_graphql_server():
    """Inicia o servidor GraphQL"""
    print("Starting GraphQL server on port 8081...")
    try:
        import uvicorn
        from graphql_server import app
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
    except Exception as e:
        print(f"Failed to start GraphQL server: {e}")

def start_grpc_server():
    """Inicia o servidor gRPC"""
    print("Starting gRPC server on port 50051...")
    try:
        from grpc_server import serve
        serve()
    except Exception as e:
        print(f"Failed to start gRPC server: {e}")

if __name__ == "__main__":
    print("🚀 Starting Archimedes-Ω Multi-Protocol Server")
    print("=" * 50)

    # Verificar se estamos no diretório correto
    if not os.path.exists("skills.py"):
        print("Error: Must run from skills/archimedes-omega directory")
        sys.exit(1)

    # Iniciar servidores em threads separadas
    threads = []

    # REST Server
    rest_thread = threading.Thread(target=start_rest_server, daemon=True)
    threads.append(rest_thread)

    # GraphQL Server
    graphql_thread = threading.Thread(target=start_graphql_server, daemon=True)
    threads.append(graphql_thread)

    # gRPC Server
    grpc_thread = threading.Thread(target=start_grpc_server, daemon=True)
    threads.append(grpc_thread)

    # Iniciar todas as threads
    for thread in threads:
        thread.start()
        time.sleep(1)  # Pequena pausa para evitar conflitos de porta

    print("\n✅ All servers started!")
    print("🌐 REST API:    http://localhost:8080")
    print("🔗 GraphQL:     http://localhost:8081/graphql")
    print("📡 gRPC:        localhost:50051")
    print("\nPress Ctrl+C to stop all servers")

    try:
        # Manter o programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)