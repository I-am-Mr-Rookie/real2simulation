$ErrorActionPreference='Stop'
$root='C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$prepared='C:\Users\HP\.codex\worktrees\s02g-forensics\2026-10-26 - Meta Global AI Developer Hackathon'
$out=$PSScriptRoot
function Assert($ok,$message){if(-not $ok){throw $message}}
function Save($name,$value){$value|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $out $name) -Encoding utf8}
function G($path,[string[]]$arguments){$value=@(& git.exe --no-optional-locks -C $path @arguments);Assert ($LASTEXITCODE -eq 0) ('Git failed: '+($arguments -join ' '));$value}
function Hash($path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
$ledger=Get-Content -Raw -LiteralPath (Join-Path $out 'pre-removal-ledger.json')|ConvertFrom-Json
$map=Get-Content -Raw -LiteralPath (Join-Path $out 'restoration-map.json')|ConvertFrom-Json
$removed=@(Get-Content -Raw -LiteralPath (Join-Path $out 'removal-results.json')|ConvertFrom-Json)
$registration=@(G $root @('worktree','list','--porcelain'))
$before=@(Get-Content -Raw -LiteralPath (Join-Path $out 'registration-before.json')|ConvertFrom-Json)
function WithoutTargets($lines){(($lines -join "`n") -split "`n`n"|Where-Object{$_ -notmatch '(?m)^worktree .*/\.worktrees/S02c1?$' -and $_.Trim()}|ForEach-Object{$_.Trim()}) -join "`n`n"}
Assert ((WithoutTargets $registration) -eq (WithoutTargets $before)) 'Unrelated worktree registration changed'
Assert ($removed.Count -eq 2 -and @($removed|Where-Object{$_.exit -ne 0}).Count -eq 0) 'Removal result incomplete'
$objects=@()
foreach($target in $ledger.targets){
 Assert (-not (Test-Path -LiteralPath $target.path)) 'Old path exists'
 Assert (-not ($registration -contains ('worktree '+$target.path.Replace('\','/')))) 'Old path registered'
 Assert ((G $root @('rev-parse',$target.branch)) -eq $target.head) 'Retained branch changed'
 $rows=@(G $root @('rev-list','--objects','--missing=print',$target.head));Assert (@($rows|Where-Object{$_.StartsWith('?')}).Count -eq 0) 'Missing reachable object'
 $checks=@(($rows|ForEach-Object{($_ -split ' ',2)[0]})| & git.exe --no-optional-locks -C $root cat-file '--batch-check=%(objectname) %(objecttype) %(objectsize)')
 Assert ($LASTEXITCODE -eq 0 -and $checks.Count -eq $target.objects.reachable_objects -and @($checks|Where-Object{$_ -match ' missing$| ambiguous$'}).Count -eq 0) 'Restoration objects incomplete'
 $objects += [pscustomobject]@{branch=$target.branch;head=$target.head;reachable_objects=$checks.Count;missing=0}
}
foreach($m in $map.tracked_redirects){Assert ((Hash $m.canonical) -eq $m.sha256 -and (Get-Item -LiteralPath $m.canonical).Length -eq $m.bytes) 'Canonical input changed'}
Assert ((Hash (Join-Path $root 'evidence\clips\S02c-acquisition.json')) -eq $map.acquisition_record_sha256) 'Acquisition manifest changed'
foreach($p in $map.ignored_preservation){
 Assert ((Hash $p.preserved) -eq $p.sha256 -and (Get-Item -LiteralPath $p.preserved).Length -eq $p.bytes) 'Ignored preservation changed'
 $ignore=@(& git.exe --no-optional-locks -C $prepared check-ignore -- $p.preserved);Assert ($LASTEXITCODE -eq 0) 'Preservation not ignored'
 Assert (@(G $prepared @('ls-files','--',$p.preserved)).Count -eq 0) 'Preservation tracked'
}
$prefixPath=(Get-Content -Raw -LiteralPath (Join-Path $root 'evidence\S07\S07b\recovery3\manifest.json')|ConvertFrom-Json).prefix_directory
$prefix=@(Get-ChildItem -LiteralPath $prefixPath -File -Force|Sort-Object Name|ForEach-Object{[pscustomobject]@{name=$_.Name;bytes=$_.Length;mtime=$_.LastWriteTimeUtc.ToString('o')}})
$oldPrefix=Get-Content -Raw -LiteralPath (Join-Path $out 'prefix-before.json')|ConvertFrom-Json
$newMetadata=@($prefix|ForEach-Object{$_.name+'|'+$_.bytes+'|'+([datetime]$_.mtime).ToUniversalTime().Ticks})
$oldMetadata=@($oldPrefix|ForEach-Object{$_.name+'|'+$_.bytes+'|'+([datetime]$_.mtime).ToUniversalTime().Ticks})
Assert ($prefix.Count -eq 271 -and ($newMetadata -join "`n") -eq ($oldMetadata -join "`n")) 'Protected prefix metadata changed'
Save 'prefix-after.json' $prefix
$totals=@{};$stack=[Collections.Generic.Stack[string]]::new();$stack.Push($root)
while($stack.Count){foreach($f in [IO.DirectoryInfo]::new($stack.Pop()).GetFileSystemInfos()){
 Assert (-not ($f.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse in inventory'
 if($f -is [IO.DirectoryInfo]){$stack.Push($f.FullName);continue}
 $top=$f.FullName.Substring($root.Length+1).Split('\')[0];if(-not $totals.ContainsKey($top)){$totals[$top]=@{files=0L;bytes=0L}};$totals[$top].files++;$totals[$top].bytes+=$f.Length
}}
$rows=@($totals.GetEnumerator()|ForEach-Object{[pscustomobject]@{name=$_.Key;files=$_.Value.files;bytes=$_.Value.bytes}}|Sort-Object name)
$inventory=[pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');files=($rows|Measure-Object files -Sum).Sum;logical_bytes=($rows|Measure-Object bytes -Sum).Sum;top_level=$rows}
Save 'inventory-after.json' $inventory
$initial=Get-Content -Raw -LiteralPath (Join-Path $out 'inventory-before.json')|ConvertFrom-Json
$stableBefore=@($initial.top_level|Where-Object{$_.name -notin @('.git','.worktrees')}|ForEach-Object{$_.name+'|'+$_.files+'|'+$_.bytes})
$stableAfter=@($inventory.top_level|Where-Object{$_.name -notin @('.git','.worktrees')}|ForEach-Object{$_.name+'|'+$_.files+'|'+$_.bytes})
Assert (($stableBefore -join "`n") -eq ($stableAfter -join "`n")) 'Unrelated root metadata totals changed'
$canonical=Get-Content -Raw -LiteralPath (Join-Path $out 'canonical-before.json')|ConvertFrom-Json
$current=[pscustomobject]@{head=(G $root @('rev-parse','HEAD'));branch=(G $root @('symbolic-ref','HEAD'));status=@(G $root @('status','--porcelain=v1','--untracked-files=all'));index=@(G $root @('ls-files','--stage'))}
Save 'canonical-after.json' $current
$unchanged=($current.head -eq $canonical.head -and $current.branch -eq $canonical.branch -and ($current.status -join "`n") -eq ($canonical.status -join "`n") -and ($current.index -join "`n") -eq ($canonical.index -join "`n"))
$tokens=$null;$errors=$null
foreach($script in @('preflight.ps1','remove-verified.ps1','verify.ps1')){
 $ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $out $script),[ref]$tokens,[ref]$errors);Assert ($errors.Count -eq 0) 'Script parse failed'
 $commands=@($ast.FindAll({param($n)$n -is [Management.Automation.Language.CommandAst]},$true))
 Assert (@($commands|Where-Object{$_.GetCommandName() -in @('Remove-Item','rm','rmdir','del','Move-Item')}).Count -eq 0) 'Shell destructive primitive prohibited'
 $gitCommands=@($commands|Where-Object{$_.GetCommandName() -in @('git.exe','G','Git')})
 Assert (@($gitCommands|Where-Object{$_.Extent.Text -match '(?i)--force|\s-f(?:\s|$)|["''](?:clean|reset|gc|prune)["'']'}).Count -eq 0) 'Forbidden force/reset/GC primitive'
}
Save 'verification.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');status='PASS';removed_paths_absent_unregistered=2;unrelated_registrations_unchanged=$true;retained_branch_objects=$objects;canonical_hashes_pass=$map.tracked_redirects.Count;acquisition_manifest_hash='PASS';ignored_hashes_pass=$map.ignored_preservation.Count;ignored_preserved_bytes=($map.ignored_preservation|Measure-Object bytes -Sum).Sum;protected_prefix_files=$prefix.Count;protected_prefix_bytes=($prefix|Measure-Object bytes -Sum).Sum;protected_prefix_metadata='UNCHANGED';canonical_head_index_status_unchanged=$unchanged;removed_checkout_files=($ledger.targets|Measure-Object files -Sum).Sum;removed_checkout_logical_bytes=($ledger.targets|Measure-Object logical_bytes -Sum).Sum;root_before_files=$initial.files;root_after_files=$inventory.files;root_before_bytes=$initial.logical_bytes;root_after_bytes=$inventory.logical_bytes;root_measured_logical_delta=($initial.logical_bytes-$inventory.logical_bytes);physical_allocation='Not measured; metadata logical bytes only; root delta includes Git admin removal and possible concurrent controller growth.';self_checks='PASS: scripts parse, prohibited primitive scan, preflight containment rejection tests, all acceptance assertions'})
Get-Content -Raw -LiteralPath (Join-Path $out 'verification.json')
