param([ValidateSet('before','after')][string]$Phase = 'before')
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$out = $PSScriptRoot
$prefix = $root + '\'
$totals = @{}
$generated = @{}
$structural = @{}
$skippedReparse = 0
$errors = 0
$fileCount = 0L
$bytes = 0L
$stack = [Collections.Generic.Stack[string]]::new()
$stack.Push($root)
while ($stack.Count) {
    $dir = $stack.Pop()
    try { $entries = [IO.DirectoryInfo]::new($dir).GetFileSystemInfos() }
    catch { $errors++; continue }
    foreach ($entry in $entries) {
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { $skippedReparse++; continue }
        $rel = $entry.FullName.Substring($prefix.Length)
        if ($entry -is [IO.DirectoryInfo]) { $stack.Push($entry.FullName); continue }
        $size = $entry.Length
        $bytes += $size; $fileCount++
        $top = ($rel -split '\\',2)[0]
        if (-not $totals.ContainsKey($top)) { $totals[$top] = @{bytes=0L;files=0L} }
        $totals[$top].bytes += $size; $totals[$top].files++
        if ($top -in @('.worktrees','.git')) {
            $parts = $rel -split '\\'
            $key = if ($top -eq '.worktrees' -and $parts.Length -gt 3 -and $parts[2] -in @('test-data','evidence','archive')) { $parts[0..2] -join '\' } else { $parts[0..1] -join '\' }
            if (-not $structural.ContainsKey($key)) { $structural[$key] = @{bytes=0L;files=0L} }
            $structural[$key].bytes += $size; $structural[$key].files++
        }
        # Only generated-directory paths are emitted; no private filenames.
        if ($rel -notmatch '(^|\\)(archive|test-data|evidence|Run-System|\.git|r-m-review)(\\|$)') {
            $parts = $rel -split '\\'
            for ($i=0; $i -lt $parts.Length-1; $i++) {
                if ($parts[$i] -in @('__pycache__','.pytest_cache','.next','node_modules','.venv')) {
                    $key = ($parts[0..$i] -join '\')
                    if (-not $generated.ContainsKey($key)) { $generated[$key] = @{bytes=0L;files=0L} }
                    $generated[$key].bytes += $size; $generated[$key].files++
                    break
                }
            }
        }
    }
}
$summary = [ordered]@{utc=[DateTime]::UtcNow.ToString('o'); root=$root;logical_bytes=$bytes;files=$fileCount;reparse_entries_skipped=$skippedReparse;enumeration_errors=$errors;top_level=@($totals.GetEnumerator() | ForEach-Object { [pscustomobject]@{name=$_.Key;bytes=$_.Value.bytes;files=$_.Value.files} } | Sort-Object bytes -Descending);generated=@($generated.GetEnumerator() | ForEach-Object { [pscustomobject]@{path=$_.Key;bytes=$_.Value.bytes;files=$_.Value.files} } | Sort-Object bytes -Descending)}
$summary | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $out ($Phase+'.json')) -Encoding UTF8
$structural.GetEnumerator() | ForEach-Object { [pscustomobject]@{path=$_.Key;bytes=$_.Value.bytes;files=$_.Value.files} } | Sort-Object bytes -Descending | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $out ($Phase+'-structural.json')) -Encoding UTF8
[pscustomobject]@{phase=$Phase;bytes=$bytes;files=$fileCount;reparse_skipped=$skippedReparse;errors=$errors}
