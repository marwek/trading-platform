# (very simple)Forex Trading Platform API

A RESTful API simulating a trading platform with WebSocket support for real-time order updates.

## Prerequisites

- Python 3.11+
- Docker (optional)

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt  # for running tests
```

3. Create `.env` file:
```ini
# Server settings
host=127.0.0.1
port=8080

# Logging
LOG_LEVEL=INFO

# WebSocket
WS_HEARTBEAT_INTERVAL=30
```

## Running the Server

### Local
```bash
uvicorn src.server.main:app --host 127.0.0.1 --port 8080 --reload
```

### Docker
```bash
docker-compose up -d trading-server
```

## Running Tests

### Local
```bash
pytest
```

### Docker
```bash
docker-compose up --build trading-tests
```

Test report will be generated in `reports/report.html` directory

## Documentation

- API documentation: http://localhost:8080/docs

## Manual API Testing
For manual API testing, you can use the REST Client VS Code extension

1. Install [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
2. Find API call examples in the restclient directory