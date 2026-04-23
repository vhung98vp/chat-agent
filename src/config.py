import os
import sys
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
                    handlers=[logging.StreamHandler(sys.stdout)]
                )

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


LLM = {
    'url': os.getenv("LLM_URL", "http://localhost:8000/v1/chat/completions"),
    'model': os.getenv("LLM_MODEL", "Qwen/Qwen3.5-9B"),
    'max_tokens': int(os.getenv("LLM_RESPONSE_MAX_TOKENS", 1024)),
    'stream': os.getenv("LLM_RESPONSE_STREAM", "false").lower() == "true",
    'context_window_limit': int(os.getenv("LLM_CONTEXT_WINDOW_LIMIT", 5)),
}

ES = {
    'url': os.getenv("ES_URL", "http://localhost:9200"),
    'user': os.getenv("ES_USER", "elastic"),
    'password': os.getenv("ES_PASSWORD", "password"),
    'batch_size': int(os.getenv("ES_BATCH_SIZE", 10)),
}

NEO4J = {
    'url': os.getenv("NEO4J_URL", "bolt://localhost:7687"),
    'user': os.getenv("NEO4J_USER", "neo4j"),
    'password': os.getenv("NEO4J_PASSWORD", "password"),
    'hops': int(os.getenv("NEO4J_HOPS", 3)),
}
