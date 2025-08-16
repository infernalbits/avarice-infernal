# 🚀 Sports Betting AI - Deployment Guide

This guide will help you deploy your Sports Betting AI application to various cloud platforms with a custom domain.

## 📋 Prerequisites

- Git repository with your code
- Domain name (optional but recommended)
- API keys for sports data services

## 🎯 Quick Deploy Options

### Option 1: Railway (Recommended - Free Tier Available)

1. **Sign up** at [Railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Deploy automatically**:
   ```bash
   # Railway will detect the railway.json and deploy automatically
   git push origin main
   ```

4. **Get your domain**: Railway provides a free `.railway.app` domain
5. **Custom domain**: Add your domain in Railway dashboard

### Option 2: Render (Free Tier Available)

1. **Sign up** at [Render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
   - Environment: Python 3.11

5. **Deploy**: Render will automatically deploy from your `render.yaml`

### Option 3: Heroku (Paid)

1. **Install Heroku CLI**:
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

3. **Add custom domain**:
   ```bash
   heroku domains:add yourdomain.com
   ```

### Option 4: Vercel (Frontend) + Railway (Backend)

1. **Deploy backend to Railway** (see Option 1)
2. **Deploy frontend to Vercel**:
   - Sign up at [Vercel.com](https://vercel.com)
   - Connect your repository
   - Vercel will auto-detect React app
   - Update `vercel.json` with your backend URL

## 🌐 Custom Domain Setup

### 1. Domain Registration
- **Recommended**: [Namecheap](https://namecheap.com) or [Cloudflare](https://cloudflare.com)
- **Cost**: ~$10-15/year

### 2. DNS Configuration

#### For Railway:
```
Type: CNAME
Name: @
Value: your-app.railway.app
```

#### For Render:
```
Type: CNAME
Name: @
Value: your-app.onrender.com
```

#### For Heroku:
```
Type: CNAME
Name: @
Value: your-app.herokuapp.com
```

### 3. SSL Certificate
- **Railway/Render/Heroku**: Automatic SSL
- **Vercel**: Automatic SSL
- **Custom**: Use Let's Encrypt

## 🔧 Environment Variables

Set these in your cloud platform dashboard:

```bash
# API Keys
ODDS_API_KEY=your_odds_api_key
ESPN_API_KEY=your_espn_api_key
SPORTSRADAR_API_KEY=your_sportsradar_api_key

# Enhanced ML API Keys
WEATHER_API_KEY=your_openweather_api_key
TWITTER_API_KEY=your_twitter_api_key
FANDUEL_API_KEY=your_fanduel_api_key
DRAFTKINGS_API_KEY=your_draftkings_api_key
BET365_API_KEY=your_bet365_api_key

# Database
DATABASE_URL=sqlite:///sports_betting.db

# Security
SECRET_KEY=your_secret_key_here
FLASK_ENV=production

# Betting Configuration
INITIAL_BANKROLL=1000
MAX_BET_PERCENTAGE=0.05
MIN_CONFIDENCE_THRESHOLD=0.65
```

## 🐳 Docker Deployment

### Local Docker Testing:
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Production Docker:
```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 Monitoring & Analytics

### 1. Application Monitoring
- **Railway**: Built-in monitoring
- **Render**: Built-in monitoring
- **Heroku**: Add-on monitoring
- **Custom**: Use [Sentry](https://sentry.io) for error tracking

### 2. Performance Monitoring
- **Frontend**: [Vercel Analytics](https://vercel.com/analytics)
- **Backend**: [New Relic](https://newrelic.com) or [DataDog](https://datadoghq.com)

### 3. Uptime Monitoring
- **UptimeRobot**: Free uptime monitoring
- **Pingdom**: Professional monitoring
- **StatusCake**: Comprehensive monitoring

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit API keys to Git
- Use platform-specific secret management
- Rotate keys regularly

### 2. HTTPS
- Always use HTTPS in production
- Enable HSTS headers
- Use secure cookies

### 3. Rate Limiting
- Implement API rate limiting
- Use CDN for DDoS protection
- Monitor for suspicious activity

### 4. Database Security
- Use connection pooling
- Implement proper authentication
- Regular backups

## 🚀 Performance Optimization

### 1. Frontend
- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading
- Optimize bundle size

### 2. Backend
- Use caching (Redis)
- Implement database indexing
- Optimize database queries
- Use connection pooling

### 3. CDN
- **Cloudflare**: Free CDN with DDoS protection
- **AWS CloudFront**: Professional CDN
- **Vercel Edge**: Global edge network

## 📈 Scaling Considerations

### 1. Database
- **SQLite**: Good for development, not production
- **PostgreSQL**: Recommended for production
- **MongoDB**: Alternative for document storage

### 2. Caching
- **Redis**: Session and data caching
- **Memcached**: Simple caching
- **CDN**: Static asset caching

### 3. Load Balancing
- **Railway/Render**: Automatic scaling
- **Heroku**: Dyno scaling
- **Custom**: Use nginx or HAProxy

## 🆘 Troubleshooting

### Common Issues:

1. **Port conflicts**:
   ```bash
   # Check what's using the port
   lsof -i :5001
   # Kill the process
   kill -9 <PID>
   ```

2. **Database issues**:
   ```bash
   # Reset database
   rm sports_betting.db
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

3. **Build failures**:
   ```bash
   # Clear cache and rebuild
   docker system prune -a
   docker-compose up --build
   ```

4. **SSL issues**:
   ```bash
   # Regenerate certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem
   ```

## 📞 Support

- **Documentation**: Check platform-specific docs
- **Community**: Stack Overflow, Reddit
- **Professional**: Consider managed services

## 🎉 Success Checklist

- [ ] Application deployed successfully
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Performance optimized
- [ ] Security measures implemented

---

**Your Sports Betting AI is now ready for the world! 🌍**
