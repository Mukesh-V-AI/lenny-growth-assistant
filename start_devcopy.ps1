# 1. Kill any existing hanging background processes
Write-Host "Stopping existing servers..."
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Stop-Process -Name "uvicorn" -ErrorAction SilentlyContinue

# 2. Start the FastAPI Backend
Write-Host "Starting Backend..."
Set-Location -Path "backend"
Start-Process -NoNewWindow -FilePath ".\venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app", "--reload", "--port", "8000"
Set-Location -Path ".."

# 3. Start the Next.js Frontend
Write-Host "Starting Frontend..."
Set-Location -Path "frontend"
Start-Process -NoNewWindow -FilePath "npm.cmd" -ArgumentList "run", "dev"
Set-Location -Path ".."

Write-Host "Project successfully restarted!"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend: http://localhost:8000"
