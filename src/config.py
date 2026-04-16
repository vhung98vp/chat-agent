import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv(".env")

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
    'model': os.getenv("LLM_MODEL", "Qwen/Qwen3.5-9B")
}

ES = {
    'url': os.getenv("ES_URL", "http://localhost:9200"),
    'user': os.getenv("ES_USER", "elastic"),
    'password': os.getenv("ES_PASSWORD", "password"),
}

NEO4J = {
    'url': os.getenv("NEO4J_URL", "bolt://localhost:7687"),
    'user': os.getenv("NEO4J_USER", "neo4j"),
    'password': os.getenv("NEO4J_PASSWORD", "password"),
}
