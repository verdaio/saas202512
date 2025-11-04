Write-Host "Deploying Pet Care SaaS with fixes..." -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Stopping containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml down

Write-Host "[2/5] Pulling latest fixes..." -ForegroundColor Yellow
git pull origin claude/read-claude-md-011CUoQZk34dyYEvfZmZiuQu

Write-Host "[3/5] Rebuilding containers (takes 4-5 min)..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml build --no-cache

Write-Host "[4/5] Starting all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml up -d

Write-Host "[5/5] Waiting 30 seconds for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Checking status..." -ForegroundColor Cyan
docker-compose -f docker-compose.full.yml ps

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test these URLs:" -ForegroundColor Yellow
Write-Host "  http://localhost:3010" -ForegroundColor White
Write-Host "  http://localhost:5410/health" -ForegroundColor White
Write-Host "  http://localhost:5410/api/v1/docs" -ForegroundColor White
