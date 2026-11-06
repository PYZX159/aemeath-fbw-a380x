param([string]$BasePackagePath = 'D:\Microsoft Flight Simulator 2024(ChaJian)\Community2024\flybywire-aircraft-a380-842')
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'Update-PackageLayout.ps1')
& (Join-Path $PSScriptRoot 'Validate-Package.ps1') -BasePackagePath $BasePackagePath | Tee-Object -FilePath (Join-Path $PSScriptRoot 'validation-result.txt')
$workspacePath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$sourcePath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'package\aemeath-fbw-a380x-stable'))
$deliveryPath = [IO.Path]::GetFullPath((Join-Path $workspacePath 'aemeath-fbw-a380x-stable'))
if (-not $deliveryPath.StartsWith($workspacePath + '\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe delivery path' }
New-Item -ItemType Directory -Path $deliveryPath -Force | Out-Null
$sourceFiles = @(Get-ChildItem -LiteralPath $sourcePath -Recurse -File)
foreach ($fileInfo in $sourceFiles) {
    $relativePath = [IO.Path]::GetRelativePath($sourcePath,$fileInfo.FullName)
    $destination = Join-Path $deliveryPath $relativePath
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $fileInfo.FullName -Destination $destination -Force
    if ((Get-FileHash -LiteralPath $fileInfo.FullName -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
        throw "Delivery hash mismatch: $relativePath"
    }
}
if (@(Get-ChildItem -LiteralPath $deliveryPath -Recurse -File).Count -ne $sourceFiles.Count) { throw 'Unexpected extra file in delivery folder' }
Write-Output ("Verified {0} delivery files by SHA256." -f $sourceFiles.Count)
$archivePath = Join-Path $PSScriptRoot 'deliverables\Aemeath-AM01-FBW-A380X-Stable-v0.1.0.zip'
Push-Location -LiteralPath (Split-Path -Parent $sourcePath)
try {
    & 'C:\Program Files\7-Zip\7z.exe' a -tzip $archivePath 'aemeath-fbw-a380x-stable' -mx=5
    if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed' }
    & 'C:\Program Files\7-Zip\7z.exe' t $archivePath
    if ($LASTEXITCODE -ne 0) { throw 'Archive integrity check failed' }
} finally { Pop-Location }
Write-Output 'AEMEATH_DELIVERY_READY'
