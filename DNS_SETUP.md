# 🌐 DNS Configuration for apexanalytics-ai.space

This guide will help you configure your DNS settings to point your domain to your deployed application.

## 📋 Prerequisites

- Domain: `apexanalytics-ai.space`
- Railway deployment URL (will be provided after deployment)

## 🎯 DNS Records Configuration

### Step 1: Get Your Railway URL

After running the deployment script, you'll get a Railway URL like:
```
https://your-app-name-production.up.railway.app
```

### Step 2: Configure DNS Records

Add these records in your domain registrar's DNS settings:

#### Option A: CNAME Record (Recommended)
```
Type: CNAME
Name: @
Value: your-app-name-production.up.railway.app
TTL: 300 (or default)
```

#### Option B: A Record (Alternative)
```
Type: A
Name: @
Value: [Railway IP Address]
TTL: 300 (or default)
```

#### WWW Subdomain
```
Type: CNAME
Name: www
Value: your-app-name-production.up.railway.app
TTL: 300 (or default)
```

## 🔧 Domain Registrar Instructions

### Popular Registrars:

#### 1. Namecheap
1. Log into your Namecheap account
2. Go to "Domain List" → Click "Manage"
3. Go to "Advanced DNS"
4. Add the CNAME records above
5. Save changes

#### 2. Cloudflare
1. Log into Cloudflare dashboard
2. Select your domain
3. Go to "DNS" → "Records"
4. Add the CNAME records above
5. Ensure "Proxy status" is set to "DNS only" (gray cloud)

#### 3. GoDaddy
1. Log into GoDaddy account
2. Go to "My Products" → "DNS"
3. Add the CNAME records above
4. Save changes

#### 4. Google Domains
1. Log into Google Domains
2. Select your domain
3. Go to "DNS" → "Custom records"
4. Add the CNAME records above
5. Save changes

## ⏱️ DNS Propagation

- **Time**: 5-30 minutes (usually)
- **Maximum**: Up to 48 hours
- **Check**: Use `nslookup apexanalytics-ai.space` or online DNS checkers

## 🔍 Verification Commands

### Check DNS Propagation
```bash
# Check A record
nslookup apexanalytics-ai.space

# Check CNAME record
nslookup www.apexanalytics-ai.space

# Check from different locations
dig apexanalytics-ai.space
```

### Test Website Access
```bash
# Test HTTP redirect
curl -I http://apexanalytics-ai.space

# Test HTTPS
curl -I https://apexanalytics-ai.space

# Test www subdomain
curl -I https://www.apexanalytics-ai.space
```

## 🚨 Troubleshooting

### Common Issues:

1. **DNS Not Propagated**
   - Wait 30 minutes
   - Check with different DNS servers
   - Clear browser cache

2. **CNAME at Root Not Working**
   - Some registrars don't support CNAME at root
   - Use A record instead
   - Contact Railway support for IP address

3. **SSL Certificate Issues**
   - Wait for automatic SSL provisioning
   - Check Railway dashboard for SSL status
   - Contact Railway support if needed

4. **WWW Subdomain Not Working**
   - Ensure CNAME record for www is set
   - Check TTL settings
   - Wait for propagation

## 📞 Support

- **Railway Support**: [Railway Discord](https://discord.gg/railway)
- **Domain Registrar**: Check your registrar's support
- **DNS Issues**: Use online DNS checkers

## ✅ Success Checklist

- [ ] CNAME record added for root domain
- [ ] CNAME record added for www subdomain
- [ ] DNS propagation completed
- [ ] Website accessible via HTTP
- [ ] Website accessible via HTTPS
- [ ] SSL certificate active
- [ ] All subdomains working

---

**Your ApexAnalytics AI will be live at https://apexanalytics-ai.space once DNS is configured! 🎉**
