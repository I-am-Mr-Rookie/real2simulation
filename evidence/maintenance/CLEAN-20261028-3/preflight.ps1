$ErrorActionPreference='Stop'
$root='C:\Users\HP\Documents\Hackathon\2026-10-26 - Meta Global AI Developer Hackathon'
$prepared='C:\Users\HP\.codex\worktrees\s02g-forensics\2026-10-26 - Meta Global AI Developer Hackathon'
$out=$PSScriptRoot
function Assert($ok,[string]$message){if(-not $ok){throw $message}}
function Save($name,$value){$value|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $out $name) -Encoding utf8}
function Git($path,[string[]]$arguments){$result=@(& git.exe --no-optional-locks -C $path @arguments); Assert ($LASTEXITCODE -eq 0) ('Git failed: '+($arguments -join ' ')); $result}
function Under($path,$parent){[IO.Path]::GetFullPath($path).StartsWith([IO.Path]::GetFullPath($parent).TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)}
function Safe($path){
 $full=[IO.Path]::GetFullPath($path);Assert ((Resolve-Path -LiteralPath $full).ProviderPath -eq $full) 'Resolution differs'
 $node=Get-Item -LiteralPath $full -Force
 while($null -ne $node){Assert (-not ($node.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse rejected';$node=if($node -is [IO.DirectoryInfo]){$node.Parent}else{$node.Directory}}
 $full
}
function Files($path){
 $stack=[Collections.Generic.Stack[string]]::new();$stack.Push($path)
 while($stack.Count){foreach($entry in [IO.DirectoryInfo]::new($stack.Pop()).GetFileSystemInfos()){
  Assert (-not ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)) 'Reparse traversal rejected'
  if($entry -is [IO.DirectoryInfo]){$stack.Push($entry.FullName)}else{$entry}
 }}
}
function Hash($path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Inventory {
 $totals=@{};foreach($f in Files $root){$top=$f.FullName.Substring($root.Length+1).Split('\')[0];if(-not $totals.ContainsKey($top)){$totals[$top]=@{files=0L;bytes=0L}};$totals[$top].files++;$totals[$top].bytes+=$f.Length}
 $rows=@($totals.GetEnumerator()|ForEach-Object{[pscustomobject]@{name=$_.Key;files=$_.Value.files;bytes=$_.Value.bytes}}|Sort-Object name)
 [pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');files=($rows|Measure-Object files -Sum).Sum;logical_bytes=($rows|Measure-Object bytes -Sum).Sum;top_level=$rows}
}
function State($path){[pscustomobject]@{path=$path;head=(Git $path @('rev-parse','HEAD'));branch=(Git $path @('symbolic-ref','HEAD'));status=@(Git $path @('status','--porcelain=v1','--untracked-files=all'));index=@(Git $path @('ls-files','--stage'))}}
function Prefix {
 $prefix=(Get-Content -Raw -LiteralPath (Join-Path $root 'evidence\S07\S07b\recovery3\manifest.json')|ConvertFrom-Json).prefix_directory
 @(Get-ChildItem -LiteralPath $prefix -File -Force|Sort-Object Name|ForEach-Object{[pscustomobject]@{name=$_.Name;bytes=$_.Length;mtime=$_.LastWriteTimeUtc.ToString('o')}})
}
function ProcessCheck {
 $all=@(Get-CimInstance Win32_Process)
 $matches=@($all|Where-Object{
  $p=$_; $p.ProcessId -ne $PID -and $p.CommandLine -and @('S02c','S02c1').Where({$p.CommandLine.Replace('/','\').IndexOf($root+'\.worktrees\'+$_,[StringComparison]::OrdinalIgnoreCase) -ge 0}).Count
 }|Select-Object ProcessId,Name)
 [pscustomobject]@{utc=[DateTime]::UtcNow.ToString('o');processes=$all.Count;matches=$matches;limitation='Sanitized command-line scan plus exclusive file probes, not exhaustive kernel/cwd audit; controller no-live-assignment receipt also required.'}
}
function Objects($head){
 $objects=@(Git $root @('rev-list','--objects','--missing=print',$head));Assert (@($objects|Where-Object{$_ -like '?*' -and $_.StartsWith('?')}).Count -eq 0) 'Missing reachable object'
 $ids=@($objects|ForEach-Object{($_ -split ' ',2)[0]});$checks=@($ids | & git.exe --no-optional-locks -C $root cat-file '--batch-check=%(objectname) %(objecttype) %(objectsize)')
 Assert ($LASTEXITCODE -eq 0 -and $checks.Count -eq $ids.Count -and @($checks|Where-Object{$_ -match ' missing$| ambiguous$'}).Count -eq 0) 'Object metadata check failed'
 [pscustomobject]@{head=$head;reachable_objects=$ids.Count;missing=0;cat_file='PASS'}
}
Assert (Under ($root+'\.worktrees\S02c\x') ($root+'\.worktrees\S02c')) 'Containment positive failed'
Assert (-not (Under ($root+'\.worktrees\S02c1\x') ($root+'\.worktrees\S02c'))) 'Sibling accepted'
Assert (-not (Under ($root+'\.worktrees\S02c\..\x') ($root+'\.worktrees\S02c'))) 'Traversal accepted'
Safe $root|Out-Null;Safe $prepared|Out-Null
Assert ((Git $prepared @('branch','--show-current')) -eq 'run/CLEAN-20261028-3') 'Prepared branch changed'
Save 'prepared-state.json' (State $prepared)
Save 'canonical-before.json' (State $root)
Save 'inventory-before.json' (Inventory)
$prefix=@(Prefix);Assert ($prefix.Count -eq 271) 'Protected prefix count changed';Save 'prefix-before.json' $prefix
$proc=ProcessCheck;Save 'process-before.json' $proc;Assert ($proc.matches.Count -eq 0) 'Possible active process'
$registered=@(Git $root @('worktree','list','--porcelain'));Save 'registration-before.json' $registered
$old=Get-Content -Raw -LiteralPath (Join-Path $prepared 'evidence\maintenance\CLEAN-20261028-2\restoration-map.json')|ConvertFrom-Json
$record=Join-Path $root 'evidence\clips\S02c-acquisition.json';Assert ((Hash $record) -eq $old.acquisition_record_sha256) 'Acquisition record changed'
$records=(Get-Content -Raw -LiteralPath $record|ConvertFrom-Json).files
$targets=@();$maps=@();$preserved=@()
foreach($name in @('S02c','S02c1')){
 $path=Safe (Join-Path $root ('.worktrees\'+$name));Assert (Under $path (Join-Path $root '.worktrees')) 'Target outside exact parent'
 Assert ((Split-Path $path -Leaf) -ceq $name) 'Wrong exact target'
 $block=($registered -join "`n") -split "`n`n"|Where-Object{$_ -match ('(?m)^worktree '+[regex]::Escape($path.Replace('\','/'))+'$')}
 Assert (@($block).Count -eq 1 -and $block -notmatch '(?m)^(locked|prunable|bare)') 'Registration/lock rejected'
 $state=State $path;Assert ($state.branch -eq ('refs/heads/run/'+$name) -and $state.status.Count -eq 0) 'Dirty/wrong branch'
 Assert ((Git $root @('rev-parse',$state.branch)) -eq $state.head) 'Ref mismatch'
 Assert (@($state.index|Where-Object{$_ -match '^160000 '}).Count -eq 0) 'Submodule rejected'
 $admin=(Git $path @('rev-parse','--absolute-git-dir'));Assert (Under $admin (Join-Path $root '.git\worktrees')) 'Not ordinary worktree admin path'
 $files=@(Files $path);Assert (@($files|Where-Object{$_.Name -eq '.git' -and $_.FullName -ne (Join-Path $path '.git')}).Count -eq 0) 'Embedded repository rejected'
 $nested=@(Get-ChildItem -LiteralPath $path -Directory -Recurse -Force|Where-Object{$_.Name -eq '.git'});Assert ($nested.Count -eq 0) 'Embedded Git directory rejected'
 foreach($f in $files){$handle=[IO.File]::Open($f.FullName,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None);$handle.Dispose()}
 $extras=@(Git $path @('ls-files','--others','--ignored','--exclude-standard'));$nonignored=@(Git $path @('ls-files','--others','--exclude-standard'));Assert ($nonignored.Count -eq 0) 'Unexpected nonignored untracked file'
 $allowed=@('Run-System/Runs/S02c/scratch/AP15.m4v.jpg','Run-System/Runs/S02c/scratch/BN01.jpg','Run-System/Runs/S02c/scratch/BN02.webm.jpg','Run-System/Runs/S02c/scratch/FF01.jpg','Run-System/Runs/S02c/scratch/FF01.webm.jpg','Run-System/Runs/S02c/scratch/PD01.jpg','Run-System/Runs/S02c/scratch/PD01.webm.jpg','Run-System/Runs/S02c/scratch/PJ01.webm.jpg','evidence/clips/__pycache__/s02c_v3_analysis.cpython-314.pyc')
 Assert (($name -eq 'S02c' -and $extras.Count -eq 9) -or ($name -eq 'S02c1' -and $extras.Count -eq 0)) 'Unexpected ignored count'
 foreach($rel in $extras){Assert ($rel -cin $allowed -and $name -eq 'S02c') 'Unknown/secret/personal ignored file: STOP'
  if($rel -like '*.jpg'){$stem=(Split-Path $rel -Leaf).Split('.')[0];Assert (@($records|Where-Object{(Split-Path $_.local_path -Leaf).Split('.')[0] -eq $stem}).Count -ge 1) 'Scratch origin not in licensed acquisition record'}
  else{Assert (@(Git $path @('ls-files','--','evidence/clips/s02c_v3_analysis.py')).Count -eq 1) 'Generated cache lacks project source'}
 }
 foreach($m in @($old.maps|Where-Object{Under $_.candidate $path})){
  Safe $m.candidate|Out-Null;Safe $m.canonical|Out-Null
  Assert ((Hash $m.candidate) -eq $m.sha256 -and (Hash $m.canonical) -eq $m.sha256) 'Fresh full media hash mismatch'
  $maps += [pscustomobject]@{historical_path=$m.candidate;canonical=$m.canonical;relative_path=$m.relative_path;bytes=$m.bytes;sha256=$m.sha256;acquisition_match=$m.acquisition_hash_matches;redirect='Use canonical path directly; old tracked path can be restored from retained branch.'}
 }
 foreach($rel in $extras){
  $src=Safe (Join-Path $path $rel);$dst=Join-Path $out ('local-preservation\'+$name+'\'+$rel);Assert (-not (Test-Path -LiteralPath $dst)) 'Preservation destination already exists'
  $ignored=@(& git.exe --no-optional-locks -C $prepared check-ignore -- $dst);Assert ($LASTEXITCODE -eq 0) 'Preservation must be ignored BEFORE copy'
  [IO.Directory]::CreateDirectory((Split-Path $dst -Parent))|Out-Null
  $hash=Hash $src;[IO.File]::Copy($src,$dst,$false);Assert ((Hash $dst) -eq $hash) 'Preservation hash mismatch'
  $preserved += [pscustomobject]@{original=$src;preserved=$dst;relative_path=$rel;bytes=(Get-Item -LiteralPath $src).Length;sha256=$hash;ignored=$true;restore='After restoring branch checkout, copy preserved file to exact original path only if absent, and verify this SHA256. Never overwrite.'}
 }
 $objects=Objects $state.head
 $targets += [pscustomobject]@{path=$path;name=$name;branch=$state.branch;head=$state.head;admin=$admin;state=$state;files=$files.Count;logical_bytes=($files|Measure-Object Length -Sum).Sum;ignored_files=$extras;nonignored_untracked=$nonignored;exclusive_open_probes=$files.Count;objects=$objects;restore_command=('git -C "'+$root+'" worktree add "'+$path+'" "run/'+$name+'"');ancestry_note='Retention of exact branch is recovery; merged ancestry not assumed.'}
}
Assert ($maps.Count -eq 44 -and $preserved.Count -eq 9) 'Coverage mismatch'
Save 'restoration-map.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');acquisition_record_sha256=(Hash $record);tracked_redirects=$maps;ignored_preservation=$preserved;never_archive_prepared_checkout='Local-preservation contains sole ignored scratch backup; keep until explicit restoration decision.'})
Save 'pre-removal-ledger.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');targets=$targets;all_file_probe='PASS';media_hashes=44;preserved_files=9;preserved_bytes=($preserved|Measure-Object bytes -Sum).Sum;removal_not_yet_performed=$true;controller_no_active_assignment_receipt_required=$true})
Save 'preflight-checks.json' @{status='PASS';checks=@('containment positive/sibling/traversal','no reparse/embedded/submodules','ordinary unlocked registration','clean index/retained exact branch','all reachable objects local','44 fresh full hashes','9 ignored byte copies/hash/ignore','exclusive read handles all candidate files','zero process command matches','271 protected JPEG metadata');utc=[DateTime]::UtcNow.ToString('o')}
Write-Output ('PREFLIGHT PASS: '+$targets.Count+' targets; '+$maps.Count+' full hashes; '+$preserved.Count+' ignored preserved')
