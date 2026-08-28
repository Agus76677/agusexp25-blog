# 双击上传图片到图床（PicX / pic.agusexp25.top）。
#
# 两种用法：
#   1) 双击项目根目录的「上传图片.cmd」——会弹出文件选择框，选一张或多张图片；
#   2) 把图片或文件夹直接拖到「上传图片.cmd」图标上。
#
# 依赖：Node.js、Git，以及项目根目录 .env 里的 PICX_GITHUB_TOKEN。
# 实际转换 / 推送逻辑仍复用 scripts\upload-images.mjs，本脚本只是给它加一个鼠标入口。

$ErrorActionPreference = 'Stop'

# 控制台统一用 UTF-8，避免中文说明和图片链接出现乱码。
try {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

# 项目根目录 = 本脚本所在的 scripts\ 的上一级。
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$uploader = Join-Path $scriptDir 'upload-images.mjs'
Set-Location $projectRoot

# 收集要上传的图片：优先用拖拽 / 命令行传入的路径，否则弹出文件选择框。
$inputs = @($args | Where-Object { $_ -and ($_.ToString().Trim() -ne '') })

if ($inputs.Count -eq 0) {
  Add-Type -AssemblyName System.Windows.Forms | Out-Null
  $dialog = New-Object System.Windows.Forms.OpenFileDialog
  $dialog.Title = '选择要上传的图片（按住 Ctrl / Shift 可多选）'
  $dialog.Filter = '图片 (*.png;*.jpg;*.jpeg;*.webp;*.avif)|*.png;*.jpg;*.jpeg;*.webp;*.avif|所有文件 (*.*)|*.*'
  $dialog.Multiselect = $true
  $dialog.InitialDirectory = [Environment]::GetFolderPath('MyPictures')
  if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
    Write-Host '已取消，没有选择任何图片。'
    return
  }
  $inputs = @($dialog.FileNames)
}

Write-Host ''
Write-Host ("准备上传 {0} 个文件/目录：" -f $inputs.Count) -ForegroundColor Cyan
$inputs | ForEach-Object { Write-Host "  $_" }
Write-Host ''

# 检查 Node 是否可用。
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Host '找不到 Node.js，请先安装（https://nodejs.org）或确认它在 PATH 中。' -ForegroundColor Red
  exit 1
}

# 软提示：缺少上传凭据时先给个警告，但仍继续（用户可能用了系统环境变量）。
$envFile = Join-Path $projectRoot '.env'
if (-not ($env:PICX_GITHUB_TOKEN -or $env:GITHUB_TOKEN -or (Test-Path $envFile))) {
  Write-Host '提示：未检测到 .env 或 PICX_GITHUB_TOKEN，推送图床可能会因缺少凭据而失败。' -ForegroundColor Yellow
  Write-Host ''
}

# 调用现有上传引擎：转成 webp -> 推送图床 master -> 同步 gh-pages。
& node $uploader @inputs
$code = $LASTEXITCODE

Write-Host ''
if ($code -eq 0) {
  Write-Host '完成。上面的图片链接可直接粘贴到 Markdown 里使用。' -ForegroundColor Green
} else {
  Write-Host ("上传失败（退出码 {0}），请查看上面的错误信息。" -f $code) -ForegroundColor Red
}
exit $code
