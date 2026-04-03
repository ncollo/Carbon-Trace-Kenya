from fastapi import APIRouter

router = APIRouter()


@router.post("/calculate/{company_id}")
async def calculate(company_id: int):
    # Placeholder: enqueue calculation job for company
    return {"status": "started", "company_id": company_id}
