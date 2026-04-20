import requests
import json
import time 
from config import get_logger, LLM
from .prompt import build_messages_pipeline_single, build_messages_pipeline_conversation, build_messages_eval_entity, build_messages_eval_entity_relation


logger = get_logger("__name__")

def parse_json_safe(text):
    try:
        text = text.strip().strip('```json').strip('```')
        return json.loads(text)
    except Exception:
        logger.error(f"⚠️ Raw output (invalid JSON): {text}")
        return None


def query_vllm(messages, max_tokens=512, stream=False):
    try:
        payload = {
            "model": LLM['model'],
            "messages": messages,
            "chat_template_kwargs": {
                "enable_thinking": False
            },
            "temperature": 0.1,
            "top_p": 0.6,
            "top_k": 5,
            "min_p": 0.1,
            "presence_penalty": 0.0,
            "repetition_penalty": 1.05,
            "max_tokens": max_tokens,
            "stream": stream
        }

        response = requests.post(LLM['url'], json=payload)
        response.raise_for_status()

        result = response.json()

        content = result["choices"][0]["message"]["content"]

        return content
    except Exception as e:
        logger.exception(f"Error querying LLM: {e}")
        return {}


def get_pipeline_info(user_query: str, context: dict = None, conversation: list = None):
    if context or conversation:
        messages = build_messages_pipeline_conversation(user_query, context, conversation)
    else:
        messages = build_messages_pipeline_single(user_query)

    start = time.time()
    raw_output = query_vllm(messages)
    logger.info(f"Time taken: {time.time() - start:.2f} (s)\n - Query: {user_query}\n - Response: {raw_output}")

    return parse_json_safe(raw_output)


def eval_entity(candidates: list, user_query: str, conversation: list):
    messages = build_messages_eval_entity(user_query, candidates, conversation)
    return query_vllm(messages, 1024)


def eval_entity_relation(candidates: list, user_query: str, conversation: list):
    messages = build_messages_eval_entity_relation(user_query, candidates, conversation)
    return query_vllm(messages, 1024)
