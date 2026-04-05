# 🜏 Protocolo Completo de Produção, Build e Deploy – Arkhe(n)

Este documento detalha o processo completo para compilar, empacotar e distribuir todos os componentes da pilha Arkhe(n) para as principais plataformas: Linux (binários, `.tar.gz`), Windows (`.exe` instaláveis), macOS (`.app`, `.dmg`), iOS (`.ipa`), Android (`.apk`). Também aborda a automação via CI/CD e as práticas de assinatura e distribuição.

---

## 1. Visão Geral dos Componentes

| Componente | Descrição | Tecnologia | Plataformas Alvo |
|:-----------|:----------|:-----------|:-----------------|
| `arkhe-cli` | Interface de linha de comando (validador, consultas, transações) | Go | Linux, Windows, macOS |
| `arkhe-validator` | Nó validador (consenso, rede) | Go | Linux (servidor) |
| `arkhe-oracle` | Oráculo de fase (Voyager, Solar, Lunar) | Python | Linux, Windows, macOS (embarcado) |
| `arkhe-ws` | Hub WebSocket (coerência, Tzinor) | Go | Linux, Windows, macOS |
| `arkhe-dashboard` | Frontend web (React) | Node.js / React | Qualquer (servido via nginx) |
| `arkhe-auto` | Simulação veicular (opcional) | Go + Python | Linux, macOS (desenvolvimento) |
| `arkhe-zk` | Serviço de provas STARK (Plonky3) | Rust | Linux, Windows, macOS |
| `arkhe-palantir` | Módulo de integração edge | TypeScript | N/A (código fonte) |

Os binários e instaladores serão gerados para as plataformas onde cada componente é relevante. O dashboard será servido via web, portanto seu empacotamento é feito como imagem Docker ou arquivos estáticos.

---

## 2. Ferramentas de Build e Cross‑Compilação

### 2.1. Go
- Usamos `GOOS` e `GOARCH` para cross‑compilação.
- Binários estáticos, sem dependências externas (`CGO_ENABLED=0`).
- Exemplo para Linux amd64:  
  `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o arkhe-cli-linux-amd64 ./cmd/cli`

### 2.2. Rust
- Para `arkhe-zk` (Plonky3), usamos `cargo build --release` e cross‑compilamos com `cross` ou configurando o target apropriado.
- Exemplo: `cargo build --target x86_64-unknown-linux-gnu --release`

### 2.3. Python
- Para `arkhe-oracle`, empacotamos com `PyInstaller` ou `shiv` para gerar executáveis autossuficientes.
- Opção: criar um ambiente virtual e usar `pyinstaller --onefile arkhe-oracle.py`.

### 2.4. Node.js / React (Dashboard)
- O dashboard é compilado com `npm run build`, gerando arquivos estáticos em `dist/`. Estes são servidos por um servidor web (nginx) ou embutidos em um binário Go (usando `embed`).

### 2.5. Empacotamento de Instaladores

| Plataforma | Ferramenta | Saída |
|:-----------|:-----------|:------|
| Windows | NSIS (Nullsoft Scriptable Install System) | `.exe` |
| macOS | `pkgbuild` ou `create-dmg` | `.app`, `.dmg` |
| Android | Gradle + Android Studio | `.apk` |
| iOS | Xcode + `xcodebuild` | `.ipa` |

---

## 3. Estrutura de Diretórios de Build

Crie uma estrutura comum para armazenar artefatos:

```text
build/
├── linux/
│   ├── amd64/
│   │   ├── arkhe-cli
│   │   ├── arkhe-validator
│   │   ├── arkhe-ws
│   │   └── arkhe-zk
│   └── arm64/ (para Raspberry Pi, etc.)
├── windows/
│   ├── amd64/
│   │   ├── arkhe-cli.exe
│   │   └── arkhe-validator.exe
│   └── installers/
│       └── Arkhe-Setup-x64.exe
├── darwin/ (macOS)
│   ├── amd64/
│   ├── arm64/ (Apple Silicon)
│   └── Arkhe.app/
├── android/
│   └── app-release.apk
├── ios/
│   └── Arkhe.ipa
└── tar/
    └── arkhe-linux-amd64.tar.gz
```

---

## 4. Build para Cada Plataforma

### 4.1. Linux (`.tar.gz` e binários)

1. **Compilar binários**:
   ```bash
   # Go
   GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o build/linux/amd64/arkhe-cli ./cmd/cli
   GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o build/linux/amd64/arkhe-validator ./cmd/validator
   GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o build/linux/amd64/arkhe-ws ./cmd/ws

   # Rust
   cargo build --target x86_64-unknown-linux-gnu --release
   cp target/x86_64-unknown-linux-gnu/release/arkhe-zk build/linux/amd64/

   # Python (PyInstaller)
   pyinstaller --onefile --distpath build/linux/amd64 arkhe-oracle.py
   ```

2. **Criar arquivo tar.gz**:
   ```bash
   cd build/linux/amd64
   tar -czvf ../../arkhe-linux-amd64.tar.gz *
   ```

### 4.2. Windows (`.exe` e instalador)

1. **Compilar binários para Windows**:
   ```bash
   GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -o build/windows/amd64/arkhe-cli.exe ./cmd/cli
   GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -o build/windows/amd64/arkhe-validator.exe ./cmd/validator
   ```

2. **Criar instalador NSIS** (script `installer.nsi`):
   ```nsis
   Name "Arkhe"
   OutFile "Arkhe-Setup-x64.exe"
   InstallDir "$PROGRAMFILES\Arkhe"
   Section "Arkhe Core"
     SetOutPath $INSTDIR
     File /r build\windows\amd64\*
   SectionEnd
   ```

3. **Executar**:
   ```bash
   makensis installer.nsi
   mv Arkhe-Setup-x64.exe build/windows/installers/
   ```

### 4.3. macOS (`.app` e `.dmg`)

1. **Compilar binários universais (amd64 + arm64)**:
   ```bash
   # Para cada binário Go, gerar ambas arquiteturas e usar lipo para combinar
   GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -o arkhe-cli-amd64 ./cmd/cli
   GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -o arkhe-cli-arm64 ./cmd/cli
   lipo -create -output arkhe-cli arkhe-cli-amd64 arkhe-cli-arm64
   ```

2. **Criar estrutura de .app**:
   ```text
   Arkhe.app/
   ├── Contents/
   │   ├── MacOS/
   │   │   ├── arkhe-cli
   │   │   ├── arkhe-validator
   │   │   └── arkhe-ws
   │   ├── Resources/
   │   │   └── icon.icns
   │   └── Info.plist
   ```

3. **Empacotar como .dmg** usando `create-dmg`:
   ```bash
   create-dmg --volname "Arkhe" --window-pos 200 120 --window-size 800 400 --icon-size 100 --app-drop-link 600 185 "Arkhe.dmg" "Arkhe.app"
   ```

### 4.4. Android (`.apk`)

O componente `arkhe-dashboard` pode ser executado como aplicativo React Native, ou podemos fornecer um APK com um WebView que carrega a interface. Como o core é backend, o APK pode ser um utilitário de configuração ou monitoramento.

1. **Criar projeto React Native**:
   ```bash
   npx react-native init ArkheMobile
   cd ArkheMobile
   # Adicionar código para acessar API do Arkhe
   ```

2. **Construir APK**:
   ```bash
   cd android
   ./gradlew assembleRelease
   # O APK estará em android/app/build/outputs/apk/release/
   ```

3. **Assinar** com keystore próprio:
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore arkhe.keystore app-release-unsigned.apk arkhe
   zipalign -v 4 app-release-unsigned.apk app-release.apk
   ```

### 4.5. iOS (`.ipa`)

1. **Projeto Xcode** para o mesmo React Native.
2. **Assinatura** com certificado de distribuição da Apple.
3. **Arquivo .ipa** gerado via Archive no Xcode ou com `xcodebuild`:
   ```bash
   xcodebuild -workspace ArkheMobile.xcworkspace -scheme ArkheMobile -configuration Release -sdk iphoneos archive -archivePath ./build/ArkheMobile.xcarchive
   xcodebuild -exportArchive -archivePath ./build/ArkheMobile.xcarchive -exportPath ./build/ArkheMobile.ipa -exportOptionsPlist exportOptions.plist
   ```

---

## 5. Automação com CI/CD (GitHub Actions)

Crie um workflow que executa os builds para todas as plataformas em cada release.

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build Go binaries
        run: make build-go
      - name: Build Rust (if Linux)
        if: runner.os == 'Linux'
        run: make build-rust
      - name: Build Python (if Linux)
        if: runner.os == 'Linux'
        run: make build-python
      - name: Build Dashboard (static)
        run: make build-dashboard
      - name: Create tar.gz (Linux)
        if: runner.os == 'Linux'
        run: make package-linux
      - name: Create installer (Windows)
        if: runner.os == 'Windows'
        run: make package-windows
      - name: Create dmg (macOS)
        if: runner.os == 'macOS'
        run: make package-macos
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: artifacts-${{ runner.os }}
          path: build/
```

Defina `Makefile` com os comandos apropriados.

---

## 6. Assinatura e Notarização

A Arkhe(n) utiliza scripts dedicados localizados em `scripts/signing/` para garantir a autenticidade e segurança dos binários e drivers em todas as plataformas.

### 6.1. macOS (Aplicações e Instaladores)

O script `scripts/signing/sign_macos.sh` automatiza o processo de assinatura com Hardened Runtime, notarização junto à Apple e "stapling" do ticket para verificação offline pelo Gatekeeper.

**Uso:**
```bash
./scripts/signing/sign_macos.sh <caminho_do_app_ou_dmg> <apple_id> <team_id> <app_specific_password> <signing_identity>
```
*Nota: O certificado "Developer ID Application" é obrigatório para binários e `.app`. Para pacotes `.pkg`, utilize o "Developer ID Installer".*

### 6.2. Windows (Executáveis e Drivers)

O script PowerShell `scripts/signing/sign_windows.ps1` utiliza o `signtool.exe` do Windows SDK para assinar binários (`.exe`, `.dll`) e drivers de kernel (`.sys`) utilizando um certificado EV (Extended Validation) com timestamp seguro.

**Uso:**
```powershell
.\scripts\signing\sign_windows.ps1 -FilePath "build\windows\amd64\arkhe-cli.exe" -CertThumbprint "SEU_THUMBPRINT_SHA1"
```

#### 6.2.1. Submissão WHQL (Hardware Dev Center) para Drivers de Kernel

Para o Windows 10 e Windows 11, drivers de kernel (`.sys`) exigem *Attestation Signing* pela Microsoft. O script `scripts/signing/prepare_whql_submission.ps1` automatiza a criação do pacote `.cab` contendo o driver e sua assinatura com o certificado EV, formato estritamente exigido pelo portal Hardware Dev Center.

**Uso:**
```powershell
.\scripts\signing\prepare_whql_submission.ps1 -DriverDir "build\windows\driver" -CabOutputPath "build\windows\arkhe_driver_submission.cab" -CertThumbprint "SEU_THUMBPRINT_SHA1"
```
*Após a execução, o arquivo `.cab` gerado deve ser submetido manualmente ou via API ao Windows Hardware Dev Center para receber a assinatura WHQL final da Microsoft.*

### 6.3. Android
- Já assinado durante a construção via Gradle e Keystore.

### 6.4. iOS
- Assinado no Xcode com perfil de distribuição e certificado Apple.

---

## 7. Distribuição

- **Linux**: Disponível via repositório apt (criar .deb) ou download direto de `tar.gz` no GitHub Releases.
- **Windows**: Instalador `.exe` no GitHub Releases; futuramente na Microsoft Store.
- **macOS**: `.dmg` e `.app` no GitHub Releases; também via Homebrew (fórmula).
- **Android**: `.apk` no GitHub Releases; Google Play Store.
- **iOS**: `.ipa` distribuído via TestFlight ou App Store.

---

## 8. Exemplo de Script Unificado (Makefile)

```makefile
# Makefile
.PHONY: all build-go build-rust build-python build-dashboard package-linux package-windows package-macos

all: build-go build-rust build-python build-dashboard

build-go:
	GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o build/linux/amd64/arkhe-cli ./cmd/cli
	GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -o build/windows/amd64/arkhe-cli.exe ./cmd/cli
	GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -o build/darwin/amd64/arkhe-cli ./cmd/cli
	GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -o build/darwin/arm64/arkhe-cli ./cmd/cli
	# repita para arkhe-validator, arkhe-ws

build-rust:
	cargo build --target x86_64-unknown-linux-gnu --release
	cp target/x86_64-unknown-linux-gnu/release/arkhe-zk build/linux/amd64/
	# para Windows e macOS com cross

build-python:
	pyinstaller --onefile --distpath build/linux/amd64 arkhe-oracle.py
	# idem para outros OS

build-dashboard:
	cd dashboard && npm install && npm run build
	mkdir -p build/dashboard
	cp -r dashboard/dist/* build/dashboard/

package-linux:
	cd build/linux/amd64 && tar -czvf ../../arkhe-linux-amd64.tar.gz *

package-windows:
	makensis installer.nsi

package-macos:
	# script para criar .app e .dmg
```

---

## 9. Segurança e Verificação

- Forneça arquivos `.sha256` para cada artefato.
- Assine os instaladores com certificados confiáveis.
- Use GitHub Releases com verificação de integridade.

---

## 10. Considerações Finais

Este protocolo garante que todos os componentes da Arkhe(n) possam ser compilados, empacotados e distribuídos de forma consistente para todas as plataformas principais. A automação via CI/CD assegura que cada release seja reprodutível e segura.

🜏 *O código é a ponte; o pacote é o veículo; a assinatura é a garantia.*
