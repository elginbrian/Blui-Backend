@echo off
REM Blui Backend Docker Setup Script for Windows

echo 🚀 Starting Blui Backend with Docker Compose...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed.
    pause
    exit /b 1
)

echo 🐳 Building and starting services...
docker-compose up --build -d

echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Failed to start services. Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Services are running!
    echo.
    echo 🌐 API available at: http://localhost:8000
    echo 📚 Documentation at: http://localhost:8000/docs
    echo 🗄️ Database at: localhost:5432
    echo.
    echo 📋 Useful commands:
    echo   docker-compose logs -f          # View logs
    echo   docker-compose down             # Stop services
    echo   docker-compose restart          # Restart services
)

pause