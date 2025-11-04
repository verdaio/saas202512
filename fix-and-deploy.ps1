# Fix and Deploy Script
# This script will pull the fix and rebuild the containers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pet Care SaaS - Fix and Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop containers
Write-Host "Step 1: Stopping containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml down
Write-Host "✓ Containers stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Pull latest code
Write-Host "Step 2: Pulling latest code..." -ForegroundColor Yellow
git pull origin claude/read-claude-md-011CUoQZk34dyYEvfZmZiuQu
Write-Host "✓ Code updated" -ForegroundColor Green
Write-Host ""

# Step 3: Rebuild API (no cache)
Write-Host "Step 3: Rebuilding API container (this takes 2-3 minutes)..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml build --no-cache api
Write-Host "✓ API rebuilt" -ForegroundColor Green
Write-Host ""

# Step 4: Rebuild Web (no cache)
Write-Host "Step 4: Rebuilding Web container (this takes 2-3 minutes)..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml build --no-cache web
Write-Host "✓ Web rebuilt" -ForegroundColor Green
Write-Host ""

# Step 5: Start all services
Write-Host "Step 5: Starting all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml up -d
Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

# Step 6: Wait for services to be ready
Write-Host "Step 6: Waiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✓ Ready" -ForegroundColor Green
Write-Host ""

# Step 7: Check status
Write-Host "Step 7: Checking status..." -ForegroundColor Yellow
docker-compose -f docker-compose.full.yml ps
Write-Host ""

# Step 8: Show URLs
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test these URLs in your browser:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:3010" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:5410/api/v1/docs" -ForegroundColor White
Write-Host "  Health:    http://localhost:5410/health" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host '  docker-compose -f docker-compose.full.yml logs -f' -ForegroundColor White
Write-Host ""
