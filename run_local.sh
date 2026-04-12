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

agents=("chief_justice" "quantitative_auditor" "legal_researcher" "mitigator_juror" "strict_auditor_juror" "ethicist_juror")

for agent in "${agents[@]}"
do
    echo "Starting $agent..."
    cd agents/$agent
    python adk_app.py &
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
