$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

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

if(-not($pathContent -match [Regex]::Escape($pathLine))){
    [Environment]::SetEnvironmentVariable("Path", $env:Path + $pathLine, [System.EnvironmentVariableTarget]::Machine)
}