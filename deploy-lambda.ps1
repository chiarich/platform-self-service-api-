# -------------------------------
# AWS Lambda Build & Deploy Script
# -------------------------------

# 1️⃣ Set paths
\C:\Users\lichi\Documents\GitHub\Platform Self-Service API = "C:\Users\lichi\Documents\GitHub\Platform Self-Service API"
\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build = "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build"
\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist = "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist"
\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist\lambda.zip = "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist\lambda.zip"

# 2️⃣ Clean previous build
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build
Remove-Item -Force -ErrorAction SilentlyContinue \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist\lambda.zip

# 3️⃣ Recreate build directories
New-Item -ItemType Directory -Force -Path \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build
New-Item -ItemType Directory -Force -Path "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build\app"

# 4️⃣ Copy your application code
Copy-Item -Path "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\app\*" -Destination "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build\app" -Recurse -Force

# 5️⃣ Ensure main.py is at the root of build/ for Lambda
Copy-Item -Path "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\app\main.py" -Destination "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build\main.py" -Force

# 6️⃣ Install Python dependencies into build/
pip install fastapi mangum pydantic -t \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build

# 7️⃣ Create dist directory if it doesn’t exist
If (-Not (Test-Path \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist)) { New-Item -ItemType Directory -Force -Path \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist }

# 8️⃣ Package everything into Lambda ZIP
Compress-Archive -Path "\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\build\*" -DestinationPath \C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist\lambda.zip -Force

# 9️⃣ Update Lambda function
aws lambda update-function-code --function-name platform-api-dev --zip-file "fileb://\C:\Users\lichi\Documents\GitHub\Platform Self-Service API\dist\lambda.zip"

Write-Host "✅ Lambda function updated successfully!"
