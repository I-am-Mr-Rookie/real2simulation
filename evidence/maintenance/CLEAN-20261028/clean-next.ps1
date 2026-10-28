# Single-target maintenance receipt; never accepts an arbitrary deletion path.
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$target = Join-Path $root 'Build\web\.next'
$cutoff = [DateTimeOffset]::Parse('2026-10-28T14:20:00Z')
function Assert-True($condition, $message) { if (-not $condition) { throw $message } }
function Assert-Contained([string]$path) {
    Assert-True ($path.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)) 'Outside canonical root'
}
function Metadata-Snapshot {
    $stack = [Collections.Generic.Stack[string]]::new(); $stack.Push($root)
    $records = [Collections.Generic.List[string]]::new()
    $bytes = 0L; $files = 0L
    while ($stack.Count) {
        foreach ($e in [IO.DirectoryInfo]::new($stack.Pop()).GetFileSystemInfos()) {
            Assert-True (-not ($e.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse point in snapshot'
            if ($e.FullName -eq $target) { continue }
            if ($e -is [IO.DirectoryInfo]) { $stack.Push($e.FullName); continue }
            $bytes += $e.Length; $files++
            $records.Add($e.FullName.Substring($root.Length)+"`t"+$e.Length+"`t"+$e.LastWriteTimeUtc.Ticks)
        }
    }
    $records.Sort([StringComparer]::Ordinal)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $hash = [Convert]::ToHexString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes(($records -join "`n")))) } finally { $sha.Dispose() }
    [pscustomobject]@{files=$files;logical_bytes=$bytes;metadata_sha256=$hash}
}
Assert-True ([DateTimeOffset]::UtcNow -lt $cutoff) 'Deletion cutoff passed'
$resolved = (Resolve-Path -LiteralPath $target).ProviderPath
Assert-Contained $resolved
Assert-True ($resolved -eq $target -and (Split-Path -Leaf $resolved) -eq '.next') 'Unexpected generated identity'
Assert-True ($resolved -notmatch '(?i)(\\archive\\|\\test-data\\|\\evidence\\|\\Run-System\\|\\\.git\\|r-m-review)') 'Protected target'
$ancestor = [IO.DirectoryInfo]::new($resolved)
while ($ancestor) {
    Assert-True (-not ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse ancestor'
    $ancestor = $ancestor.Parent
}
$items = @(Get-ChildItem -LiteralPath $resolved -Force -Recurse)
Assert-True (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count -eq 0) 'Reparse descendant'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $resolved 'dev\lock'))) 'Next dev lock present'
$tracked = @(& git -C $root ls-files -- 'Build/web/.next')
Assert-True ($LASTEXITCODE -eq 0 -and $tracked.Count -eq 0) 'Tracked descendants or git failure'
& git -C $root check-ignore -q -- 'Build/web/.next'
Assert-True ($LASTEXITCODE -eq 0) 'Target not ignored'
$ignoreReason = @(& git -C $root check-ignore -v -- 'Build/web/.next')
$statusBefore = @(& git --no-optional-locks -C $root status --porcelain=v1)
$headBefore = (& git -C $root rev-parse HEAD).Trim()
$processes = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(node|npm|pnpm|next)(\.exe)?$' })
$processSummary = @($processes | ForEach-Object {
    $c = $_.CommandLine
    [pscustomobject]@{pid=$_.ProcessId;name=$_.Name;command_available=[bool]$c;known_tool_host=($c -match '(mcp|server-playwright|codex|context7|tinyfish)');target_reference=($c -like '*Build*web*' -or $c -like '*.next*');build_server=($c -match '(next-server|next[\\/].*(dev|start|build)|next\s+(dev|start|build)|webpack|vite|npm.+(dev|start|build)|pnpm.+(dev|start|build))')}
})
Assert-True (@($processSummary | Where-Object { -not $_.command_available -or -not $_.known_tool_host -or $_.target_reference -or $_.build_server }).Count -eq 0) 'Unknown or active node/build process; skip deletion'
$outsideBefore = Metadata-Snapshot
$fileItems = @($items | Where-Object { -not $_.PSIsContainer })
$targetBytes = ($fileItems | Measure-Object Length -Sum).Sum
$ledger = [ordered]@{target=$resolved;reason='Ignored Next.js generated build/cache; tracked package.json build script regenerates it';regenerate='cd Build/web; npm run build (not run)';utc_validated=[DateTime]::UtcNow.ToString('o');files_before=$fileItems.Count;directories_before=@($items | Where-Object PSIsContainer).Count;bytes_before=$targetBytes;contained=$true;reparse_free=$true;protected_parent_absent=$true;tracked_descendants=0;ignored=$true;ignore_rule=$ignoreReason;process_check=$processSummary;outside_before=$outsideBefore;head_before=$headBefore;status_before=$statusBefore;outcome='VALIDATED_NOT_YET_DELETED'}
$ledgerPath = Join-Path $PSScriptRoot 'deletion-ledger.json'
$ledger | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $ledgerPath -Encoding UTF8
Assert-True ([DateTimeOffset]::UtcNow -lt $cutoff) 'Deletion cutoff passed'
Assert-Contained (Resolve-Path -LiteralPath $resolved).ProviderPath
Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
$ledger.outcome = 'DELETED'
$ledger.utc_deleted = [DateTime]::UtcNow.ToString('o')
$ledger.target_absent = -not (Test-Path -LiteralPath $resolved)
$ledger.outside_after = Metadata-Snapshot
$ledger.status_after = @(& git --no-optional-locks -C $root status --porcelain=v1)
$ledger.head_after = (& git -C $root rev-parse HEAD).Trim()
$ledger.outside_metadata_unchanged = ($ledger.outside_before.metadata_sha256 -eq $ledger.outside_after.metadata_sha256)
$ledger.git_status_unchanged = (($ledger.status_before -join "`n") -eq ($ledger.status_after -join "`n"))
$ledger | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $ledgerPath -Encoding UTF8
Assert-True $ledger.target_absent 'Deletion incomplete'
Assert-True $ledger.outside_metadata_unchanged 'Unexpected outside metadata change; stop cleanup'
Assert-True ($ledger.git_status_unchanged -and $ledger.head_before -eq $ledger.head_after) 'Unexpected git change; stop cleanup'
[pscustomobject]@{deleted=$resolved;logical_bytes=$targetBytes;files=$fileItems.Count;outside_unchanged=$true;git_unchanged=$true}
