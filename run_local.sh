#!/bin/bash

# Local development startup script

echo "🚀 Starting Justice AI Workflow (Local Development)"
echo "=================================================="
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
GOOGLE_PROJECT_ID=justice-ai-project
GOOGLE_REGION=us-central1
DEBUG=True
EOF
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start agents in background
echo "👥 Starting agents..."

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
    echo "Starting $agent on port ${agent_ports[$agent]}..."
    cd agents/$agent
    PORT=${agent_ports[$agent]} python adk_app.py &
    cd ../..
    sleep 2
done

# Start main app
echo ""
echo "🌐 Starting main application server..."
cd app
python main.py

# Keep script running
wait
