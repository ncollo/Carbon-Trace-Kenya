from fastapi import APIRouter, Depends
from api.auth import get_current_user

router = APIRouter()


@router.post("/calculate/{company_id}")
async def calculate(company_id: int, _user=Depends(get_current_user)):
    # Protected endpoint: enqueue calculation job for company
    return {"status": "started", "company_id": company_id}
