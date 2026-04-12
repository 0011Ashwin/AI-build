#!/bin/bash

# Setup script for Justice AI Workflow

echo "⚖️  Justice AI Workflow Setup"
echo "=============================="
echo ""

# Create project directories
echo "📁 Creating project structure..."

mkdir -p data/case_files
mkdir -p data/legal_precedents
mkdir -p logs
mkdir -p reports
mkdir -p cache

# Copy shared utilities to each agent
echo "🔗 Linking shared utilities..."

agents=("chief_justice" "quantitative_auditor" "legal_researcher" "mitigator_juror" "strict_auditor_juror" "ethicist_juror")

for agent in "${agents[@]}"
do
    if [ ! -L "agents/$agent/../shared" ]; then
        ln -s ../shared agents/$agent/shared 2>/dev/null || true
    fi
done

# Create environment configuration
echo "⚙️  Creating configuration files..."

cat > .env.local << 'EOF'
# Google Cloud Configuration
GOOGLE_PROJECT_ID=justice-ai-project
GOOGLE_REGION=us-central1
GOOGLE_CREDENTIALS_PATH=.gcp/service-account.json

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Database & Storage
VECTOR_DB_TYPE=vertex-ai-vector-search
CASE_DB_URI=postgresql://localhost/justice_ai

# Feature Flags
ENABLE_RAG=true
ENABLE_JURY_DEBATE=true
ENABLE_PDF_GENERATION=true

# Logging
LOG_LEVEL=INFO
DEBUG=False
EOF

# Create .gitignore
echo "📝 Creating .gitignore..."

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.venv/
venv/

# Environment
.env
.env.local
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/
reports/
logs/
cache/
.gcp/

# OS
.DS_Store
Thumbs.db
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set up Google Cloud credentials:"
echo "   mkdir -p .gcp"
echo "   cp /path/to/service-account.json .gcp/"
echo ""
echo "2. Update .env.local with your configuration"
echo ""
echo "3. Start the system:"
echo "   docker-compose up"
echo "   or"
echo "   bash run_local.sh"
