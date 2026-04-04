import os
import sys
import shutil
import subprocess

ROOT = os.path.abspath(os.path.dirname(__file__))

PACKAGE_PATHS = {
    'npm': os.path.join(ROOT, '..', 'packages', 'archimedes-agent-client-js'),
    'maven': os.path.join(ROOT, '..', 'packages', 'archimedes-agent-client-java'),
    'nuget': os.path.join(ROOT, '..', 'packages', 'archimedes-agent-client-dotnet'),
    'rubygems': os.path.join(ROOT, '..', 'packages', 'archimedes-agent-client-ruby'),
}


def run_command(cmd, cwd=None, env=None):
    print(f"→ Executando: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, env=env or os.environ, check=True)


def publish_npm():
    print("🜏 [Hermes] Iniciando publicação no npm (JavaScript/Node.js)...")
    package_dir = PACKAGE_PATHS['npm']
    package_json = os.path.join(package_dir, 'package.json')

    if not os.path.exists(package_json):
        print(f"✗ [Hermes] Erro: {package_json} não encontrado.")
        return False

    token = os.environ.get('NPM_TOKEN')
    if not token:
        print('✗ [Hermes] Erro: NPM_TOKEN não definido.')
        return False

    run_command(['npm', 'config', 'set', '//registry.npmjs.org/:_authToken', token])
    run_command(['npm', 'publish', '--access', 'public'], cwd=package_dir)
    print("✓ [Hermes] npm publish concluído com sucesso.")
    return True


def publish_maven():
    print("🜏 [Hermes] Iniciando publicação no Apache Maven (Java/JVM)...")
    package_dir = PACKAGE_PATHS['maven']
    pom = os.path.join(package_dir, 'pom.xml')

    if not os.path.exists(pom):
        print(f"✗ [Hermes] Erro: {pom} não encontrado.")
        return False

    run_command(['mvn', '-f', pom, 'deploy', '-DskipTests'])
    print("✓ [Hermes] Maven artifact (JAR) publicado com sucesso.")
    return True


def publish_nuget():
    print("🜏 [Hermes] Iniciando publicação no NuGet (.NET)...")
    package_dir = PACKAGE_PATHS['nuget']
    project_file = os.path.join(package_dir, 'Arkhe.ArchimedesAgent.csproj')

    if not os.path.exists(project_file):
        print(f"✗ [Hermes] Erro: {project_file} não encontrado.")
        return False

    api_key = os.environ.get('NUGET_API_KEY')
    if not api_key:
        print('✗ [Hermes] Erro: NUGET_API_KEY não definido.')
        return False

    artifacts_dir = os.path.join(package_dir, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    run_command(['dotnet', 'pack', project_file, '-c', 'Release', '-o', artifacts_dir])
    packages = [f for f in os.listdir(artifacts_dir) if f.endswith('.nupkg')]
    if not packages:
        print('✗ [Hermes] Nenhum pacote nupkg encontrado.')
        return False

    for package in packages:
        run_command([
            'dotnet', 'nuget', 'push', os.path.join(artifacts_dir, package),
            '--api-key', api_key,
            '--source', 'https://api.nuget.org/v3/index.json'
        ])

    print("✓ [Hermes] NuGet package publicado com sucesso.")
    return True


def publish_rubygems():
    print("🜏 [Hermes] Iniciando publicação no RubyGems (Ruby)...")
    package_dir = PACKAGE_PATHS['rubygems']
    gemspec = os.path.join(package_dir, 'archimedes_agent.gemspec')

    if not os.path.exists(gemspec):
        print(f"✗ [Hermes] Erro: {gemspec} não encontrado.")
        return False

    api_key = os.environ.get('RUBYGEMS_API_KEY')
    if not api_key:
        print('✗ [Hermes] Erro: RUBYGEMS_API_KEY não definido.')
        return False

    run_command(['gem', 'build', gemspec], cwd=package_dir)
    gem_files = [f for f in os.listdir(package_dir) if f.endswith('.gem')]
    if not gem_files:
        print('✗ [Hermes] Nenhum arquivo .gem foi gerado.')
        return False

    for gem_file in gem_files:
        run_command([
            'gem', 'push', os.path.join(package_dir, gem_file),
            '--api-key', api_key
        ])

    print("✓ [Hermes] RubyGem publicada com sucesso.")
    return True


def publish_container():
    print("🜏 [Hermes] Iniciando publicação em Container Registries (Docker/OCI)...")
    image = os.environ.get('DOCKER_IMAGE', 'ghcr.io/arkhe-network/archimedes-agent:latest')
    dockerfile = os.path.join(ROOT, '..', 'Dockerfile.archimedes-agent')
    context_dir = os.path.abspath(os.path.join(ROOT, '..'))
    if not os.path.exists(dockerfile):
        print(f"✗ [Hermes] Erro: {dockerfile} não encontrado.")
        return False

    run_command(['docker', 'build', '-t', image, '-f', dockerfile, '.'], cwd=context_dir)
    run_command(['docker', 'push', image])
    print("✓ [Hermes] Imagem de container publicada com sucesso.")
    return True


def main():
    registry = sys.argv[1] if len(sys.argv) > 1 else 'all'
    actions = {
        'npm': publish_npm,
        'maven': publish_maven,
        'nuget': publish_nuget,
        'rubygems': publish_rubygems,
        'container': publish_container,
    }

    if registry == 'all':
        success = True
        for name, action in actions.items():
            try:
                success &= action()
            except subprocess.CalledProcessError as exc:
                print(f"✗ [Hermes] Falha ao publicar {name}: {exc}")
                success = False
        if not success:
            sys.exit(1)
    elif registry in actions:
        if not actions[registry]():
            sys.exit(1)
    else:
        print(f"✗ [Hermes] Registro desconhecido: {registry}")
        sys.exit(1)


if __name__ == '__main__':
    main()
