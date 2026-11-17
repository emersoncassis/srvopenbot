# Abre o app OpenBot do Windows usando o servidor de contas proprio (sem openbot.run).
#
# O login por e-mail do servidor de contas nao fica na internet (ele mostra o codigo na tela, sem e-mail).
# Por isso este script abre um tunel SSH: o app fala com o servidor de contas em http://127.0.0.1:3100
# (o app aceita http so em 127.0.0.1) e com o Signal publico. Depois do login, o OpenBot do servidor
# aparece na lista de servidores do app, como no celular.
#
# Uso:  powershell -ExecutionPolicy Bypass -File abrir-openbot-local.ps1
# Precisa: chave SSH com acesso root ao VPS. Deixe esta janela aberta enquanto usa o app.

param(
  [string]$Vps = "91.108.124.85",
  [string]$Chave = "$env:USERPROFILE\.ssh\dokploy_claude",
  [string]$Signal = "wss://signal.openbot.icteam.com.br/v1/signal",
  [int]$Porta = 3100
)
$ErrorActionPreference = "Stop"
$app = "$env:LOCALAPPDATA\Programs\OpenBot\OpenBot.exe"
if (-not (Test-Path $app)) { throw "OpenBot nao encontrado em $app" }

# O app precisa reabrir com as variaveis: feche o que estiver aberto.
Get-Process OpenBot -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# O projeto OpenBot Contas publica a porta 3101 so no localhost do VPS; o tunel traz ela para este PC.
$tunel = Start-Process ssh -PassThru -WindowStyle Hidden -ArgumentList @(
  "-i", $Chave, "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30",
  "-N", "-L", "127.0.0.1:${Porta}:127.0.0.1:3101", "root@$Vps")
for ($i = 0; $i -lt 20; $i++) {
  try { Invoke-WebRequest "http://127.0.0.1:$Porta/health/live" -UseBasicParsing -TimeoutSec 2 | Out-Null; $ok = $true; break } catch { Start-Sleep 1 }
}
if (-not $ok) { Stop-Process $tunel -ErrorAction SilentlyContinue; throw "O tunel para o servidor de contas nao respondeu." }

$env:OPENBOT_AUTH_API_URL = "http://127.0.0.1:$Porta"
$env:OPENBOT_REMOTE_SIGNAL_URL = $Signal
$proc = Start-Process $app -PassThru
Write-Host "OpenBot aberto com o servidor de contas proprio. Nao feche esta janela enquanto usar o app."
$proc.WaitForExit()
# O Electron reabre em outro processo; espere todos fecharem antes de derrubar o tunel.
while (Get-Process OpenBot -ErrorAction SilentlyContinue) { Start-Sleep 5 }
Stop-Process $tunel -ErrorAction SilentlyContinue
