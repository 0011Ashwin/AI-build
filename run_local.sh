#!/bin/bash

# Local development startup script

echo "🚀 Starting Justice AI (Local Development)"
echo "=================================================="
echo ""

#Cleanup function to kill background processes on exit
cleanup() {
    echo -e "\n 🛑 Shutting down all Justice AI processes..."
    kill $(jobs -p) 2>/dev/null || true
    echo "✅ All processes stopped. Goodbye!"
    exit 0  
}

# Trap signals for graceful shutdown
trap cleanup SIGINT SIGTERM EXIT

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
GOOGLE_PROJECT_ID=justice-ai-project
GOOGLE_REGION=us-central1
DEBUG=True
PORT=8080
EOF
   echo "✅ .env file created with default values."
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start agents in background
echo "👥 Starting agents..."

# Check and killl port 8080 if already in use
if lsof -i :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8080 is already in use. Killing existing process..."
    sudo kill -9 $(lsof -i :8080 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 2
    echo "✅ Port 8080 has been freed."
fi

# Define agents with their ports
declare -A agent_ports=(
    ["chief_justice"]="8081"
    ["quantitative_auditor"]="8082"
    ["legal_researcher"]="8083"
    ["mitigator_juror"]="8084"
    ["strict_auditor_juror"]="8085"
    ["ethicist_juror"]="8086"
)

for agent in "${!agent_ports[@]}"
do
    port=${agent_ports[$agent]}
    echo "Starting $agent on port $port..."
    cd agents/$agent 2>/dev/null || { echo "❌ Directory agents/$agent not found!"; continue; }

    PORT=$port python adk_app.py &
    cd ../..
    sleep 1.5
done

# Start main app
echo ""
echo "🌐 Starting main application server on port 8080..."
cd app
echo "Running: python main.py"

PORT=8080 python main.py
# Keep script running
wait
