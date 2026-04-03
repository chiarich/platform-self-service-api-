# --------------------------------------------
# AWS Lambda Full Build & Deploy Script (PowerShell)
# --------------------------------------------

# 1️⃣ Set paths
$ProjectRoot = "C:\Users\lichi\Documents\GitHub\Platform Self-Service API"
$BuildDir    = "$ProjectRoot\build"
$DistDir     = "$ProjectRoot\dist"
$ZipFile     = "$DistDir\lambda.zip"

# 2️⃣ Clean previous build and zip
Write-Host "🧹 Cleaning previous build..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $BuildDir
Remove-Item -Force -ErrorAction SilentlyContinue $ZipFile

# 3️⃣ Recreate build directories
Write-Host "📂 Creating build directories..."
New-Item -ItemType Directory -Force -Path $BuildDir
New-Item -ItemType Directory -Force -Path "$BuildDir\app"

# 4️⃣ Copy application code
Write-Host "📋 Copying application code..."
Copy-Item -Path "$ProjectRoot\app\*" -Destination "$BuildDir\app" -Recurse -Force

# 5️⃣ Ensure main.py is at the root of build/ for Lambda
Copy-Item -Path "$ProjectRoot\app\main.py" -Destination "$BuildDir\main.py" -Force

# (Optional) If you have service.py at root
# Copy-Item -Path "$ProjectRoot\app\service.py" -Destination "$BuildDir\service.py" -Force

# 6️⃣ Install Python dependencies into build/
Write-Host "📦 Installing Python dependencies..."
pip install fastapi mangum pydantic -t $BuildDir

# 7️⃣ Create dist directory if it doesn’t exist
If (-Not (Test-Path $DistDir)) { New-Item -ItemType Directory -Force -Path $DistDir }

# 8️⃣ Package everything into Lambda ZIP
Write-Host "🗜️ Packaging Lambda ZIP..."
Compress-Archive -Path "$BuildDir\*" -DestinationPath $ZipFile -Force

# 9️⃣ Update Lambda function
Write-Host "🚀 Updating Lambda function..."
aws lambda update-function-code --function-name platform-api-dev --zip-file "fileb://$ZipFile"

Write-Host "✅ Lambda function updated successfully!"