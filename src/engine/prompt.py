import json
from config import LLM


def build_messages_pipeline_single(user_query: str) -> list:
    system_prompt = """
You are an AI Query Router.

Your job is to:
1. Extract entities from user query
2. Determine:
   - source_type (person, organization, event)
   - target_type (if exists)
3. Detect conditions:
   - no_relation: user only asks about entity info
   - has_relation: user asks about connection/related entities (query contains 2 entities)
   - entity_info: id (identity_id, phone, tax_code, ...) OR attributes (keyword) about entity or related entity (name, address, date, job, ...).
   - relation: one_ambiguous / both_ambiguous
4. Keyword extraction:
   - Field name must be standardized (without accents if possible). 
   - All other fields use original keywords (do not standardized).
   - Only extract keywords that are useful for searching in database
   - Example:
        + "làm ca sĩ" → "ca sĩ"
        + "ông Nguyễn Thành" → "Nguyễn Thành"
        + "công tác tại Bộ Công an" → "Bộ Công an"

5. Based on rules below, choose pipeline:
RULES:
- P1: one_entity (no_relation) AND entity_info
- P2: two_entities (has_relation) AND both_ambiguous/one_ambiguous/expand from known entity

IMPORTANT:
- Only choose ONE pipeline from P1 → P2
- Do NOT invent new pipeline
- If both conditions match, prioritize:
  two_entities > has_relation > no_relation
- If no_relation, return attributes info in e1
- Answer json value in vietnamese
- Output must be valid JSON only.

OUTPUT FORMAT (STRICT JSON):
{
  "pipeline": "P?",
  "e1": {
    "type": "...",
    "info": {...}
  },
  "e2": {
    "type": "...",
    "info": {...}
  },
  "target": "e1/e2"
}
"""

    few_shot = [
        {
            "role": "user",
            "content": "Tìm người tên Ngọc Trinh và sống ở Hà Nội"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "pipeline": "P1",
                "e1": {
                    "type": "person",
                    "info": {
                        "name": "Ngọc Trinh",
                        "address": "Hà Nội"
                    }
                },
                "e2": {
                    "type": "",
                    "info": {}
                },
                "target": "e1"
            }, ensure_ascii=False)
        },
        {
            "role": "user",
            "content": "Những người có liên quan đến công ty FPT"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "pipeline": "P2",
                "e1": {
                    "type": "organization",
                    "info": {
                        "name": "công ty FPT"
                    }
                },
                "e2": {
                    "type": "person",
                    "info": {}
                },
                "target": "e2"
            }, ensure_ascii=False)
        },
        {
            "role": "user",
            "content": "Người tên là Bùi Anh Tuấn và hay đi với Ngọc Trinh"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "pipeline": "P2",
                "e1": {
                    "type": "person",
                    "info": {
                        "name": "Bùi Anh Tuấn"
                    }
                },
                "e2": {
                    "type": "person",
                    "info": {
                        "name": "Ngọc Trinh"
                    }
                },
                "target": "e1"
            }, ensure_ascii=False)
        }
    ]

    system_prompt += f"\n\nEXAMPLES:\n{json.dumps(few_shot, ensure_ascii=False)}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    return messages


def build_messages_pipeline_conversation(user_query: str, context: dict, conversation: list) -> list:
    system_prompt = """
You are an AI Query Router with conversation awareness.

Your job is to:
1. Extract entities from user query, context and conversation
   - Understand the current query and exact entities
   - Use CONTEXT to resolve references
   - Use CONVERSATION to understand previous mentions and add information to entities if query is related to previous

2. Determine:
   - source_type (person, organization, event)
   - target_type (if exists)
3. Detect conditions:
   - no_relation: user only asks about entity info
   - has_relation: user asks about connection/related entities (query contains 2 entities)
   - entity_info: id (identity_id, phone, tax_code, ...) OR attributes (keyword) about entity or related entity (name, address, date, job, ...).
   - relation: one_ambiguous / both_ambiguous
4. Keyword extraction:
   - Field name must be standardized (without accents if possible). 
   - All other fields use original keywords (do not standardized).
   - Only extract keywords that are useful for searching in database
   - Example:
        + "làm ca sĩ" → "ca sĩ"
        + "ông Nguyễn Thành" → "Nguyễn Thành"
        + "công tác tại Bộ Công an" → "Bộ Công an"

5. Based on rules below, choose pipeline:
RULES:
- P1: one_entity (no_relation) AND strong_filter/entity_ambiguous
- P2: two_entities (has_relation) AND both_ambiguous/one_ambiguous/expand from known entity

IMPORTANT:
- Only choose ONE pipeline from P1 → P2
- Do NOT invent new pipeline
- If both conditions match, prioritize:
  two_entities > has_relation > no_relation
- Answer json value in vietnamese
- Output must be valid JSON only.

OUTPUT FORMAT (STRICT JSON):
{
  "pipeline": "P?",
  "e1": {
    "type": "...",
    "info": {...}
  },
  "e2": {
    "type": "...",
    "info": {...}
  },
  "target": "e1/e2"
}
"""

    few_shot = [
        {
            "CONVERSATION": [{"role": "user", "content": "Tìm người tên là Anh Tuấn sống ở Hà Nội"}],
            "role": "user",
            "content": "Những người liên quan đến người này"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "pipeline": "P2",
                "e1": {
                    "type": "person",
                    "info": {"name": "Anh Tuấn", "address": "Hà Nội"}
                },
                "e2": {
                    "type": "person",
                    "info": {}
                },
                "target": "e2"
            }, ensure_ascii=False)
        },
        {
            "CONVERSATION": [{"role": "user", "content": "Tìm người tên là Văn Thành sống ở Cầu Giấy"}],
            "role": "user",
            "content": "Người này sinh năm 2002"
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "pipeline": "P1",
                "e1": {
                    "type": "person",
                    "info": {"name": "Văn Thành", "address": "Cầu Giấy", "birth_year": 2002}
                },
                "e2": {
                    "type": "",
                    "info": {}
                },
                "target": "e1"
            }, ensure_ascii=False)
        }
    ]

    system_prompt += f"\n\nEXAMPLES:\n{json.dumps(few_shot, ensure_ascii=False)}"
    if context:
        system_prompt += f"\n\nCONTEXT:\n{json.dumps(context, ensure_ascii=False)}"

    if conversation:
        system_prompt += f"\n\nCONVERSATION:\n{json.dumps(conversation, ensure_ascii=False)}"

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.append({
        "role": "user",
        "content": user_query
    })

    return messages


def build_messages_eval_entity(user_query: str, candidates: list, conversation: list) -> list:
    conversation_text = f"\n- Cuộc hội thoại: {json.dumps(conversation, ensure_ascii=False)} \n - " if conversation else ""

    system_prompt = f"""Bạn là trợ lý tra cứu thông tin từ dữ liệu graph.

    NGỮ CẢNH: {conversation_text} User hỏi: "{user_query}"

    DỮ LIỆU: Agent trả về {len(candidates)} ứng viên (candidates):
    - Mỗi candidate có: name, label (Person/Organization), title, text, properties (thông tin chi tiết)
    - properties chứa các thuộc tính như: profession, role, position, organization, addresss, ...
    - text là mô tả ngắn gọn của entity (VD: "Công ty NCS | profession: Công ty phần mềm | addresss: Việt Nam")

    NHIỆM VỤ:
    1. Chọn candidate phù hợp nhất với query của user
    2. Trả về thông tin chi tiết của candidate đó (name, label, properties, text)
    3. Nếu có nhiều candidates trùng tên: tổng hợp thành các nhóm theo tên và 2-3 thuộc tính quan trọng nhất để phân biệt, sắp xếp theo mức độ phổ biến và nêu rõ nguồn thông tin

    QUY TẮC BẮT BUỘC:
    - Nếu query có tên cụ thể (VD: "tìm công ty NCS"): ưu tiên candidates có name match tên đó
    - Trả lời bằng tiếng Việt, ngắn gọn, có cấu trúc
    - Nêu rõ: tên entity (heading) + label + các thông tin quan trọng từ properties
    - Nếu có nhiều kết quả: liệt kê đầy đủ với số thứ tự, sắp xếp theo mức độ trùng khớp và thời gian gần nhất, hỏi user muốn xem chi tiết cái nào
    - Nếu không có candidate nào match: "Không tìm thấy thông tin phù hợp. Kiểm tra lại câu hỏi hoặc thử với truy vấn khác."
    - KHÔNG bịa thêm thông tin ngoài dữ liệu candidates

    DỮ LIỆU CANDIDATES:
    ```json
    {json.dumps(candidates, ensure_ascii=False)}
    ```"""

    messages = [
        {"role": "system", "content": system_prompt[:LLM["max_input_length"]]},
        {"role": "user", "content": "Đánh giá các entity và trả về kết quả phù hợp nhất"}
    ]

    return messages


def build_messages_eval_entity_relation(user_query: str, candidates: list, conversation) -> list:
    conversation_text = f"\n- Cuộc hội thoại: {json.dumps(conversation, ensure_ascii=False)} \n - " if conversation else ""

    system_prompt = f"""Bạn là trợ lý tra cứu thông tin từ dữ liệu graph.

    NGỮ CẢNH: {conversation_text} User hỏi: "{user_query}"

    DỮ LIỆU: Agent trả về {len(candidates)} khối entity pairs có quan hệ trong graph:
    - Mỗi khối có: e1 (entity 1), e2 (entity 2), via (ID cạnh quan hệ), distance (khoảng cách), target (entity user muốn)
    - Mỗi entity có: name, label (Person/Organization), title, text, properties (thông tin chi tiết)
    - distance càng NHỎ = 2 entities càng GẦN nhau trong graph = match TỐT hơn
    - target chỉ định entity nào là kết quả user cần tìm (e1 hoặc e2)
    - via là ID của cạnh nối e1 và e2 trong graph

    NHIỆM VỤ:
    1. Xếp hạng các blocks theo distance (ưu tiên distance nhỏ nhất)
    2. Chọn blocks phù hợp nhất với query của user
    3. Trả về entity được chỉ định trong "target" của block tốt nhất
    4. Giải thích mối quan hệ giữa e1 và e2 dựa trên context của block

    QUY TẮC BẮT BUỘC:
    - Nếu query có tên cụ thể (VD: "tìm công ty NCS"): ưu tiên blocks có e1/e2.name match tên đó
    - Trả lời bằng tiếng Việt, ngắn gọn, có cấu trúc
    - Nêu rõ: tên entity (heading) + label + thông tin từ properties/text + mối quan hệ với entity còn lại
    - Nếu có nhiều kết quả: liệt kê đầy đủ với số thứ tự, sắp xếp theo thời gian gần nhất, hỏi user muốn xem chi tiết cái nào
    - Nếu không có block nào match: "Không tìm thấy thông tin phù hợp. Kiểm tra lại câu hỏi hoặc thử với truy vấn khác."
    - KHÔNG bịa thêm thông tin ngoài dữ liệu blocks

    DỮ LIỆU BLOCKS:
    ```json
    {json.dumps(candidates, ensure_ascii=False)}
    ```"""

    messages = [
        {"role": "system", "content": system_prompt[:LLM["max_input_length"]]},
        {"role": "user", "content": "Đánh giá các entity blocks và trả về kết quả phù hợp nhất"}
    ]

    return messages
