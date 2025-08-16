# 🤖 ApexAnalytics AI - Sports Betting Intelligence Platform

A cutting-edge sports betting AI platform that combines advanced machine learning, real-time data integration, and intelligent risk assessment to provide professional-grade betting insights.

## 🌟 Features

### 🚀 **Enhanced AI Prediction Engine**
- **6 ML Algorithms**: XGBoost, Random Forest, Gradient Boosting, Neural Networks, SVM, Logistic Regression
- **Ensemble Learning**: Weighted voting system with cross-validation optimization
- **Confidence Scoring**: Individual and ensemble confidence thresholds
- **Feature Importance Analysis**: Comprehensive feature ranking across all models

### 🌐 **Advanced Data Integration**
- **Real-time Weather Data**: Impact analysis on outdoor sports
- **Social Media Sentiment**: Reddit and Twitter sentiment analysis
- **Injury Reports**: Multi-source injury data (ESPN, Rotowire, Sportsline)
- **Market Data**: Multi-bookmaker odds aggregation
- **Concurrent Data Fetching**: Async data collection from all sources

### 📊 **Intelligent Risk Assessment**
- **Multi-factor Risk Scoring**: Weather, injury, market, sentiment analysis
- **Kelly Criterion Optimization**: Advanced bet sizing with confidence intervals
- **Expected Value Calculation**: Market efficiency analysis
- **Real-time Insights**: Key factors affecting predictions

### 🎯 **Professional Dashboard**
- **Real-time Analytics**: Live sports data and predictions
- **Enhanced ML Interface**: Model training and performance monitoring
- **Risk Management**: Comprehensive risk assessment tools
- **Performance Tracking**: ROI analysis and historical performance

## 🏗️ Architecture

```
├── Backend (Flask + Python)
│   ├── Enhanced ML Models
│   ├── Data Integration Services
│   ├── API Endpoints
│   └── Database Models
├── Frontend (React + Material-UI)
│   ├── Real-time Dashboard
│   ├── Enhanced ML Interface
│   ├── Analytics & Charts
│   └── Responsive Design
└── Infrastructure
    ├── Docker Containers
    ├── Nginx Reverse Proxy
    ├── SSL/HTTPS
    └── Cloud Deployment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)
- API keys for sports data services

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/apexanalytics-ai.git
cd apexanalytics-ai
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp production.env .env
# Edit .env with your API keys

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Start backend
python run.py
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- Enhanced ML: http://localhost:3000/enhanced-ml

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build -d

# Or use the deployment script
./deploy.sh
```

## 🌐 Production Deployment

### Railway (Recommended)
```bash
# Deploy to Railway with custom domain
./deploy-apexanalytics.sh
```

### Other Platforms
- **Render**: Use `render.yaml` configuration
- **Heroku**: Use `heroku.yml` and `Procfile`
- **Vercel**: Frontend deployment with `vercel.json`

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
ODDS_API_KEY=your_odds_api_key
ESPN_API_KEY=your_espn_api_key
SPORTSRADAR_API_KEY=your_sportsradar_key

# Enhanced ML API Keys
WEATHER_API_KEY=your_openweather_api_key
TWITTER_API_KEY=your_twitter_api_key
FANDUEL_API_KEY=your_fanduel_api_key
DRAFTKINGS_API_KEY=your_draftkings_api_key
BET365_API_KEY=your_bet365_api_key

# Application Settings
FLASK_ENV=production
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///sports_betting.db
```

### Custom Domain Setup
1. Configure DNS records pointing to your deployment
2. Add custom domain in your platform dashboard
3. SSL certificates will be automatically provisioned

## 📊 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/games` - Get available games
- `GET /api/predictions` - Get predictions
- `POST /api/bets` - Place bets

### Enhanced ML Endpoints
- `GET /api/enhanced/model-performance` - Model performance metrics
- `GET /api/enhanced/feature-importance` - Feature importance analysis
- `GET /api/enhanced/predictions` - Enhanced predictions
- `POST /api/enhanced/train-model` - Train enhanced model
- `GET /api/enhanced/data-integration/weather` - Weather data
- `GET /api/enhanced/data-integration/social` - Social media sentiment
- `GET /api/enhanced/data-integration/injuries` - Injury reports

## 🤖 ML Models

### Ensemble Architecture
1. **XGBoost**: Gradient boosting for structured data
2. **Random Forest**: Ensemble of decision trees
3. **Neural Networks**: Deep learning for complex patterns
4. **Support Vector Machines**: Classification and regression
5. **Gradient Boosting**: Sequential model training
6. **Logistic Regression**: Linear classification baseline

### Feature Engineering
- Rolling averages and momentum indicators
- Weather impact analysis
- Social media sentiment scores
- Injury impact assessment
- Market efficiency metrics
- Historical performance patterns

## 📈 Performance Metrics

- **Prediction Accuracy**: 65-75% (varies by sport)
- **Risk Assessment**: Multi-factor scoring system
- **Expected Value**: Kelly Criterion optimization
- **Model Performance**: Cross-validation metrics
- **Real-time Processing**: < 2 seconds per prediction

## 🔒 Security Features

- **HTTPS/SSL**: End-to-end encryption
- **Rate Limiting**: API protection
- **CORS**: Cross-origin resource sharing
- **Input Validation**: Data sanitization
- **Environment Variables**: Secure configuration
- **Health Checks**: Application monitoring

## 📱 User Interface

### Dashboard Features
- Real-time sports data visualization
- Interactive charts and graphs
- Responsive design for all devices
- Dark/light theme support
- Real-time updates and notifications

### Enhanced ML Interface
- Model training controls
- Performance monitoring
- Feature importance visualization
- Risk assessment tools
- Prediction confidence displays

## 🛠️ Development

### Project Structure
```
├── app/
│   ├── api/              # API routes
│   ├── ml/               # Machine learning models
│   ├── models/           # Database models
│   └── services/         # Business logic
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   └── public/           # Static assets
├── models/               # Saved ML models
├── data/                 # Data storage
└── docs/                 # Documentation
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **DNS Setup**: [DNS_SETUP.md](DNS_SETUP.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🌟 Live Demo

Visit: **https://apexanalytics-ai.space**

---

**Built with ❤️ using cutting-edge AI and modern web technologies**
