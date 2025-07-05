
param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host "                    FastAPI-HTMX - Setup Script                " -ForegroundColor Blue
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  setup           - Complete project setup" -ForegroundColor Yellow
    Write-Host "  install         - Install dependencies only" -ForegroundColor Yellow
    Write-Host "  env             - Create .env file" -ForegroundColor Yellow
    Write-Host "  migrate         - Run database migrations" -ForegroundColor Yellow
    Write-Host "  init-db         - Initialize database with migrations" -ForegroundColor Yellow
    Write-Host "  run             - Start the application" -ForegroundColor Yellow
    Write-Host "  run-dev         - Start in development mode" -ForegroundColor Yellow
    Write-Host "  credentials     - Show admin login credentials" -ForegroundColor Yellow
    Write-Host "  status          - Show project status" -ForegroundColor Yellow
    Write-Host "  clean           - Clean up generated files" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [command]" -ForegroundColor Magenta
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    if (Get-Command poetry -ErrorAction SilentlyContinue) {
        poetry install
    } else {
        pip install -r requirements.txt
    }
    Write-Host "Dependencies installed!" -ForegroundColor Green
}

function Create-EnvFile {
    Write-Host "Creating .env file..." -ForegroundColor Blue
    if (-not (Test-Path ".env")) {
        $envContent = @"
# Database Configuration
DATABASE_URL="sqlite+aiosqlite:///./users.db"
SECRET_KEY="super-secret-key-example-123456789"

# MinIO Configuration (Required for file uploads)
MINIO_URL="http://localhost:9000"
MINIO_ACCESS_KEY="minioadmin123456789"
MINIO_SECRET_KEY="miniosecret987654321xyz"
MINIO_BUCKET="my-fastapi-bucket"
MINIO_SECURE=false

# CSRF Protection
CSRF_SECRET_KEY="csrf-secret-key-example-987654321"
COOKIE_SAMESITE="lax"
COOKIE_SECURE=true
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host ".env file created!" -ForegroundColor Green
    } else {
        Write-Host ".env file already exists, skipping..." -ForegroundColor Yellow
    }
}

function Run-Migrations {
    Write-Host "Running database migrations..." -ForegroundColor Blue
    
    # Check if this is the first time (no migration files exist)
    $migrationsPath = "app\migrations\versions"
    $migrationFiles = Get-ChildItem -Path $migrationsPath -Filter "*.py" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "__init__.py" }
    
    if (-not $migrationFiles) {
        Write-Host "No migration files found. Creating initial migration..." -ForegroundColor Yellow
        
        # Create initial migration
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            poetry run alembic revision --autogenerate -m "Initial migration"
        } else {
            alembic revision --autogenerate -m "Initial migration"
        }
        
        # Find the newly created migration file
        $newMigrationFiles = Get-ChildItem -Path $migrationsPath -Filter "*.py" -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "__init__.py" }
        
        if ($newMigrationFiles) {
            $latestMigration = $newMigrationFiles | Sort-Object CreationTime -Descending | Select-Object -First 1
            Write-Host "Adding required imports to migration file: $($latestMigration.Name)" -ForegroundColor Yellow
            
            # Read the migration file content
            $migrationContent = Get-Content $latestMigration.FullName -Raw
            
            # Check if imports are already present
            if ($migrationContent -notmatch "import fastapi_users_db_sqlalchemy.generics" -or $migrationContent -notmatch "import app.models.groups") {
                # Find the line with existing imports and add our imports after it
                $lines = Get-Content $latestMigration.FullName
                $newLines = @()
                $importsAdded = $false
                
                foreach ($line in $lines) {
                    $newLines += $line
                    
                    # Add imports after the revision identifiers but before the main imports
                    if ($line -match "^# Revision ID:" -and -not $importsAdded) {
                        # Find the end of the header comments and add imports
                        continue
                    }
                    
                    if ($line -match "^from alembic import op" -and -not $importsAdded) {
                        $newLines += "import fastapi_users_db_sqlalchemy.generics"
                        $newLines += "import app.models.groups"
                        $newLines += ""
                        $importsAdded = $true
                    }
                }
                
                # Write the updated content back to the file
                $newLines | Set-Content $latestMigration.FullName -Encoding UTF8
                Write-Host "Required imports added to migration file!" -ForegroundColor Green
            } else {
                Write-Host "Required imports already present in migration file." -ForegroundColor Green
            }
        }
    }
    
    # Run the migrations
    if (Get-Command poetry -ErrorAction SilentlyContinue) {
        poetry run alembic upgrade head
    } else {
        alembic upgrade head
    }
    
    Write-Host "Migrations completed!" -ForegroundColor Green
}

function Initialize-Database {
    Write-Host "Initializing database with migrations..." -ForegroundColor Blue
    
    # Check if alembic is initialized
    if (-not (Test-Path "alembic.ini")) {
        Write-Host "Alembic not initialized. Please run 'alembic init' first." -ForegroundColor Red
        return
    }
    
    # Create initial migration if none exist
    $migrationsPath = "app\migrations\versions"
    if (-not (Test-Path $migrationsPath)) {
        New-Item -ItemType Directory -Path $migrationsPath -Force | Out-Null
    }
    
    Run-Migrations
}


function Start-App {
    Write-Host "Starting FastAPI-HTMX..." -ForegroundColor Green
    Write-Host "Application will be available at: http://127.0.0.1:8000" -ForegroundColor Blue
    Show-Credentials
    poetry run python main.py
}

function Start-DevApp {
    Write-Host "Starting FastAPI-HTMX in development mode..." -ForegroundColor Green
    Write-Host "Application will be available at: http://127.0.0.1:8000" -ForegroundColor Blue
    Write-Host "Auto-reload enabled" -ForegroundColor Blue
    Show-Credentials
    uvicorn app.app:app --reload --host 127.0.0.1 --port 8000
}

function Show-Credentials {
    Write-Host "Admin Login Credentials" -ForegroundColor Blue
    Write-Host "Email: superuser@admin.com" -ForegroundColor Green
    Write-Host "Password: password123" -ForegroundColor Green
    Write-Host "URL: http://127.0.0.1:8080" -ForegroundColor Blue
}

function Show-Status {
    Write-Host "Project Status" -ForegroundColor Blue
    Write-Host "Project: FastAPI-HTMX" -ForegroundColor Blue
    
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "Python: $pythonVersion" -ForegroundColor Blue
    } catch {
        Write-Host "Python: Not found" -ForegroundColor Red
    }
    
    if (Get-Command poetry -ErrorAction SilentlyContinue) {
        try {
            $poetryVersion = poetry --version
            Write-Host "Poetry: $poetryVersion" -ForegroundColor Blue
        } catch {
            Write-Host "Poetry: Found but error getting version" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Poetry: Not found" -ForegroundColor Yellow
    }
    
    if (Test-Path 'users.db') {
        Write-Host "Database: Exists" -ForegroundColor Green
    } else {
        Write-Host "Database: Not found" -ForegroundColor Yellow
    }
    
    if (Test-Path '.env') {
        Write-Host "Environment: Configured" -ForegroundColor Green
    } else {
        Write-Host "Environment: Not configured" -ForegroundColor Yellow
    }
}

function Clean-Project {
    Write-Host "Cleaning up..." -ForegroundColor Blue
    
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    if (Test-Path ".pytest_cache") {
        Remove-Item ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

function Complete-Setup {
    Write-Host "Starting complete project setup..." -ForegroundColor Green
    Install-Dependencies
    Create-EnvFile
    Run-Migrations
    Write-Host "Setup complete! Run '.\setup.ps1 run' to start the application." -ForegroundColor Green
    Show-Credentials
}

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Complete-Setup }
    "install" { Install-Dependencies }
    "env" { Create-EnvFile }
    "migrate" { Run-Migrations }
    "init-db" { Initialize-Database }
    "run" { Start-App }
    "run-dev" { Start-DevApp }
    "credentials" { Show-Credentials }
    "status" { Show-Status }
    "clean" { Clean-Project }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help 
    }
}