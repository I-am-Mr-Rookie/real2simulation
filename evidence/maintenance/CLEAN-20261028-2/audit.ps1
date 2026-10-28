$ErrorActionPreference = 'Stop'
$root = 'C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$prepared = 'C:\Users\HP\.codex\worktrees\s02g-forensics\2026-10-26 - Meta Global AI Developer Hackathon'
$out = $PSScriptRoot
$start = [DateTime]::UtcNow.ToString('o')

function Assert($ok, [string]$message) { if (-not $ok) { throw $message } }
function Under([string]$path, [string]$parent) {
    [IO.Path]::GetFullPath($path).StartsWith([IO.Path]::GetFullPath($parent).TrimEnd('\')+'\', [StringComparison]::OrdinalIgnoreCase)
}
function SafePath([string]$path) {
    $full = [IO.Path]::GetFullPath($path)
    Assert ((Resolve-Path -LiteralPath $full).ProviderPath -eq $full) 'Resolved path differs'
    $node = Get-Item -LiteralPath $full -Force
    while ($null -ne $node) {
        Assert (-not ($node.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse path rejected'
        $node = if ($node -is [IO.DirectoryInfo]) { $node.Parent } else { $node.Directory }
    }
    $full
}
function Hash([string]$path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Save([string]$name, $value) {
    $value | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $out $name) -Encoding UTF8
}
function GitState([string]$path) {
    $head = git --no-optional-locks -C $path rev-parse HEAD
    Assert ($LASTEXITCODE -eq 0) 'HEAD lookup failed'
    $status = @(git --no-optional-locks -C $path status --porcelain=v1 --untracked-files=normal)
    Assert ($LASTEXITCODE -eq 0) 'Git status failed'
    $index = @(git --no-optional-locks -C $path ls-files -s)
    Assert ($LASTEXITCODE -eq 0) 'Git index lookup failed'
    [pscustomobject]@{root=$path;head=$head;status=$status;index=$index}
}
function Inventory {
    # Reused prior cleaner's metadata-only stack traversal, simplified to aggregates.
    $totals = @{}; $stack = [Collections.Generic.Stack[string]]::new(); $stack.Push($root)
    $count=0L; $bytes=0L; $reparse=0
    while($stack.Count) {
        foreach($entry in [IO.DirectoryInfo]::new($stack.Pop()).GetFileSystemInfos()) {
            if($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { $reparse++; continue }
            if($entry -is [IO.DirectoryInfo]) { $stack.Push($entry.FullName); continue }
            $top=$entry.FullName.Substring($root.Length+1).Split('\')[0]
            if(-not $totals.ContainsKey($top)) { $totals[$top]=@{bytes=0L;files=0L} }
            $totals[$top].bytes += $entry.Length; $totals[$top].files++
            $bytes += $entry.Length; $count++
        }
    }
    $rows=@($totals.GetEnumerator() | ForEach-Object { [pscustomobject]@{name=$_.Key;bytes=$_.Value.bytes;files=$_.Value.files} } | Sort-Object name)
    Assert (($rows|Measure-Object bytes -Sum).Sum -eq $bytes) 'Inventory sum mismatch'
    [pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');logical_bytes=$bytes;files=$count;reparse_skipped=$reparse;top_level=$rows}
}
function Processes {
    $all=@(Get-CimInstance Win32_Process)
    # No raw command lines: they may contain credentials. Matches contain only PID/name.
    $matches=@($all | Where-Object {
        $_.ProcessId -ne $PID -and $_.CommandLine -and
        ($_.CommandLine.IndexOf($root+'\.worktrees\S02c\',[StringComparison]::OrdinalIgnoreCase) -ge 0 -or
         $_.CommandLine.IndexOf($root+'\.worktrees\S02c1\',[StringComparison]::OrdinalIgnoreCase) -ge 0)
    } | Select-Object ProcessId,Name)
    [pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');observed=$all.Count;exact_candidate_tree_command_matches=$matches;
      limitation='Command-line scan is not an open-handle/cwd proof; no deletion permitted anyway because every candidate is tracked.'}
}

Assert (Under ($root+'\.worktrees\S02c\test-data\public\x') ($root+'\.worktrees\S02c\test-data')) 'Positive containment failed'
Assert (-not (Under ($root+'\.worktrees\S02c\test-data-evil\x') ($root+'\.worktrees\S02c\test-data'))) 'Sibling escape accepted'
Assert (-not (Under ($root+'\.worktrees\S02c\test-data\..\outside') ($root+'\.worktrees\S02c\test-data'))) 'Parent escape accepted'
Assert (-not (Under ($root+'\.worktrees\S02c1\test-data\x') ($root+'\.worktrees\S02c\test-data'))) 'Other source root accepted'
SafePath $root | Out-Null; SafePath $prepared | Out-Null
Assert ((git --no-optional-locks -C $prepared branch --show-current) -eq 'run/CLEAN-20261028-2') 'Wrong prepared branch'
Assert ((git --no-optional-locks -C $prepared rev-parse HEAD) -eq '6a2a2be5508fbe6717705292a420f0675bdd92d2') 'Prepared HEAD changed'
$sources=@('S02c','S02c1') | ForEach-Object { SafePath (Join-Path $root ".worktrees\$_") }
$beforeGit=@(GitState $root; foreach($s in $sources) { GitState $s })
Save 'git-before.json' $beforeGit
Save 'inventory-before.json' (Inventory)
Save 'process-before.json' (Processes)
$recordPath=Join-Path $root 'evidence\clips\S02c-acquisition.json'
$recordHash=Hash $recordPath
$records=@((Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json).files)
$prefixPath=(Get-Content -Raw -LiteralPath (Join-Path $root 'evidence\S07\S07b\recovery3\manifest.json') | ConvertFrom-Json).prefix_directory
function PrefixMetadata {
    $files=@(Get-ChildItem -LiteralPath $prefixPath -File -Force)
    @($files | Sort-Object Name | ForEach-Object { [pscustomobject]@{name=$_.Name;bytes=$_.Length;mtime=$_.LastWriteTimeUtc.ToString('o')} })
}
$prefixBefore=@(PrefixMetadata)
Assert ($prefixBefore.Count -eq 271) 'Protected prefix count unexpected'
Save 'prefix-before.json' $prefixBefore
$maps=@(foreach($source in $sources) {
    $allowed=SafePath (Join-Path $source 'test-data')
    foreach($file in Get-ChildItem -LiteralPath $allowed -File -Recurse -Force) {
        $candidate=SafePath $file.FullName
        Assert (Under $candidate $allowed) 'Outside deletion allowlist'
        $rel=$candidate.Substring($source.Length+1).Replace('\','/')
        Assert ($rel -notmatch '(^|/)(\.git|\.env[^/]*|evidence|Run-System|archive)(/|$)') 'Protected overlap'
        $canonical=SafePath (Join-Path $root $rel)
        Assert (Under $canonical (Join-Path $root 'test-data')) 'Canonical escape'
        $original=Get-Item -LiteralPath $canonical -Force
        Assert ($original -is [IO.FileInfo]) 'Canonical not regular file'
        $tracked=@(git --no-optional-locks -C $source ls-files -- $rel)
        Assert ($LASTEXITCODE -eq 0) 'Index query failed'
        $ignore=@(git --no-optional-locks -C $source check-ignore -v -- $rel); $ignoreExit=$LASTEXITCODE
        Assert ($ignoreExit -in @(0,1)) 'Ignore query failed'
        $ch=Hash $candidate; $oh=Hash $canonical
        $acq=@($records | Where-Object {$_.local_path -eq $rel})
        $recordMatches=($acq.Count -eq 1 -and $acq[0].sha256 -eq $oh)
        $identity=($ch -eq $oh -and $file.Length -eq $original.Length)
        $reasons=@(); if($tracked.Count) {$reasons+='TRACKED_IN_SOURCE_INDEX'}
        if($ignoreExit -ne 0) {$reasons+='NOT_IGNORED_IN_SOURCE_WORKTREE'}
        if(-not $identity) {$reasons+='CANONICAL_IDENTITY_MISMATCH'}
        if(-not $recordMatches) {$reasons+='NO_UNAMBIGUOUS_ACQUISITION_HASH'}
        [pscustomobject]@{candidate=$candidate;allowed_root=$allowed;canonical=$canonical;relative_path=$rel;
          bytes=$file.Length;sha256=$ch;canonical_sha256=$oh;identical=$identity;
          tracked_in_source=($tracked.Count -gt 0);tracked_index_paths=$tracked;ignored_in_source=($ignoreExit -eq 0);
          ignore_exit=$ignoreExit;ignore_rule=$ignore;acquisition_sha256=@($acq | ForEach-Object {$_.sha256});
          acquisition_hash_matches=$recordMatches;decision='KEEP';reasons=$reasons;
          restoration='No restoration needed: retained. Historical path maps to canonical above. If separately authorized restoration is ever needed, copy canonical bytes to exact candidate path after verifying SHA256 and absence; never overwrite an existing file.'}
    }
})
Assert ($maps.Count -eq 44) 'Unexpected candidate count'
Assert (@($maps | Where-Object {-not $_.tracked_in_source -or $_.ignored_in_source}).Count -eq 0) 'Finding changed: stop for review, no deletion implemented'
Save 'restoration-map.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');acquisition_record=$recordPath;acquisition_record_sha256=$recordHash;
  deletion_enabled=$false;deleted_files=0;deleted_logical_bytes=0;maps=$maps})

# Fresh second full hashes: no destructive command exists in this audit.
foreach($m in $maps) {
    Assert ((Hash $m.canonical) -eq $m.canonical_sha256) 'Canonical input changed'
    Assert ((Hash $m.candidate) -eq $m.sha256) 'Retained candidate changed'
    Assert ((Get-Item -LiteralPath $m.candidate).Length -eq $m.bytes) 'Retained candidate size changed'
}
Assert ((Hash $recordPath) -eq $recordHash) 'Acquisition manifest changed'
$prefixAfter=@(PrefixMetadata); Save 'prefix-after.json' $prefixAfter
Assert (($prefixBefore|ConvertTo-Json -Compress) -eq ($prefixAfter|ConvertTo-Json -Compress)) 'Protected prefix metadata changed'
$afterGit=@(GitState $root; foreach($s in $sources) { GitState $s })
Save 'git-after.json' $afterGit
$sourceGitUnchanged=($beforeGit[1..2]|ConvertTo-Json -Compress -Depth 6) -eq ($afterGit[1..2]|ConvertTo-Json -Compress -Depth 6)
Assert $sourceGitUnchanged 'Dormant source Git state changed'
Save 'inventory-after.json' (Inventory)
Save 'process-after.json' (Processes)
Save 'verification.json' ([ordered]@{start_utc=$start;end_utc=[DateTime]::UtcNow.ToString('o');status='PARTIAL';
  candidates=$maps.Count;candidate_bytes=($maps|Measure-Object bytes -Sum).Sum;
  exact_canonical_matches=@($maps|Where-Object {$_.identical}).Count;
  acquisition_matches=@($maps|Where-Object {$_.acquisition_hash_matches}).Count;
  tracked_candidates=@($maps|Where-Object {$_.tracked_in_source}).Count;ignored_candidates=0;
  retained_candidates=$maps.Count;deleted_files=0;deleted_logical_bytes=0;
  fresh_canonical_and_candidate_hashes='PASS';dormant_git_unchanged=$sourceGitUnchanged;
  canonical_git_unchanged=(($beforeGit[0]|ConvertTo-Json -Compress -Depth 6) -eq ($afterGit[0]|ConvertTo-Json -Compress -Depth 6));
  protected_prefix_count=$prefixAfter.Count;protected_prefix_bytes=($prefixAfter|Measure-Object bytes -Sum).Sum;protected_prefix_metadata_unchanged=$true;
  self_checks=@('positive containment','sibling-prefix rejection','parent-escape rejection','cross-source rejection','inventory sum','44 mapped retained candidates','own-index tracked gate','fresh full hashes','protected prefix metadata');
  physical_allocated_savings='Not measured; no files deleted';deletion_cutoff_utc='2026-10-28T14:35:00Z'})
Get-Content -Raw -LiteralPath (Join-Path $out 'verification.json')
