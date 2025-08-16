#!/bin/bash

# Sports Betting AI - Setup Script
echo "🏈 Setting up Sports Betting AI System..."
echo "========================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"

# Check if we're in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Running in virtual environment: $VIRTUAL_ENV"
else
    echo "⚠️  Not in virtual environment. Consider running:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate  # On Mac/Linux"
    echo "   venv\\Scripts\\activate     # On Windows"
fi

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip install flask flask-cors flask-sqlalchemy pandas numpy scikit-learn xgboost python-dotenv joblib

# Create directories
echo ""
echo "📁 Creating project directories..."
mkdir -p models
mkdir -p logs

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully!')
"

# Generate sample data
echo ""
echo "📊 Generating sample data for testing..."
python -c "
from app import create_app
from app.ml.data_processor import DataProcessor
from app.models import Bankroll
from app import db

app = create_app()
with app.app_context():
    # Create initial bankroll
    bankroll = Bankroll.query.first()
    if not bankroll:
        bankroll = Bankroll(
            current_balance=1000.0,
            starting_balance=1000.0,
            max_daily_loss=100.0
        )
        db.session.add(bankroll)
        db.session.commit()
    
    # Generate sample data
    processor = DataProcessor()
    result = processor.generate_historical_data('americanfootball_nfl', 30)
    print(f'✅ Generated {result.get(\"generated_games\", 0)} sample games')
"

# Test ML model creation
echo ""
echo "🧠 Testing ML model setup..."
python -c "
from app import create_app
from app.ml.prediction_model import PredictionModel

app = create_app()
with app.app_context():
    model = PredictionModel()
    print('✅ ML model initialized successfully!')
"

# Check frontend setup
echo ""
echo "🌐 Checking frontend setup..."
if [ -d "frontend" ]; then
    echo "✅ Frontend directory exists"
    if [ -f "frontend/package.json" ]; then
        echo "✅ package.json found"
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "📦 Installing frontend dependencies..."
            npm install
        else
            echo "✅ Frontend dependencies already installed"
        fi
        cd ..
    else
        echo "⚠️  package.json not found in frontend directory"
    fi
else
    echo "⚠️  Frontend directory not found"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🚀 To start the application:"
echo "1. Backend:  python run.py"
echo "2. Frontend: cd frontend && npm start"
echo "3. Open:     http://localhost:3000"
echo ""
echo "🔧 Available CLI commands:"
echo "   python run.py init-db          # Initialize database"
echo "   python run.py generate-data    # Generate sample data"
echo "   python run.py train-model      # Train ML models"
echo "   python run.py update-games     # Fetch latest odds"
echo "   python run.py daily-analysis   # Run betting analysis"
echo "   python run.py backtest         # Test strategy"
echo ""
echo "📚 See README.md for detailed documentation"
echo ""
echo "⚠️  Remember: This is for educational purposes only!"
echo "   • Never bet more than you can afford to lose"
echo "   • Ensure sports betting is legal in your area"
echo "   • Past performance doesn't guarantee future results"
