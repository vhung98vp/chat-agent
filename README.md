# Chat Agent
A modular Python project for building and running LLM-powered pipelines, with support for multiple engines and easy configuration.

## Features
- Modular engine support (Elasticsearch, Neo4j, LLMs, etc.)
- Configurable pipelines for data processing and inference
- Dockerized for easy deployment
- Example scripts and test utilities

## Getting Started
### Prerequisites
- Python 3.12+
- Docker (optional, for containerized runs)

### Installation
- Clone the repository:
```
    git clone https://github.com/vhung98vp/chat-agent
    cd chat-agent
```

- Install dependencies:
```
    pip install -r requirements.txt
```

### Running the Application
To run the main app:
```
python src/app.py
```
- To run in Docker:
```
docker build -t chat-agent .
docker run --rm -it chat-agent
```

## License
MIT