$ErrorActionPreference = 'Stop'

# Update only this workspace's independent Aemeath repaint package.
$packageRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'package\aemeath-fbw-a380x-stable'))
$manifestPath = Join-Path $packageRoot 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw 'The expected Aemeath livery manifest is missing.'
}

& (Join-Path $PSScriptRoot 'Write-TextureDescriptors.ps1') -PackagePath $packageRoot

$packageFiles = @(Get-ChildItem -LiteralPath $packageRoot -Recurse -File | Where-Object {
    $_.FullName -ne $manifestPath -and $_.FullName -ne (Join-Path $packageRoot 'layout.json')
} | Sort-Object FullName)
$layoutItems = @($packageFiles | ForEach-Object {
    [ordered]@{
        path = [System.IO.Path]::GetRelativePath($packageRoot,$_.FullName).Replace('\','/')
        size = $_.Length
        date = $_.LastWriteTimeUtc.ToFileTimeUtc()
    }
})
$layoutJson = [ordered]@{content=$layoutItems} | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $packageRoot 'layout.json'),$layoutJson + [Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$contentBytes = ($packageFiles | Measure-Object -Property Length -Sum).Sum
$manifest.total_package_size = ([int64]$contentBytes).ToString('D20')
[System.IO.File]::WriteAllText($manifestPath,($manifest | ConvertTo-Json -Depth 8) + [Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
Write-Output ('Indexed {0} files, {1} bytes in {2}' -f $layoutItems.Count,$contentBytes,$packageRoot)
