from fastapi import APIRouter, Request
from app.services.restaurants import get_restaurant_by_slug, build_restaurant_prompt

router = APIRouter()


@router.post("/assistant-selector")
async def assistant_selector(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    print("ASSISTANT REQUEST BODY:", body)

    message = body.get("message", {}) or {}
    metadata = body.get("metadata", {}) or message.get("metadata", {}) or {}
# restaurant_slug = metadata.get("restaurantSlug") or "pizza-palace"
    restaurant_slug = metadata.get("restaurantSlug")
    print("ASSISTANT restaurantSlug:", restaurant_slug)

    if not restaurant_slug:
        return {"error": "Missing restaurantSlug"}

    restaurant = get_restaurant_by_slug(restaurant_slug)
    print("ASSISTANT restaurant:", restaurant)

    if not restaurant:
        return {"error": "Restaurant not found"}

    prompt = build_restaurant_prompt(restaurant)
    print("ASSISTANT prompt:", prompt)

    return {
        "assistant": {
            "name": f"{restaurant['name']} Assistant",
            "model": {
                "provider": "openai",
                "model": "gpt-4.1",
                "messages": [
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            },
            "voice": {
                "provider": restaurant.get("voice_provider", "vapi"),
                "voiceId": restaurant.get("voice_id", "Elliot")
            },
            "firstMessage": restaurant.get("welcome_message") or f"Hello, welcome to {restaurant['name']}. How can I help you today?"
        }
    }