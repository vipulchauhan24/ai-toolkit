from fastapi import APIRouter

router = APIRouter()


@router.get("/orders")
async def list_orders() -> list:
    return []
