Param(
    [switch]$DryRun,
    [switch]$AutoContinue,
    [string]$Remote = "fork",
    [string]$Branch = "feature/emitiq-scaffold"
)

$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$backupDir = ".git/merge_conflict_backups_$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Find files containing conflict markers, ignoring .git
$conflictFiles = Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\.git' } | Select-String '<<<<<<< ' -List | Select-Object -ExpandProperty Path -Unique

if (-not $conflictFiles) {
    Write-Host "No conflict markers found."; exit 0
}

foreach ($file in $conflictFiles) {
    Copy-Item -Path $file -Destination $backupDir -Force
    $text = Get-Content -Raw -Encoding UTF8 -LiteralPath $file
    $pattern = '(?s)<<<<<<<.*?\r?\n(.*?)\r?\n=======(.*?)\r?\n>>>>>>>.*?(?:\r?\n|$)'
    $replaced = [regex]::Replace($text, $pattern, {
        param($m)
        $left = $m.Groups[1].Value.TrimEnd("`r","`n")
        $right = $m.Groups[2].Value.TrimStart("`r","`n")
        return $left + "`r`n" + $right
    })
    if ($replaced -ne $text) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would update $file"
        } else {
            Set-Content -Encoding UTF8 -Value $replaced -LiteralPath $file
            git add -- $file
            Write-Host "Resolved and staged $file"
        }
    } else {
        Write-Host "No conflict blocks replaced in $file"
    }
}

if ($DryRun) {
    Write-Host "Dry run complete. Backups in $backupDir"; exit 0
}

if ($AutoContinue) {
    while ($true) {
        $res = git rebase --continue 2>&1
        $code = $LASTEXITCODE
        Write-Host $res
        if ($code -eq 0) { break }
        if ($res -match 'No rebase in progress') { break }
        if ($res -match 'resolve the conflicts' -or $res -match 'fix conflicts and then') {
            Write-Host "Conflicts remain after automated resolution. Stopping for manual intervention."; exit 1
        }
        Start-Sleep -Seconds 1
    }
}

Write-Host "Done. If rebase finished, run: git push --force $Remote $Branch"
