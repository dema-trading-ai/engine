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
echo "Installing DemaTrading.ai Engine... (this takes +/- 10 seconds)"
$executableUri = "https://engine-store.ams3.digitaloceanspaces.com/engine-windows-development.zip"
$tempDir = $env:TEMP + "\engine"
$tempLocation = $tempDir + "\executable.zip"
$installationDir = $env:ProgramFiles + "\engine"
$null = New-Item -ItemType Directory -Force -Path "$tempDir"
$wc = New-Object net.webclient
$wc.Downloadfile($executableUri, $tempLocation)
Expand-Archive -Force -Path "$tempLocation" -DestinationPath "$installationDir"
$pathContent = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
$pathLine = ";$installationDir/engine"
if (-not($pathContent -match [Regex]::Escape($pathLine))) {
    [Environment]::SetEnvironmentVariable("Path", $env:Path + $pathLine, [System.EnvironmentVariableTarget]::Machine)
}
echo "Installed DemaTrading.ai Engine."
echo " Open a new powershell window and type 'engine init <YOUR DIRECTORY NAME>' to get started."