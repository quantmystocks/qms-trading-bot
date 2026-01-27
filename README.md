# QMS Trading Bot

Automated portfolio rebalancing bot that tracks a leaderboard and automatically rebalances your portfolio to match the top 5 stocks every Monday.

## Features

- **Automated Rebalancing**: Automatically rebalances portfolio to match leaderboard top 5 stocks
- **Multiple Broker Support**: Works with Alpaca and Robinhood
- **Flexible Scheduling**: Internal scheduler or external webhook triggers
- **Email Notifications**: Get notified when trades complete (SMTP, SendGrid, or AWS SES)
- **Docker Ready**: Containerized for easy deployment
- **Cloud Deployable**: Works with AWS, GCP, and Azure

## Quick Start

### Prerequisites

- Python 3.11+ or Docker
- Broker account (Alpaca or Robinhood)
- Leaderboard API access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qms-trading-bot
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure your settings**
   Edit `.env` with your API keys and credentials (see Configuration section)

4. **Run with Docker (Recommended)**
   ```bash
   docker-compose up
   ```

5. **Or run locally**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m src.main
   ```

## Configuration

All configuration is done via environment variables. See `.env.example` for all available options.

### Required Configuration

- `LEADERBOARD_API_URL`: Your leaderboard API endpoint
- `LEADERBOARD_API_TOKEN`: Authentication token for leaderboard API
- `BROKER_TYPE`: `alpaca` or `robinhood`

### Broker Configuration

**Alpaca:**
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_API_SECRET`: Your Alpaca API secret
- `ALPACA_BASE_URL`: `https://paper-api.alpaca.markets` (paper) or `https://api.alpaca.markets` (live)

**Robinhood:**
- `ROBINHOOD_USERNAME`: Your Robinhood username/email
- `ROBINHOOD_PASSWORD`: Your Robinhood password
- `ROBINHOOD_MFA_CODE`: Optional MFA code if 2FA is enabled

### Email Configuration

Set `EMAIL_ENABLED=true` and choose a provider:

**SMTP (Gmail, Outlook, etc.):**
- `EMAIL_PROVIDER=smtp`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`
- 📖 **Gmail Setup:** See [Gmail App Password Setup Guide](docs/GMAIL_APP_PASSWORD_SETUP.md) for detailed instructions

**SendGrid:**
- `EMAIL_PROVIDER=sendgrid`
- `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`

**AWS SES:**
- `EMAIL_PROVIDER=ses`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `SES_FROM_EMAIL`

### Scheduler Configuration

**Internal Scheduler (Default):**
- `SCHEDULER_MODE=internal`
- `CRON_SCHEDULE=0 0 * * 1` (Mondays at midnight)

**External Scheduler (for cloud deployments):**
- `SCHEDULER_MODE=external`
- `WEBHOOK_PORT=8080`
- `WEBHOOK_SECRET=optional_secret_token`

## How It Works

1. **Scheduler triggers** every Monday (or as configured)
2. **Fetches leaderboard** top 5 stocks from your API
3. **Checks current portfolio** allocation
4. **Rebalances if needed**:
   - If portfolio is empty: Divides initial capital into 5 equal parts and buys top 5
   - If allocations don't match: Sells positions not in top 5, buys missing positions
   - If allocations match: Does nothing
5. **Sends email notification** with trade summary (if enabled)

## Deployment

📖 **Not sure which hosting option to choose?** See [Hosting Comparison Guide](docs/HOSTING_COMPARISON.md)

### Local/Docker

See Quick Start section above.

### GitHub Actions (Free for Scheduled Runs)

Run your bot on a schedule using GitHub Actions - perfect for weekly rebalancing!

**Pros:**
- ✅ Free for public repos (500 min/month) or private repos (2,000 min/month)
- ✅ No infrastructure to manage
- ✅ Built-in scheduling
- ✅ Secure secret management

**Cons:**
- ⚠️ Jobs can be delayed during high load
- ⚠️ Not suitable for time-critical trading
- ⚠️ Limited to scheduled runs (not always-on)

📖 **Quick Start:** See [GitHub Actions Quick Start Guide](docs/GITHUB_ACTIONS_QUICKSTART.md) (5-minute setup!)

📖 **Full Guide:** See [GitHub Actions Deployment Guide](docs/GITHUB_ACTIONS_DEPLOYMENT.md)

**Quick Steps:**
1. Add secrets to GitHub repository (Settings → Secrets and variables → Actions)
2. The workflow file is already created at `.github/workflows/trading-bot.yml`
3. Test it manually (Actions → Run workflow)
4. It will run automatically on schedule!

### AWS (ECS/Fargate with EventBridge)

1. Build and push Docker image to ECR
2. Deploy to ECS/Fargate
3. Set `SCHEDULER_MODE=external`
4. Create EventBridge rule: `cron(0 0 ? * MON *)`
5. Configure EventBridge to POST to your container endpoint

### GCP (Cloud Run with Cloud Scheduler)

1. Build and push Docker image to GCR
2. Deploy to Cloud Run
3. Set `SCHEDULER_MODE=external`
4. Create Cloud Scheduler job: `0 0 * * 1`
5. Configure job to POST to Cloud Run service URL

### Azure (Container Instances with Logic Apps)

1. Build and push Docker image to ACR
2. Deploy to Container Instances
3. Set `SCHEDULER_MODE=external`
4. Create Logic App with weekly recurrence trigger
5. Configure Logic App to POST to container endpoint

## API Endpoints (External Scheduler Mode)

### Health Check
```
GET /health
```
Returns: `{"status": "healthy"}`

### Trigger Rebalancing
```
POST /rebalance
Headers: Authorization: Bearer <WEBHOOK_SECRET> (if configured)
```
Returns: Trade summary JSON

## Testing

Run unit tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Broker Connection Issues
- Verify API keys/credentials are correct
- Check broker account status
- Ensure paper trading is enabled for testing

### Email Not Sending
- Verify email provider credentials
- Check email provider service status
- Review logs for specific error messages

### Scheduler Not Running
- Check cron expression format
- Verify scheduler mode (internal vs external)
- Review application logs

## Security

- Never commit `.env` file to version control
- Use environment variables in production
- Rotate API keys regularly
- Use webhook secrets for external scheduler mode
- Review SECURITY.md for best practices

## License

MIT License - see LICENSE file

## Contributing

See CONTRIBUTING.md for guidelines.

## Support

For issues and questions, please open an issue on GitHub.
