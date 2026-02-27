# Crypto-Sentiment-Pulse

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)

**Crypto-Sentiment-Pulse** is an open-source project serving as a real-time ETL pipeline and analytics dashboard. It aggregates cryptocurrency market data, curates relevant news, and performs sentiment analysis on Telegram streams to provide a unified overview of the crypto ecosystem.

---

## Overview

- **Problem:** Traders and analysts often struggle with context switching between price charts, news aggregators, and social sentiment streams.
- **Solution:** A consolidated, real-time dashboard powered by an event-driven, distributed data ingestion pipeline.
- **Type:** Open-source full-stack microservices ecosystem (Backend APIs, Background Data Ingestors, Live SPA).

---

## Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **Frontend:** Vue 3
- **Background Processing / Queue:** Celery
- **Message Broker (Pub/Sub):** Redis
- **Database:** PostgreSQL
- **Infrastructure:** Docker & Docker Compose

---

## Quick Start

The project is fully containerized and relies on Docker Compose for deterministic environments and seamless orchestration.

```bash
# Clone the repository
git clone https://github.com/Modern-Messiah/Crypto-Sentiment-Pulse.git
cd Crypto-Sentiment-Pulse

# Setup environment variables
cp .env.example .env
# Edit .env with your specific API keys

# Spin up the infrastructure
docker-compose up --build -d

# Important: Telegram Authentication
# Since Telegram requires an interactive login (phone number + code), 
# you must run the auth script inside the backend container:
docker exec -it backend python app/scripts/auth_telegram.py

docker-compose restart news-service
```

**Access Points:**
- **Frontend Dashboard:** `http://localhost:3000`
- **Backend API & Swagger:** `http://localhost:8080/docs`

---

## Configuration

Application state and secrets are managed via environment variables. Refer to `.env.example` for the baseline configuration.

**Required External Secrets:**
- `TELEGRAM_API_ID` & `TELEGRAM_API_HASH`: Required for the Telegram MTProto client. Fetch from [my.telegram.org](https://my.telegram.org/apps).
- `CRYPTOPANIC_API_TOKEN`: Optional, required for scraping curated crypto news.

*Note: Without valid Telegram credentials, the Telegram ingestion service will fail gracefully, but core crypto prices will continue to stream.*

---

## Architecture

The system follows a **Distributed Microservices** pattern, heavily utilizing asynchronous execution (`FastAPI`, `asyncio`) and background workloads (`Celery`) for non-blocking I/O and high-throughput ingestion.

### Services Topology

| Service | Responsibility | Port |
|---------|----------------|------|
| **Backend API** | Exposes WebSocket/REST endpoints, broadcasts live Redis events | `:8080` |
| **Frontend** | Vue 3 SPA dashboard for live data visualization | `:3000` |
| **Crypto Service**| Connects to Binance WS, publishes crypto price ticks to Redis | N/A |
| **News Service** | Scrapes Telegram (MTProto) & CryptoPanic, publishes to Redis | N/A |
| **Celery Tasks**| Background workers consuming Redis queues to persist data | N/A |
| **PostgreSQL** | Primary persistent data store (Messages, Prices, Channels) | `:5432` |
| **Redis** | In-memory message broker & real-time event bus | `:6379` |

### Architectural Documentation (C4 Model)

Comprehensive architectural diagrams and documentation are available in the [docs/architecture/c4](./docs/architecture/c4) directory, organized by levels:

- **[Level 1: System Context](./docs/architecture/c4/L1%20-%20System%20Context/docs.md)**: High-level overview of actors and external system dependencies.
- **[Level 2: Container Level](./docs/architecture/c4/L2%20-%20Container/docs.md)**: Details of service-to-service communication, ports, and data flows.
- **[Level 3: Component Level](./docs/architecture/c4/L3%20-%20Component/docs.md)**: Deep dive into the internal class structure and method call chains of each microservice.
- **[Level 4: Code Level](./docs/architecture/c4/L4%20-%20Code%20Level/docs.md)**: Explains the non-obvious internals of critical pipelines (WebSocket threads, Sentiment analysis).

> [!TIP]
> To view and edit `.puml` files directly in VS Code, we recommend installing the [PlantUML extension](https://open-vsx.org/vscode/item?itemName=jebbs.plantuml).

---

## Documentation

- **API Documentation:** Auto-generated Swagger (OpenAPI) documentation is exposed at `http://localhost:8080/docs`.
- **System Architecture:** Detailed C4 models and behavioral sequence diagrams are available in the [Architecture Guide](./docs/architecture/c4/).

---

## Testing

Test suites are configured to ensure data integrity and pipeline resilience across the microservices.

### Backend / Microservices 
Run tests utilizing `pytest` within individual service scopes (e.g., `backend`, `crypto_service`, `news_service`).

```bash
# Navigate to the service directory (e.g. backend)
cd backend

# Run the full test suite
pytest

# Run tests with code coverage
pytest --cov=app tests/
```

### Frontend
Component tests are executed using standard NPM scripts:
```bash
cd frontend
npm run test
```

---

## Deployment

The application is infrastructure-agnostic, primarily optimized for straightforward single-node deployments using **Docker Compose** on any standard Linux VPS (e.g., AWS EC2, DigitalOcean, Hetzner).

*Future iterations may migrate towards Kubernetes (K8s) manifests as data ingestion scales require horizontal pod autoscaling.*

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Demo & Visualization

### Real-time Price Engine
![Market Dashboard Preview](.github/assets/lv_0_20260226185659-ezgif.com-video-to-gif-converter.gif)
*Showcase of the real-time websocket-driven price updates with interactive charts.*

### Desktop vs Mobile Adaptation
| Desktop Workflow | Mobile Version |
|------------------|----------------|
| <video src="https://github.com/user-attachments/assets/1fd9e970-95ec-4ae2-82f0-fc61b8dc8733"></video> | <video src="https://github.com/user-attachments/assets/f57065d0-6fbe-406e-b44d-fd4593a127ee"></video> |
| *Full-scale desktop dashboard view.* | *Optimized mobile experience.* |

