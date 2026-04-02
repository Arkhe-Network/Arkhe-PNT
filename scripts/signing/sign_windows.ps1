<#
.SYNOPSIS
Arkhe(n) Windows Code Signing Script (Bulk)

.DESCRIPTION
Recursively signs all Windows executables (.exe, .dll) and installers (.msi) 
in a given directory using signtool.exe with SHA256 digest and a trusted timestamp.

.PARAMETER TargetDir
Path to the directory containing the files to sign.

.PARAMETER CertThumbprint
The SHA1 thumbprint of the Code Signing Certificate in the Windows Cert Store.

.PARAMETER TimestampServer
URL of the timestamp server (default: Digicert).
#>
param (
    [Parameter(Mandatory=$true)][string]$TargetDir,
    [Parameter(Mandatory=$true)][string]$CertThumbprint,
    [string]$TimestampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

Write-Host "🜏 [1/3] Locating signtool.exe..."
$SignToolPath = (Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" | Sort-Object FullName -Descending | Select-Object -First 1).FullName

if (-not $SignToolPath) {
    Write-Error "signtool.exe not found. Please install the Windows SDK."
}

Write-Host "🜏 [2/3] Finding executables, libraries, and installers in $TargetDir..."
if (-not (Test-Path $TargetDir)) {
    Write-Error "Target directory not found: $TargetDir"
}

$FilesToSign = Get-ChildItem -Path $TargetDir -Include *.exe,*.dll,*.msi -Recurse -File

if ($FilesToSign.Count -eq 0) {
    Write-Host "No .exe, .dll, or .msi files found to sign in $TargetDir."
    exit 0
}

Write-Host "Found $($FilesToSign.Count) files to sign."

Write-Host "🜏 [3/3] Signing files with SHA256 and timestamp..."
$FailedFiles = @()

foreach ($File in $FilesToSign) {
    Write-Host "   -> Signing: $($File.Name)"
    
    # Execute signtool
    # /fd SHA256 : File digest algorithm
    # /tr : Timestamp server
    # /td SHA256 : Timestamp digest algorithm
    # /sha1 : Certificate thumbprint
    & $SignToolPath sign /fd SHA256 /tr $TimestampServer /td SHA256 /sha1 $CertThumbprint $File.FullName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "      [!] Signing failed for $($File.Name)"
        $FailedFiles += $File.FullName
    } else {
        # Verify signature
        & $SignToolPath verify /pa /q $File.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "      [!] Verification failed for $($File.Name)"
            $FailedFiles += $File.FullName
        } else {
            Write-Host "      [OK] Verified."
        }
    }
}

if ($FailedFiles.Count -gt 0) {
    Write-Error "Signing process completed with errors. Failed to sign $($FailedFiles.Count) files."
} else {
    Write-Host "🜏 Windows Bulk Signing Complete! All files successfully signed and timestamped."
}
