# 🔐 Code Signing for macOS and Driver Signing for Windows – Arkhe(n) Production Guide

A segurança da cadeia de suprimentos de software é o último elo entre o código confiável e o usuário seguro. Sem assinatura de código, o sistema operacional trata o software como um arquivo hostil. Para a Arkhe(n), onde a integridade do binário é prova de coerência, a assinatura não é opcional — é parte do consenso.

Abaixo, apresento a implementação completa de **Assinatura de Código (Code Signing)** para macOS e Windows, integrada ao pipeline de CI/CD.

---

## 🜏 I. Visão Geral da Segurança de Assinatura

| Plataforma | Requisito | Ferramenta | Tipo de Certificado |
|:-----------|:----------|:-----------|:--------------------|
| **macOS** | Apple Developer ID | `codesign`, `notarytool` | Developer ID Application |
| **Windows** | Authenticode | `SignTool` (Windows SDK) | Code Signing Certificate (OV/EV) |

---

## 🜏 II. Assinatura macOS: Aplicativos e Instaladores

O processo em macOS envolve três etapas: **Assinar** o app, **Notarizar** com a Apple, e **Grampear** (Staple) o ticket.

### 1. Pré-requisitos
- Conta Apple Developer.
- Certificado "Developer ID Application" instalado no Keychain.
- Senha específica de app (App-specific password) para notarização.

### 2. Script de Assinatura (`scripts/sign_macos.sh`)

```bash
#!/bin/bash
set -e

# Configurações
APP_NAME="Arkhe.app"
DMG_NAME="Arkhe.dmg"
SIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
APPLE_ID="your-email@example.com"
TEAM_ID="YOUR_TEAM_ID"
APP_PASSWORD="@keychain:AC_PASSWORD" # Referência ao keychain

echo "🜏 Iniciando assinatura macOS..."

# 1. Assinar Binários Internos (Executáveis dentro do .app)
# Isso é crítico: todos os executáveis devem ser assinados antes do bundle.
find "$APP_NAME/Contents/MacOS" -type f -exec codesign --force --sign "$SIGN_IDENTITY" --timestamp --options runtime {} \;

# 2. Assinar o Bundle do Aplicativo (.app)
# --options runtime habilita o Hardened Runtime (exigido para notarização)
# --timestamp garante que a assinatura será válida mesmo após o certificado expirar
codesign --force --sign "$SIGN_IDENTITY" --timestamp --options runtime --deep --entitlements entitlements.plist "$APP_NAME"

echo "✓ Aplicativo assinado."

# 3. Verificar Assinatura
codesign --verify --deep --strict --verbose=2 "$APP_NAME"
spctl --assess --verbose=4 --type execute "$APP_NAME"

# 4. Criar DMG (se não existir)
if [ ! -f "$DMG_NAME" ]; then
    hdiutil create -volname "Arkhe" -srcfolder "$APP_NAME" -ov -format UDZO "$DMG_NAME"
fi

# 5. Assinar o DMG
codesign --force --sign "$SIGN_IDENTITY" --timestamp "$DMG_NAME"
echo "✓ Instalador DMG assinado."

# 6. Notarização (Envio para Apple)
echo "🜏 Enviando para notarização..."
SUBMIT_OUTPUT=$(xcrun notarytool submit "$DMG_NAME" --apple-id "$APPLE_ID" --team-id "$TEAM_ID" --password "$APP_PASSWORD" --wait 2>&1)

# Capturar o ID da submissão
SUBMIT_ID=$(echo "$SUBMIT_OUTPUT" | grep "id:" | awk '{print $2}')
echo "   ID da submissão: $SUBMIT_ID"

# Verificar status (o --wait bloqueia até terminar)
if echo "$SUBMIT_OUTPUT" | grep "status: Accepted"; then
    echo "✓ Notarização aprovada!"
    
    # 7. Grampear (Staple) o ticket ao DMG
    xcrun stapler staple "$DMG_NAME"
    echo "✓ Ticket grampeado ao DMG."
else
    echo "✗ Notarização falhou."
    # Log detalhado em caso de falha
    xcrun notarytool log $SUBMIT_ID --apple-id "$APPLE_ID" --team-id "$TEAM_ID" --password "$APP_PASSWORD"
    exit 1
fi

echo "🜏 Processo macOS concluído com sucesso."
```

### 3. Arquivo de Entitlements (`entitlements.plist`)

Necessário para permitir que o aplicativo execute tarefas específicas sem violar o Hardened Runtime.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <false/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

---

## 🜏 III. Assinatura Windows: Executáveis e Drivers

No Windows, usamos o **Authenticode**. Para drivers (kernel-mode), o requisito é mais rigoroso (WHQL), mas para aplicativos de usuário (como o nó validador), a assinatura padrão é suficiente.

### 1. Pré-requisitos
- Certificado de Assinatura de Código (arquivo `.pfx` ou token USB/HSM).
- Windows SDK instalado (contém `SignTool`).

### 2. Script de Assinatura (`scripts/sign_windows.ps1`)

Este script PowerShell assina todos os executáveis e cria o instalador assinado.

```powershell
# Configurações
$CertPath = "C:\path\to\code_signing.pfx"
$CertPassword = $env:CODE_SIGN_PASSWORD # Segredo do CI/CD
$TimestampServer = "http://timestamp.digicert.com"
$Binaries = @("build\windows\amd64\arkhe-cli.exe", "build\windows\amd64\arkhe-validator.exe")

Write-Host "🜏 Iniciando assinatura Windows..."

# 1. Instalar Certificado (temporário para a sessão)
$Cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($CertPath, $CertPassword)

# 2. Assinar cada binário
foreach ($Binary in $Binaries) {
    if (Test-Path $Binary) {
        Write-Host "   Assinando $Binary..."
        & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
            /fd SHA256 `
            /sha1 $Cert.Thumbprint `
            /tr $TimestampServer `
            /td SHA256 `
            /v `
            $Binary
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao assinar $Binary"
            exit 1
        }
    }
}

Write-Host "✓ Binários assinados."

# 3. Verificar Assinatura
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" verify /pa /all build\windows\amd64\arkhe-validator.exe

# 4. Construir e Assinar Instalador (NSIS)
Write-Host "   Criando instalador..."
makensis installer.nsi

# 5. Assinar o Instalador Final
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
    /fd SHA256 `
    /sha1 $Cert.Thumbprint `
    /tr $TimestampServer `
    /td SHA256 `
    /v `
    "Arkhe-Setup-x64.exe"

Write-Host "✓ Instalador assinado."
Write-Host "🜏 Processo Windows concluído."
```

---

## 🜏 IV. Integração com CI/CD (GitHub Actions)

A segurança exige que as chaves privadas nunca sejam expostas. Usamos **GitHub Secrets** e **Azure Key Vault** ou **HSM** para produção.

### Workflow Atualizado (`.github/workflows/release.yml`)

```yaml
name: Release

on:
  push:
    tags: [ 'v*' ]

jobs:
  release:
    runs-on: macos-latest # Runner macOS pode assinar tanto macOS quanto Windows (via crossover ou VM)
    # Nota: Para produção real, use runners self-hosted com HSM conectado.
    
    steps:
      - uses: actions/checkout@v4

      # ... (Passos de build anteriores) ...

      # --- ASSINATURA MACOS ---
      - name: Import Apple Certificate
        env:
          CERTIFICATE_BASE64: ${{ secrets.APPLE_CERT_BASE64 }}
          CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERT_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # Criar keychain temporário
          security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          
          # Importar certificado
          echo $CERTIFICATE_BASE64 | base64 --decode > certificate.p12
          security import certificate.p12 -k build.keychain -P "$CERTIFICATE_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple: -s -k "$KEYCHAIN_PASSWORD" build.keychain

      - name: Sign macOS App
        env:
          APPLE_ID: ${{ secrets.APPLE_ID }}
          TEAM_ID: ${{ secrets.TEAM_ID }}
          APP_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
        run: |
          chmod +x scripts/sign_macos.sh
          ./scripts/sign_macos.sh

      # --- ASSINATURA WINDOWS ---
      - name: Sign Windows Executables
        # Usando um serviço de assinatura em nuvem (ex: Azure Key Vault, DigiCert ONE, SignPath)
        # Abaixo, exemplo conceitual com Azure Key Vault
        uses: azure/azure-code-signing-action@v1
        with:
          azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
          azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
          azure-key-vault-uri: ${{ secrets.AZURE_KEY_VAULT_URI }}
          azure-key-vault-certificate: ${{ secrets.AZURE_CERT_NAME }}
          files: |
            build/windows/amd64/*.exe
            build/windows/installers/*.exe

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: Arkhe-Signed-Releases
          path: |
            build/**/*.dmg
            build/**/*.exe
```

---

## 🜏 V. Verificação Final

Após o deploy, qualquer usuário pode verificar a autenticidade.

**macOS (Terminal):**
```bash
codesign --verify --deep --strict Arkhe.app
spctl --assess --verbose=4 --type execute Arkhe.app
```

**Windows (PowerShell):**
```powershell
Get-AuthenticodeSignature Arkhe-Setup-x64.exe | Format-List
# Verificar se "Status" é "Valid"
```

**Agora, a Arkhe(n) não apenas funciona; ela prova sua identidade.**

🜏 *A assinatura é o selo de coerência. Sem ela, o código é apenas ruído.*
