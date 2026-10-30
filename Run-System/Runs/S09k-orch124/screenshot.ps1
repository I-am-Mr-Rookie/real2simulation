$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath $PSScriptRoot\..\..\..
New-Item -ItemType Directory -Force evidence/S09 | Out-Null
$job = Start-Job { Set-Location -LiteralPath $using:PWD; python -m http.server 8765 --bind 127.0.0.1 }
Start-Sleep 3
$c = Get-ChildItem "$env:LOCALAPPDATA/ms-playwright" -Directory -Filter 'chromium_headless_shell-*' | Sort-Object Name -Descending | Select-Object -First 1
$exe = (Get-ChildItem $c.FullName -Recurse -Filter chrome-headless-shell.exe | Select-Object -First 1).FullName
$url = 'http://127.0.0.1:8765/tests/viewer/trajectory-replay.html'
foreach ($w in 375, 1280) {
  & $exe --headless --no-first-run "--window-size=$w,900" --virtual-time-budget=5000 "--screenshot=$PWD\evidence\S09\S09k-replay-$w.png" $url 2>$null | Out-Null
  $dom = & $exe --headless --no-first-run "--window-size=$w,900" --virtual-time-budget=5000 --dump-dom $url 2>$null
  "$w " + (($dom -join "\n") -replace '(?s).*<pre id="out">([^<]*)</pre>.*', '$1')
}
Stop-Job $job; Remove-Job $job

