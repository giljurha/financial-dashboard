# Financial Dashboard

Financial data visualization dashboard with Spring Boot backend and React frontend.

## Tech Stack

**Backend:**
- Spring Boot 3.2.0
- Kotlin
- WebFlux

**Frontend:**
- React
- TypeScript
- Chart.js

**Deployment:**
- Docker & Docker Compose
- GitHub Actions CI/CD

## Deployment

Automatically deploys to server on push to main branch using GitHub Actions.

### Access
- Application: https://searchstock.kr

### HTTPS Setup (First Time Only)

To enable HTTPS with Let's Encrypt SSL certificate:

1. SSH into your server
2. Navigate to the project directory
3. Update email in `init-letsencrypt.sh`:
   ```bash
   email="your-email@example.com"  # Change this
   ```
4. Run the initialization script:
   ```bash
   chmod +x init-letsencrypt.sh
   sudo ./init-letsencrypt.sh
   ```

The certificate will auto-renew every 12 hours via the certbot container.

## Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Features

- Real-time financial data visualization
- Interactive charts powered by Chart.js
- RESTful API with Spring Boot
- Responsive React frontend
- Automated deployment with GitHub Actions
