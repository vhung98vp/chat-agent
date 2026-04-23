from engine.es import query_es, query_es_ids
from engine.neo import query_neo4j
from engine.llm import get_pipeline_info, eval_entity, eval_entity_relation
from config import get_logger, LLM
logger = get_logger(__name__)


def pipeline_single(pipe_info, user_query, conversation):
    e1 = pipe_info["e1"]
    e1_cands = query_es(e1)
    return eval_entity(e1_cands, user_query, conversation)


def pipeline_multi(pipe_info, user_query, conversation):
    e1 = pipe_info["e1"]
    e2 = pipe_info["e2"]

    e1_cands = query_es(e1) if len(e1["info"]) > 0 else []
    e2_cands = query_es(e2) if len(e2["info"]) > 0 else []

    if not e1_cands and not e2_cands:
        return {"candidates": [], "relation": False}

    result = []
    if e1_cands and e2_cands:
        e1_lookup = {item['id']: item for item in e1_cands}
        e2_lookup = {item['id']: item for item in e2_cands}

        e1_ids = list(e1_lookup.keys())
        e2_ids = list(e2_lookup.keys())

        e1_related = query_neo4j(e1_ids, e1['type'], "document")
        e2_related = query_neo4j(e2_ids, e2['type'], "document")

        e1_rel_map = {
            s_id: {node['id']: node for node in related}
            for s_id, related in e1_related
        }

        e2_rel_map = {
            s_id: {node['id']: node for node in related}
            for s_id, related in e2_related
        }

        for e1_id, rel1 in e1_rel_map.items():
            for e2_id, rel2 in e2_rel_map.items():
                common_ids = set(rel1.keys()) & set(rel2.keys())

                for mid_id in common_ids:
                    result.append({
                        "e1": e1_lookup[e1_id],
                        "e2": e2_lookup[e2_id],
                        "via": rel1[mid_id].get("id", "-"),  # or rel2[mid_id]
                        "distance": rel1[mid_id].get("distance", 999) + rel2[mid_id].get("distance", 999),
                        "target": pipe_info["target"]
                    })

        result.sort(key=lambda x: (x["distance"], x["e1"]))
    else:
        if e1_cands:
            src_list, src_type, t_type = e1_cands, e1['type'], e2['type']
        else:
            src_list, src_type, t_type = e2_cands, e2['type'], e1['type']
        
        src_lookup = {item['id']: item for item in src_list}
        related_list = query_neo4j(src_lookup, src_type, t_type)
        related_list.sort(key=lambda x: len(x[1]))

        related_ids = []
        for _, related_items in related_list:
            related_ids.extend([item['id'] for item in related_items])

        related_data = query_es_ids(related_ids)
        related_map = { rd["id"]:rd for rd in related_data }

        for s_id, related_items in related_list:
            for rel in related_items:
                result.append({
                    "e1": src_lookup[s_id],
                    "e2": related_map.get(rel["id"]),
                    "via": "-",
                    "distance": rel.get("distance", 999),
                    "target": "e2"
                })

        result.sort(key=lambda x: (x["distance"], x["e1"]))
    return eval_entity_relation(result, user_query, conversation)


def process_request(user_query: str, context: dict = None, conversation: list = None):
    if conversation:
        conversation = conversation[-LLM['context_window_limit']:]
    pipe_info = get_pipeline_info(user_query, context, conversation)

    try:
        if pipe_info["pipeline"] == "P1":
            return pipeline_single(pipe_info, user_query, conversation)
        elif pipe_info["pipeline"] == "P2":
            return pipeline_multi(pipe_info, user_query, conversation)
        else:
            raise ValueError("Invalid pipeline type")
    except Exception as e:
        logger.error(f"Error while processing pipeline: {e}")
        return pipe_info
