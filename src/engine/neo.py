from neo4j import GraphDatabase
from neo4j import GraphDatabase
from config import NEO4J

driver = GraphDatabase.driver(NEO4J['url'], auth=(NEO4J['user'], NEO4J['password']))


def get_related_nodes(tx, node_id, node_label, n_hops):
    # Sử dụng biến p để đại diện cho đường đi, từ đó lấy được length(p) là distance
    query = f"""
    MATCH p = (start:{node_label} {{id: $id}})-[*1..{n_hops}]-(related)
    WHERE start <> related
    RETURN DISTINCT 
        related.id AS id, 
        labels(related) AS labels, 
        length(p) AS distance
    ORDER BY distance ASC
    LIMIT 200
    """
    result = tx.run(query, id=node_id)
    return [record.data() for record in result]


def query_neo4j(source_ids, label, n_hops=3):
    label = label.capitalize()
    try:
        with driver.session() as session:
            related_list = []
            for sid in source_ids:
                related = session.execute_read(get_related_nodes, sid, label, n_hops)
                print(f"--- Tìm thấy {len(related)} nodes liên quan đến {label} ID: {sid} (max {n_hops} hops) ---")
                related_list.append((sid, related))
            return related_list    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []
    finally:
        driver.close()
