# from fastapi import APIRouter, Request
# from app.services.retrieval import search_menu
# from app.services.restaurants import get_restaurant_by_slug

# router = APIRouter()


# @router.post("/search")
# async def kb_search(request: Request):
#     try:
#         body = await request.json()
#     except Exception:
#         body = {}

#     print("KB RAW BODY:", body)

#     message = body.get("message", {}) or {}
#     messages = message.get("messages", []) or []
#     restaurant_slug = None

# # 1. Try metadata first
#     metadata = body.get("metadata", {}) or message.get("metadata", {}) or {}
#     restaurant_slug = metadata.get("restaurantSlug")

#     # 2. If not found, get from assistant.name
#     if not restaurant_slug:
#         assistant = body.get("assistant", {}) or {}
#         restaurant_slug = assistant.get("name")

#     print("KB restaurantSlug:", restaurant_slug)

#     if not restaurant_slug:
#         print("❌ No restaurant slug found!")
#         return {"documents": []}

#     restaurant = get_restaurant_by_slug(restaurant_slug)
#     print("KB restaurant:", restaurant)

#     if not restaurant:
#         return {"documents": []}

#     user_query = ""
#     for msg in reversed(messages):
#         if msg.get("role") == "user":
#             content = msg.get("message", "") or msg.get("content", "")
#             if isinstance(content, str):
#                 user_query = content
#             break

#     print("KB user_query:", user_query)

#     if not user_query:
#         return {"documents": []}

#     results = search_menu(restaurant["id"], user_query, match_count=5)
#     print("KB results:", results)

#     return {
#         "documents": [
#             {
#                 "content": row["content"],
#                 "uuid": str(row["id"]),
#                 "similarity": row.get("similarity", 0.9)
#             }
#             for row in results
#         ]
#     }


from fastapi import APIRouter, Request
from app.services.retrieval import search_menu
from app.services.restaurants import get_restaurant_by_slug

router = APIRouter()


def extract_latest_user_query(body: dict) -> str:
    message = body.get("message", {}) or {}
    messages = message.get("messages", []) or []

    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("message", "") or msg.get("content", "")
            if isinstance(content, str):
                return content.strip()
    return ""


def normalize_query(user_query: str) -> str:
    q = user_query.lower().strip()

    if "pepperoni" in q and "pizza" not in q:
        q += " pizza"

    if "classic" in q and "burger" not in q:
        q += " burger"

    if "cheeseburger" in q:
        q = q.replace("cheeseburger", "cheese burger")

    if "smash" in q and "burger" not in q:
        q += " burger"

    if "price" not in q and "cost" not in q:
        q += " price"

    return q


@router.post("/{restaurant_slug}/search")
async def kb_search_by_restaurant(restaurant_slug: str, request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    print("KB PATH restaurant_slug:", restaurant_slug)
    print("KB RAW BODY:", body)

    restaurant = get_restaurant_by_slug(restaurant_slug)
    print("KB restaurant:", restaurant)

    if not restaurant:
        print("❌ Restaurant not found in database!")
        return {"documents": []}

    user_query = extract_latest_user_query(body)
    print("KB user_query:", user_query)

    if not user_query:
        print("❌ No user query found!")
        return {"documents": []}

    normalized_query = normalize_query(user_query)
    print("KB normalized_query:", normalized_query)

    results = search_menu(restaurant["id"], normalized_query, match_count=5)
    print("KB results count:", len(results))
    print("KB results:", results)

    return {
        "documents": [
            {
                "content": row["content"],
                "uuid": str(row["id"]),
                "similarity": row.get("similarity", 0.9)
            }
            for row in results
        ]
    }