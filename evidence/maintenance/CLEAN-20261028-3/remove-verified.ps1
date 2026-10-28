param([switch]$Execute)
$ErrorActionPreference='Stop'
if(-not $Execute){throw 'Explicit -Execute required; do not rerun after successful removal.'}
$root='C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$out=$PSScriptRoot
$ledger=Get-Content -Raw -LiteralPath (Join-Path $out 'pre-removal-ledger.json')|ConvertFrom-Json
$map=Get-Content -Raw -LiteralPath (Join-Path $out 'restoration-map.json')|ConvertFrom-Json
function Assert($ok,$message){if(-not $ok){throw $message}}
function Save($name,$value){$value|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $out $name) -Encoding utf8}
function G($path,[string[]]$arguments){$value=@(& git.exe --no-optional-locks -C $path @arguments);Assert ($LASTEXITCODE -eq 0) ('Git failed: '+($arguments -join ' '));$value}
function Hash($path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Files($path){
 $stack=[Collections.Generic.Stack[string]]::new();$stack.Push($path)
 while($stack.Count){foreach($f in [IO.DirectoryInfo]::new($stack.Pop()).GetFileSystemInfos()){
  Assert (-not ($f.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse rejected'
  if($f -is [IO.DirectoryInfo]){$stack.Push($f.FullName)}else{$f}
 }}
}
function ProcessCheck {
 $all=@(Get-CimInstance Win32_Process)
 $matches=@($all|Where-Object{$p=$_;$p.ProcessId -ne $PID -and $p.CommandLine -and @('S02c','S02c1').Where({$p.CommandLine.Replace('/','\').IndexOf($root+'\.worktrees\'+$_,[StringComparison]::OrdinalIgnoreCase) -ge 0}).Count}|Select-Object ProcessId,Name)
 [pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');observed=$all.Count;matches=$matches}
}
Assert (Test-Path -LiteralPath (Join-Path $out 'coordination.md')) 'Controller receipt missing'
Assert ($ledger.targets.Count -eq 2 -and $map.tracked_redirects.Count -eq 44 -and $map.ignored_preservation.Count -eq 9) 'Ledger incomplete'
$results=@()
foreach($target in $ledger.targets){
 Assert ([DateTime]::UtcNow -lt [DateTime]'2026-10-28T15:15:06Z') 'Deletion cutoff reached'
 $expected=Join-Path $root ('.worktrees\'+$target.name)
 Assert ($target.name -cin @('S02c','S02c1') -and $target.path -ceq $expected) 'Exact target rejected'
 $resolved=(Resolve-Path -LiteralPath $target.path).ProviderPath;Assert ($resolved -ceq $expected) 'Resolved target changed'
 $node=Get-Item -LiteralPath $resolved -Force
 while($node){Assert (-not ($node.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse parent rejected';$node=$node.Parent}
 $registration=@(G $root @('worktree','list','--porcelain'))
 $block=($registration -join "`n") -split "`n`n"|Where-Object{$_ -match ('(?m)^worktree '+[regex]::Escape($resolved.Replace('\','/'))+'$')}
 Assert (@($block).Count -eq 1 -and $block -notmatch '(?m)^(locked|prunable|bare)') 'Registration changed'
 Assert ((G $target.path @('rev-parse','--absolute-git-dir')) -eq $target.admin) 'Admin changed'
 $proc=ProcessCheck;Save ('process-immediate-'+$target.name+'.json') $proc;Assert ($proc.matches.Count -eq 0) 'Possible active use'
 $files=@(Files $resolved);Assert ($files.Count -eq $target.files -and ($files|Measure-Object Length -Sum).Sum -eq $target.logical_bytes) 'File inventory changed'
 foreach($f in $files){$h=[IO.File]::Open($f.FullName,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None);$h.Dispose()}
 foreach($m in $map.tracked_redirects|Where-Object{$_.historical_path.StartsWith($resolved+'\',[StringComparison]::OrdinalIgnoreCase)}){
  Assert ((Hash $m.historical_path) -eq $m.sha256 -and (Hash $m.canonical) -eq $m.sha256) 'Media changed'
 }
 foreach($p in $map.ignored_preservation){Assert ((Hash $p.preserved) -eq $p.sha256) 'Preserved bytes changed';if($p.original.StartsWith($resolved+'\',[StringComparison]::OrdinalIgnoreCase)){Assert ((Hash $p.original) -eq $p.sha256) 'Ignored original changed'}}
 $extras=@(G $resolved @('ls-files','--others','--ignored','--exclude-standard'));Assert (($extras -join "`n") -eq ($target.ignored_files -join "`n")) 'Ignored list changed'
 Assert (@(G $resolved @('ls-files','--others','--exclude-standard')).Count -eq 0) 'Nonignored extras appeared'
 Assert ((G $root @('rev-parse',$target.branch)) -eq $target.head) 'Retained ref changed'
 Assert ((G $resolved @('rev-parse','HEAD')) -eq $target.head -and (G $resolved @('symbolic-ref','HEAD')) -eq $target.branch) 'HEAD changed'
 Assert (@(G $resolved @('status','--porcelain=v1','--untracked-files=all')).Count -eq 0) 'Worktree dirty'
 Assert (((G $resolved @('ls-files','--stage')) -join "`n") -eq ($target.state.index -join "`n")) 'Index changed'
 Assert ([DateTime]::UtcNow -lt [DateTime]'2026-10-28T15:15:06Z') 'Deletion cutoff reached'
 Save ('immediate-pre-removal-'+$target.name+'.json') @{utc=[DateTime]::UtcNow.ToString('o');path=$resolved;head=$target.head;status='clean';files=$files.Count;exclusive_probes='PASS';hashes='PASS';command='git worktree remove -- exact-path; no force'}
 # Only Git performs removal; no shell recursive deletion or retry after refusal.
 $start=[DateTime]::UtcNow.ToString('o');$output=@(& git.exe -C $root worktree remove -- $resolved 2>&1);$exit=$LASTEXITCODE
 $result=[pscustomobject]@{path=$resolved;started_at=$start;ended_at=[DateTime]::UtcNow.ToString('o');exit=$exit;output=@($output|ForEach-Object{"$_"});logical_bytes=$target.logical_bytes;files=$target.files}
 $results+=$result;Save 'removal-results.json' $results
 Assert ($exit -eq 0) 'Git refused: STOP; no force/retry/manual deletion'
 Assert (-not (Test-Path -LiteralPath $resolved)) 'Removed path still exists'
 $after=@(G $root @('worktree','list','--porcelain'));Assert (-not ($after -contains ('worktree '+$resolved.Replace('\','/')))) 'Still registered'
 Assert ((G $root @('rev-parse',$target.branch)) -eq $target.head) 'Branch ref changed after removal'
}
Save 'registration-after.json' @(G $root @('worktree','list','--porcelain'))
Write-Output ('NORMAL GIT REMOVAL PASS: '+$results.Count+' exact targets')
