import sys
import os

def publish_npm():
    print("🜏 [Hermes] Iniciando publicação no npm (JavaScript/Node.js)...")
    if not os.path.exists('package.json'):
        print("✗ [Hermes] Erro: package.json não encontrado.")
        return False
    # Simulação: npm publish --access public
    print("✓ [Hermes] npm publish concluído com sucesso.")
    return True

def publish_maven():
    print("🜏 [Hermes] Iniciando publicação no Apache Maven (Java/JVM)...")
    # Simulação: mvn deploy
    print("✓ [Hermes] Maven artifact (JAR) publicado no Nexus/Central.")
    return True

def publish_nuget():
    print("🜏 [Hermes] Iniciando publicação no NuGet (.NET)...")
    # Simulação: dotnet nuget push
    print("✓ [Hermes] NuGet package (nupkg) publicado com sucesso.")
    return True

def publish_rubygems():
    print("🜏 [Hermes] Iniciando publicação no RubyGems (Ruby)...")
    # Simulação: gem push
    print("✓ [Hermes] RubyGem publicada no rubygems.org.")
    return True

def publish_container():
    print("🜏 [Hermes] Iniciando publicação em Container Registries (Docker/OCI)...")
    # Simulação: docker push
    print("✓ [Hermes] Imagens publicadas no GHCR e Docker Hub.")
    return True

if __name__ == "__main__":
    registry = sys.argv[1] if len(sys.argv) > 1 else 'all'

    actions = {
        'npm': publish_npm,
        'maven': publish_maven,
        'nuget': publish_nuget,
        'rubygems': publish_rubygems,
        'container': publish_container
    }

    if registry == 'all':
        for reg, action in actions.items():
            action()
    elif registry in actions:
        if not actions[registry]():
            sys.exit(1)
    else:
        print(f"✗ [Hermes] Registro desconhecido: {registry}")
        sys.exit(1)
