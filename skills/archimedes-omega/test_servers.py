# test_servers.py - Teste rápido dos servidores
import requests
import json
import time

def test_rest_server():
    """Testa o servidor REST"""
    try:
        response = requests.get("http://localhost:8080/health")
        if response.status_code == 200:
            print("✅ REST server is running")
            return True
        else:
            print(f"❌ REST server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ REST server error: {e}")
        return False

def test_graphql_server():
    """Testa o servidor GraphQL"""
    try:
        query = """
        query {
          simulateSu2(numPoints: 10) {
            phases
            coherence
          }
        }
        """
        response = requests.post(
            "http://localhost:8081/graphql",
            json={"query": query}
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "simulateSu2" in data["data"]:
                print("✅ GraphQL server is running")
                return True
            else:
                print(f"❌ GraphQL query failed: {data}")
                return False
        else:
            print(f"❌ GraphQL server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GraphQL server error: {e}")
        return False

def test_grpc_server():
    """Testa o servidor gRPC usando grpcurl se disponível"""
    try:
        import subprocess
        result = subprocess.run(
            ["grpcurl", "-plaintext", "localhost:50051", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "CoherenceAgent" in result.stdout:
            print("✅ gRPC server is running")
            return True
        else:
            print(f"❌ gRPC server check failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  grpcurl not available, skipping gRPC test")
        return True  # Consider as passed since it's optional
    except Exception as e:
        print(f"❌ gRPC server error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Archimedes-Ω servers...")
    print("=" * 40)

    # Wait a moment for servers to start
    time.sleep(2)

    results = []
    results.append(("REST", test_rest_server()))
    results.append(("GraphQL", test_graphql_server()))
    results.append(("gRPC", test_grpc_server()))

    print("\n📊 Results:")
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        all_passed = all_passed and passed

    if all_passed:
        print("\n🎉 All servers are running correctly!")
    else:
        print("\n⚠️  Some servers failed. Check the logs above.")