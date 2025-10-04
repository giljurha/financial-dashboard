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

Automatically deploys to cafe24 server on push to main branch using GitHub Actions.

### Access
- Application: http://giljurha01.cafe24.com

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
