# 🔐 Kernel Driver Signing & WHQL Submission for Windows – Arkhe(n) Production Guide

If any component of Arkhe(n) includes a kernel‑mode driver (e.g., for hardware acceleration, custom I/O, or real‑time extensions), it must be signed with an **Extended Validation (EV) Code Signing Certificate** and pass Windows Hardware Quality Labs (WHQL) testing to be accepted by Windows Secure Boot and modern Windows versions. This guide explains the requirements, the signing process, and how to prepare for WHQL submission.

---

### 1. Why EV Certificates and WHQL?

- **Kernel‑mode drivers** must be signed by Microsoft (or a certificate in the Microsoft Root Certificate Program) to load on systems with Secure Boot enabled.
- An **EV Certificate** is required to obtain a cross‑signature from Microsoft. EV certificates are stored on hardware tokens (HSM or USB) and provide a higher level of assurance.
- **WHQL (Windows Hardware Quality Labs)** testing validates the driver’s reliability, compatibility, and security. Drivers that pass WHQL receive a Microsoft signature and can be distributed through Windows Update.

If you distribute a kernel driver without WHQL, it may only load in test‑signing mode or on systems that have disabled driver signature enforcement (not recommended for production).

---

### 2. Prerequisites

- **EV Code Signing Certificate** from an authorized CA (DigiCert, Sectigo, GlobalSign, etc.) with hardware token (USB or HSM).
- **Microsoft Partner Center account** with the **Hardware Dashboard** enabled (requires a company registration).
- **Windows Hardware Dev Center** (partner.microsoft.com) to submit drivers for WHQL.
- A **Windows Driver Kit (WDK)** installed on your build machine to compile, sign, and test drivers.

---

### 3. Signing the Driver with an EV Certificate

#### 3.1. Prepare the Driver

- Build your `.sys` file using the WDK with **Release** configuration, and ensure it is compiled for the target architecture (x64, ARM64, etc.).
- Use **Inf2Cat** to create a catalog file (`.cat`). This step validates the driver’s INF file.

```cmd
Inf2Cat /driver:C:\path\to\driver /os:10_xxxx
```

#### 3.2. Sign the Catalog and the Driver

Use `signtool` with the EV certificate from the hardware token.

```cmd
:: Sign the catalog file
signtool sign /fd SHA256 /ph /ac "Microsoft Cross-Signing.cer" /sha1 <thumbprint> /tr http://timestamp.digicert.com /td SHA256 /v mydriver.cat

:: Sign the driver binary itself
signtool sign /fd SHA256 /ph /ac "Microsoft Cross-Signing.cer" /sha1 <thumbprint> /tr http://timestamp.digicert.com /td SHA256 /v mydriver.sys
```

- `/ph`: page hash – required for kernel drivers.
- `/ac`: specify the Microsoft cross‑signing certificate (you can obtain the latest from Microsoft).

**Important**: The cross‑signing certificate file (`.cer`) must be downloaded from Microsoft (search for “Microsoft Cross-Certificates for Kernel Mode Code Signing”).

#### 3.3. Verify the Signature

```cmd
signtool verify /pa /v mydriver.sys
signtool verify /pa /v mydriver.cat
```

The output should confirm the signature chain includes Microsoft’s cross‑signature.

---

### 4. WHQL Submission Process

To obtain a Microsoft signature and enable automatic distribution, you must submit your driver through the **Windows Hardware Dev Center**.

#### 4.1. Prepare Submission Package

- Create a **submission package** (`.cab`) containing:
  - The signed `.sys` file
  - The signed `.cat` file
  - The INF file
  - Any other driver files (e.g., `.dll`, `.exe` if needed)
- Use the **Windows HLK (Hardware Lab Kit)** to test the driver on reference systems. HLK tests ensure compatibility with various hardware configurations.

#### 4.2. Submit to Hardware Dev Center

1. Log into [partner.microsoft.com](https://partner.microsoft.com) → **Hardware** → **Create new submission**.
2. Upload your driver package (`.cab`) and provide metadata.
3. Wait for the automated and manual review (may take days to weeks). If the driver passes, you will receive a **Microsoft signature** embedded in the package.
4. After approval, you can distribute the driver via Windows Update or include it in your installer.

**Note**: WHQL testing is mandatory for drivers that will be distributed through Windows Update or that need to load on Secure Boot systems.

---

### 5. Continuous Integration Integration

For CI/CD, you can automate the signing process, but the EV certificate hardware token requires a physical presence. However, you can use an **HSM** or **Azure Key Vault** with a hardware security module to perform remote signing.

- **Azure Key Vault** (with HSM) allows you to store EV certificates and sign code remotely via REST API.
- Use tools like `AzureSignTool` to integrate with your CI pipeline.

Example with `AzureSignTool`:

```powershell
AzureSignTool sign -kvu "https://myvault.vault.azure.net" -kvi "mycert" -kvt "mytenant" -kvs "mysecret" -tr "http://timestamp.digicert.com" -v "driver.sys"
```

---

### 6. Handling WHQL Submission in CI

You can automate the HLK testing and submission using Azure Pipelines with dedicated HLK test machines. However, due to the complexity of HLK, many organizations perform WHQL submission manually.

---

### 7. Conclusion

For any kernel driver included in the Arkhe(n) Windows build, you must:

- Use an EV code signing certificate (on a hardware token).
- Sign the driver with page hash (`/ph`) and cross‑sign with Microsoft’s certificate.
- Submit the driver to WHQL for Microsoft signing and distribution.

This ensures that the driver loads on all Windows systems with Secure Boot and meets Microsoft’s security standards.

---

## 🜏 I. O Requisito de Segurança (EV + WHQL)

Diferente de aplicativos de usuário, drivers de kernel exigem:
1.  **Certificado EV (Extended Validation):** Obrigatoriamente armazenado em um token de hardware (USB) ou HSM (Hardware Security Module). A chave privada **não pode ser exportada**.
2.  **Atestado da Microsoft (WHQL):** O driver deve ser submetido ao Windows Hardware Developer Center, onde a Microsoft executa testes (HLK) e assina o driver com sua própria chave raiz.

**Contexto Arkhe:**
O driver `arkhe-tdx.sys` atua como a ponte entre o nó validador (user-space) e o hardware TDX/TEE do processador. Ele é o "sensor" físico da malha.

---

## 🜏 II. Fluxo de Trabalho WHQL (Workflow)

```mermaid
graph LR
    A[Build Driver (.sys, .inf)] --> B[Create Catalog (.cat)]
    B --> C[Sign with EV Cert (Authenticode)]
    C --> D[Package (.cab)]
    D --> E[Submit to Microsoft (HDC)]
    E --> F{Microsoft HLK Tests}
    F -- Pass --> G[Microsoft Signs Driver]
    F -- Fail --> H[Fix & Retry]
    G --> I[Distribute Signed Driver]
```

---

## 🜏 III. Script de Assinatura e Preparação (PowerShell)

Este script prepara o driver para submissão. Ele assume que o certificado EV está acessível via um provedor criptográfico (CSP) ou Key Storage Provider (KSP).

**Nota:** A submissão à Microsoft geralmente requer interação manual via portal ou API dedicada, pois envolve upload de arquivos e verificação de empresa.

```powershell
# scripts/sign_driver_ev.ps1
param(
    [string]$DriverPath = "build\windows\amd64\arkhe-tdx.sys",
    [string]$InfPath = "drivers\arkhe-tdx.inf",
    [string]$EvCertThumbprint = $env:EV_CERT_THUMBPRINT # Thumbprint do cert EV no token/HSM
)

Write-Host "🜏 Iniciando processo de assinatura de Driver (EV)..."

# 1. Validação de Existência
if (-not (Test-Path $DriverPath)) { throw "Driver não encontrado: $DriverPath" }
if (-not (Test-Path $InfPath)) { throw "INF não encontrado: $InfPath" }

# 2. Criar arquivo de catálogo (.cat)
# O catálogo é o manifesto do driver que o Windows verifica.
$CatalogPath = $DriverPath -replace '\.sys$', '.cat'
Write-Host "   Criando catálogo: $CatalogPath"
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\inf2cat.exe" /driver:(Split-Path $DriverPath -Parent) /os:10_X64,10_ARM64

if (-not (Test-Path $CatalogPath)) {
    # Fallback se inf2cat não criar na raiz
    $CatalogPath = Join-Path (Split-Path $DriverPath -Parent) "arkhe-tdx.cat"
}

# 3. Assinar com Certificado EV
# IMPORTANTE: O certificado EV deve estar em um Smart Card ou HSM.
# O SignTool acessará o token via CSP/KSP.
# A flag /ac anexa o certificado raiz intermediário (Cross-Certificate), exigido para drivers.
$CrossCertPath = ".\certs\DigiCert_Global_Root_CA.crt" # Exemplo de certificado cruzado

Write-Host "   Assinando catálogo com certificado EV ($EvCertThumbprint)..."
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
    /v `
    /s MY `
    /sha1 $EvCertThumbprint `
    /ac $CrossCertPath `
    /tr http://timestamp.digicert.com `
    /td SHA256 `
    /fd SHA256 `
    $CatalogPath

if ($LASTEXITCODE -ne 0) {
    throw "Falha na assinatura EV do driver."
}

# 4. Verificar Assinatura
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" verify /kp $CatalogPath

Write-Host "✓ Driver e Catálogo assinados com EV."
Write-Host "   Próximo passo: Submeter o pacote .cab ao Windows Hardware Dev Center."
Write-Host "   Comando para empacotar: MakeCab /F arkhe-driver.ddf"
```

---

## 🜏 IV. Submissão WHQL (Hardware Dev Center)

O passo final não pode ser automatizado por script simples sem credenciais sensíveis de API da Microsoft, mas o processo é:

1.  **Empacotar:** Criar um arquivo `.cab` contendo o driver (`.sys`), o catálogo (`.cat`) e o arquivo de instalação (`.inf`).
    ```bash
    # Criar diretiva .ddf para MakeCab
    .Set CabinetNameTemplate=arkhe-tdx.cab
    .Set DiskDirectoryTemplate=.
    .Set CompressionType=MSZIP
    "build\windows\amd64\arkhe-tdx.sys"
    "build\windows\amd64\arkhe-tdx.cat"
    "drivers\arkhe-tdx.inf"
    
    MakeCab /F arkhe-driver.ddf
    ```

2.  **Submissão via API (Opcional para CI/CD Avançado):**
    A Microsoft oferece uma API REST para o Hardware Dev Center. Um script Python pode automatizar o upload.

    ```python
    # scripts/submit_whql.py (Pseudo-código conceitual)
    import requests
    
    # Autenticação via Azure AD App Registrations
    access_token = get_azure_ad_token()
    
    # Upload do CAB
    with open('arkhe-tdx.cab', 'rb') as f:
        response = requests.post(
            'https://manage.devcenter.microsoft.com/v2.0/my/hardware/products',
            headers={'Authorization': f'Bearer {access_token}'},
            files={'file': f}
        )
    
    submission_id = response.json()['id']
    print(f"Submissão WHQL enviada. ID: {submission_id}")
    print("Aguardando processamento e validação...")
    ```

3.  **Download e Distribuição:**
    Após a aprovação, a Microsoft fornece um novo arquivo `.zip` contendo o driver assinado por eles. **Este é o arquivo que deve ir para o instalador do usuário final.**

---

## 🜏 V. Integração no Instalador NSIS

O instalador final do Arkhe deve incluir o driver já aprovado pela Microsoft.

```nsis
; installer.nsi
Section "Kernel Driver (TDX Bridge)"
  ; Copiar driver para System32/drivers
  SetOutPath $SYSDIR\drivers
  File "dist\whql_signed\arkhe-tdx.sys"
  
  ; Criar serviço de kernel
  SimpleSC::InstallService "ArkheTDX" "Arkhe TDX Bridge" "1" "2" "$SYSDIR\drivers\arkhe-tdx.sys" "" "" ""
SectionEnd
```
