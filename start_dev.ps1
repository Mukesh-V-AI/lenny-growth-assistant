# Start Script for Lenny Growth Assistant
echo "Starting PostgreSQL..."
docker-compose up -d

echo "Setting up Python Virtual Environment..."
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

echo "Starting Backend API..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\activate; uvicorn app.main:app --reload"

echo "Installing frontend dependencies..."
cd ..\frontend
npm install

echo "Starting Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

echo "Lenny Growth Assistant is running!"
