param(
    [Parameter(Mandatory=$true)][string]$Script,
    [string]$LogName = 'gimp-log.txt',
    [string]$GimpExe = (Join-Path $env:LOCALAPPDATA 'Programs\GIMP 3\bin\gimp-console-3.exe')
)
$ErrorActionPreference = 'Stop'
$scriptPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot $Script))
if (-not $scriptPath.StartsWith($PSScriptRoot + '\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'GIMP script must stay within the Aemeath project.'
}
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) { throw 'GIMP script missing.' }
$gimpCommand = Get-Command -Name $GimpExe -CommandType Application -ErrorAction Stop
$profilePath = Join-Path $PSScriptRoot 'gimp-profile'
New-Item -ItemType Directory -Path $profilePath -Force | Out-Null
$env:GIMP3_DIRECTORY = $profilePath
$projectRootPython = ConvertTo-Json -InputObject $PSScriptRoot.Replace('\','/') -Compress
$scriptPathPython = ConvertTo-Json -InputObject $scriptPath.Replace('\','/') -Compress
$batchCommand = "from gi.repository import Gimp, Gio, Gegl; from pathlib import Path; PROJECT_ROOT = Path($projectRootPython); __file__ = $scriptPathPython; exec(compile(Path(__file__).read_text(encoding='utf-8'), __file__, 'exec'))"
& $gimpCommand.Source -n -d -s --console-messages --batch-interpreter=python-fu-eval -b $batchCommand --quit 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot $LogName)
if ($LASTEXITCODE -ne 0) { throw "GIMP exited with code $LASTEXITCODE" }
if ((Get-Content -LiteralPath (Join-Path $PSScriptRoot $LogName) -Raw) -match 'batch command experienced an execution error|Traceback \(most recent call last\)') {
    throw 'GIMP batch failed; inspect the log.'
}
