from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def orders_home():
    return {"message": "orders route working"}