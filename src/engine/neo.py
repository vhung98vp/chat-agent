from neo4j import GraphDatabase
from neo4j import GraphDatabase
from config import NEO4J, get_logger
logger = get_logger(__name__)

driver = GraphDatabase.driver(
    NEO4J['url'], 
    auth=(NEO4J['user'], NEO4J['password'])
)


def get_related_nodes(tx, src_id, src_label, dst_label, max_hops):
    # Sử dụng biến p để đại diện cho đường đi, từ đó lấy được length(p) là distance
    query = f"""
    MATCH p = (start:{src_label} {{id: $id}})-[*1..{max_hops}]-(related:{dst_label})
    WHERE start <> related
    RETURN DISTINCT 
        related.id AS id, 
        labels(related) AS labels, 
        length(p) AS distance
    ORDER BY distance ASC
    LIMIT {NEO4J['max_items']}
    """
    result = tx.run(query, id=src_id)
    return [record.data() for record in result]


def query_neo4j(src_ids, src_label, dst_label, max_hops=NEO4J['max_hops']):
    src_label = src_label.capitalize()
    dst_label = dst_label.capitalize()
    try:
        with driver.session() as session:
            related_list = []
            for sid in src_ids:
                related = session.execute_read(get_related_nodes, sid, src_label, dst_label, max_hops)
                logger.info(f"--- Found {len(related)} related nodes for {src_label} ID: {sid} (max {max_hops} hops) ---")
                related_list.append((sid, related))
            return related_list    
    except Exception as e:
        logger.error(f"❌ Error querying neo4j: {e}")
        return []
