from elasticsearch import Elasticsearch
from config import ES, get_logger
logger = get_logger(__name__)


es = Elasticsearch(
    ES['url'],
    basic_auth=(ES['user'], ES['password']),
    verify_certs=False
)


def execute_elastic_query(index_name, query_json, batch=10):
    try:
        response = es.search(
            index=index_name,
            body=query_json,
            size=batch
        )
        
        hits = response['hits']['hits']
        if not hits:
            logger.info("No result found.")
            return []
            
        results = [hit['_source'] for hit in hits]
        return results

    except Exception as e:
        logger.error(f"❌ Error executing query: {e}")
    return []


def entity_to_query_json(entity):
    text_query = " ".join(str(v) for k, v in entity["info"].items() if k != "name")
    if entity["info"].get("name"):
        return {
            "query": {
                "bool": {
                    "must": [{"match_phrase": {"name.no_accent": entity["info"]["name"]}}], 
                    "should": [{"match": {"text": {"query": text_query, "boost": 2.0}}}]
                }
            }
            
        }
    elif entity["info"].get("relation_type") and entity["info"].get("src_name"):
        text_query = " ".join(str(v) for k, v in entity["info"].items() if k not in ["relation_type", "src_name"])
        return {
            "query": {
                "bool": {
                    "must": [{"match": {"text": entity["info"]["relation_type"]}},
                             {"match": {"text": entity["info"]["src_name"]}}],
                    "should": [{"match": {"text": {"query": text_query, "boost": 2.0}}}]
                }
            }
        }
    else:
        return {
            "query": {
                "match": {
                    "text": {
                        "query": text_query,
                        "minimum_should_match": "75%"
                    }
                }
            }
        }


def query_es(entity, batch=ES['batch_size']):
    if entity["type"] and entity["info"]:
        index_name = f"{entity["type"].lower()}-idx-fs-prod"
        query_json = entity_to_query_json(entity)
        return execute_elastic_query(index_name, query_json, batch)
    else:
        return {}



def ids_to_query_json(ids):
    return {
        "query": {
            "terms": {
                "id": ids
            }
        }
    }


def query_es_ids(entity_ids, entity_type):
    index_name = f"{entity_type.lower()}-idx-fs-prod"
    query_json = ids_to_query_json(entity_ids)
    batch_size = min(ES["max_batch_size"], len(entity_ids))
    return execute_elastic_query(index_name, query_json, batch_size)

