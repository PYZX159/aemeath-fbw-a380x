param(
    [string]$PackagePath = (Join-Path $PSScriptRoot 'package\aemeath-fbw-a380x-stable')
)

# GIMP creates DDS images; these companion JSON files supply MSFS bitmap metadata.
# This script is confined to the new Aemeath project, never a Community directory.
$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$packageRoot = [System.IO.Path]::GetFullPath($PackagePath)
if (-not $packageRoot.StartsWith($projectRoot + '\',[System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Descriptor writes must stay inside this Aemeath project.'
}
$textureRoot = Join-Path $packageRoot 'SimObjects\AirPlanes\FlyByWire_A380_842_Aemeath\texture.AEMEATH'
$sourceRoot = Join-Path $PSScriptRoot 'artwork\final'
$expectedNames = @(
    'A380X_FUSE1_ALBEDO.PNG.DDS',
    'A380X_FUSE2_ALBEDO.PNG.DDS',
    'A380X_FUSE3_ALBEDO.PNG.DDS',
    'A380X_FUSE4_ALBEDO.PNG.DDS',
    'A380X_FUSE5_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_ENG_LH_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_ENG_RH_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_WING1_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_WING1_2_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_WING2_ALBEDO.PNG.DDS',
    'A380_EXTERIOR_WING2_2_ALBEDO.PNG.DDS',
    'A380X_REGISTRATION_ALBEDO.PNG.DDS',
    'A380X_EXTERIOR_WINGFENCE_ALBEDO.PNG.DDS'
)
$ddsFiles = @(Get-ChildItem -LiteralPath $textureRoot -File -Filter '*.DDS')
if ($ddsFiles.Count -ne 13) { throw "Expected thirteen painted DDS images; found $($ddsFiles.Count). No descriptors were written." }
foreach ($expectedName in $expectedNames) {
    if (-not (Test-Path -LiteralPath (Join-Path $textureRoot $expectedName) -PathType Leaf)) {
        throw "Required DDS missing: $expectedName. No descriptors were written."
    }
}
foreach ($ddsFile in $ddsFiles) {
    $sourceName = [System.IO.Path]::GetFileNameWithoutExtension($ddsFile.Name)
    $sourcePath = Join-Path $sourceRoot $sourceName
    $sourceDate = if (Test-Path -LiteralPath $sourcePath -PathType Leaf) {
        (Get-Item -LiteralPath $sourcePath).LastWriteTimeUtc.ToFileTimeUtc()
    } else {
        $ddsFile.LastWriteTimeUtc.ToFileTimeUtc()
    }
    $descriptor = [ordered]@{
        Version = 2
        SourceFileDate = [int64]$sourceDate
        Flags = @('FL_BITMAP_COMPRESSION','FL_BITMAP_MIPMAP')
    }
    if ($ddsFile.Name -ieq 'A380X_REGISTRATION_ALBEDO.PNG.DDS') {
        $descriptor.HasTransp = $true
    }
    $json = $descriptor | ConvertTo-Json -Compress -Depth 4
    [System.IO.File]::WriteAllText($ddsFile.FullName + '.json',$json,[System.Text.UTF8Encoding]::new($false))
}
Write-Output 'Wrote thirteen MSFS DDS descriptors inside the Aemeath project.'
