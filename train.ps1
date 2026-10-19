Set-Location $PSScriptRoot
python train.py --device auto --batch 4 @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
