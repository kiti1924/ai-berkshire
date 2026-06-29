$ErrorActionPreference = "Stop"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
python "$scriptPath\installer.py" codex-skills
