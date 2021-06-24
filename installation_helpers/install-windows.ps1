$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

function IsElevated {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object System.Security.Principal.WindowsPrincipal($id)
    if ($p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator))
    { Write-Output $true }      
    else
    { Write-Output $false }   
}

if (-not(IsElevated)) {
    throw "Please run this script as administrator" 
}

$executableUri = "https://engine-store.ams3.digitaloceanspaces.com/windows-exe%20%281%29.zip"
$tempDir = $env:TEMP + "\engine"
$tempLocation = $tempDir + "\executable.zip"
$installationDir = $env:ProgramFiles + "\engine"

New-Item -ItemType Directory -Force -Path "$tempDir"

$wc = New-Object net.webclient
$wc.Downloadfile($executableUri, $tempLocation)

Expand-Archive -Force -Path "$tempLocation" -DestinationPath "$installationDir"

$pathContent = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)

$pathLine = ";$installationDir"

if (-not($pathContent -match [Regex]::Escape($pathLine))) {
    [Environment]::SetEnvironmentVariable("Path", $env:Path + $pathLine, [System.EnvironmentVariableTarget]::Machine)
}