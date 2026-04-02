<#
.SYNOPSIS
Prepara um pacote de Driver de Kernel do Windows para submissão ao WHQL / Hardware Dev Center.

.DESCRIPTION
Empacota um diretório contendo os arquivos do driver (.sys, .inf, .cat, etc.) em um arquivo .cab
e assina o .cab com um Certificado de Assinatura de Código EV (Extended Validation). 
Este .cab assinado com EV é o formato estritamente exigido pela Microsoft para 
Attestation Signing (assinatura de atestado) no Windows 10 e Windows 11.

.PARAMETER DriverDir
Caminho para o diretório que contém os arquivos do driver (ex: my_driver\).

.PARAMETER CabOutputPath
Caminho completo de saída para o arquivo .cab gerado (ex: build\arkhe_driver_submission.cab).

.PARAMETER CertThumbprint
O thumbprint SHA1 do Certificado EV no Windows Certificate Store.

.PARAMETER TimestampServer
URL do servidor de timestamp (padrão: Digicert).
#>
param (
    [Parameter(Mandatory=$true)][string]$DriverDir,
    [Parameter(Mandatory=$true)][string]$CabOutputPath,
    [Parameter(Mandatory=$true)][string]$CertThumbprint,
    [string]$TimestampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

Write-Host "🜏 [1/5] Localizando ferramentas do Windows SDK..."
$SignToolPath = (Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" | Sort-Object FullName -Descending | Select-Object -First 1).FullName
$Inf2CatPath = (Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x86\inf2cat.exe" | Sort-Object FullName -Descending | Select-Object -First 1).FullName
$MakeCabPath = "makecab.exe" # Geralmente em System32, disponível no PATH

if (-not $SignToolPath) { 
    Write-Error "signtool.exe não encontrado. Instale o Windows SDK." 
}
if (-not $Inf2CatPath) { 
    Write-Error "inf2cat.exe não encontrado. Instale o Windows SDK." 
}

if (-not (Test-Path $DriverDir)) {
    Write-Error "Diretório do driver não encontrado: $DriverDir"
}

Write-Host "🜏 [2/5] Gerando arquivo de catálogo (.cat) a partir do .inf..."
# Assume-se que o driver suporta Windows 10 x64. Ajuste /os conforme necessário.
& $Inf2CatPath /driver:$DriverDir /os:10_X64
if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao executar inf2cat." }

Write-Host "🜏 [3/5] Assinando o arquivo de catálogo (.cat) com o Certificado EV..."
$CatFiles = Get-ChildItem -Path $DriverDir -Filter *.cat
foreach ($CatFile in $CatFiles) {
    & $SignToolPath sign /fd SHA256 /tr $TimestampServer /td SHA256 /sha1 $CertThumbprint $CatFile.FullName
    if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao assinar o arquivo .cat: $($CatFile.Name)" }
}

Write-Host "🜏 [4/5] Gerando DDF (Diamond Directive File) para criação do CAB..."
$DdfPath = Join-Path $env:TEMP "arkhe_driver_submission.ddf"
$CabDir = Split-Path $CabOutputPath -Parent
$CabName = Split-Path $CabOutputPath -Leaf

if (-not (Test-Path $CabDir)) {
    New-Item -ItemType Directory -Path $CabDir | Out-Null
}

# Configuração do DDF para o MakeCab
$DdfContent = @"
.OPTION EXPLICIT
.Set CabinetNameTemplate=$CabName
.Set DiskDirectoryTemplate=$CabDir
.Set CompressionType=MSZIP
.Set UniqueFiles=Off
.Set Cabinet=on
.Set DiskDirectory1=$CabDir
"@

# Adiciona todos os arquivos do diretório do driver ao DDF
Get-ChildItem -Path $DriverDir -File | ForEach-Object {
    $DdfContent += "`r`n`"$($_.FullName)`""
}

Set-Content -Path $DdfPath -Value $DdfContent

Write-Host "🜏 [5/5] Empacotando arquivos do driver no CAB e assinando..."
& $MakeCabPath /f $DdfPath
if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao executar MakeCab." }

Write-Host "🜏 Assinando o arquivo CAB com o Certificado EV..."
# A Microsoft exige que o CAB de submissão seja assinado com EV
& $SignToolPath sign /fd SHA256 /tr $TimestampServer /td SHA256 /sha1 $CertThumbprint $CabOutputPath
if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao assinar o arquivo CAB." }

Write-Host "🜏 Verificando a assinatura do CAB..."
& $SignToolPath verify /pa /v $CabOutputPath

# Limpeza de arquivos temporários do MakeCab
Remove-Item $DdfPath -ErrorAction SilentlyContinue
Remove-Item "setup.rpt" -ErrorAction SilentlyContinue
Remove-Item "setup.inf" -ErrorAction SilentlyContinue

Write-Host "🜏 Preparação WHQL Concluída com Sucesso!"
Write-Host "O arquivo $CabOutputPath está pronto para ser submetido ao Windows Hardware Dev Center."
