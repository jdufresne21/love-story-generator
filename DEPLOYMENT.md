# Railway Deployment Guide

This guide will help you deploy your Love Story Generator to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code needs to be in a GitHub repository
3. **OpenAI API Key**: You'll need this for the story generation

## Step 1: Prepare Your Code

Make sure your code is in a GitHub repository. If it's not already:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## Step 2: Deploy to Railway

1. **Go to Railway Dashboard**: Visit [railway.app/dashboard](https://railway.app/dashboard)

2. **Create New Project**: Click "New Project"

3. **Deploy from GitHub**: Choose "Deploy from GitHub repo"

4. **Select Repository**: Choose your love story generator repository

5. **Wait for Build**: Railway will automatically detect it's a Python app and start building

## Step 3: Configure Environment Variables

Once deployed, go to your project settings:

1. **Variables Tab**: Click on the "Variables" tab
2. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FLASK_ENV`: Set to `production`

## Step 4: Get Your Domain

1. **Settings Tab**: Go to the "Settings" tab
2. **Custom Domains**: You can add a custom domain here
3. **Default Domain**: Railway provides a default domain like `your-app-name.railway.app`

## Step 5: Test Your Deployment

Visit your Railway URL and test:

- Home page: `https://your-app-name.railway.app/`
- Health check: `https://your-app-name.railway.app/health`
- Love form: `https://your-app-name.railway.app/love-form`

## Custom Domain Setup

To use your own domain:

1. **Add Custom Domain**: In Railway settings, add your domain
2. **Update DNS**: Point your domain's DNS to Railway's servers
3. **SSL Certificate**: Railway automatically provides SSL certificates

### DNS Configuration

Add these DNS records to your domain provider:

```
Type: CNAME
Name: @ (or your subdomain)
Value: cname.railway.app
```

## Monitoring and Logs

- **Logs**: View real-time logs in the Railway dashboard
- **Metrics**: Monitor your app's performance
- **Deployments**: Track deployment history

## Troubleshooting

### Common Issues:

1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **App Won't Start**: Verify the `Procfile` is correct
3. **Environment Variables**: Make sure `OPENAI_API_KEY` is set
4. **Port Issues**: The app should use `os.environ.get('PORT', 3000)`

### Debug Commands:

```bash
# View logs
railway logs

# Check status
railway status

# Redeploy
railway up
```

## Cost Management

With Railway's Hobby plan:

- **Free Tier**: $5/month credit
- **Usage**: Pay for what you use
- **Scaling**: Automatically scales based on traffic

## Next Steps

1. **Set up monitoring**: Configure alerts for downtime
2. **Add analytics**: Track usage and performance
3. **Optimize**: Monitor resource usage and optimize as needed
4. **Backup**: Consider setting up database backups if you add a database later
