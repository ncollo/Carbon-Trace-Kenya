from fastapi import APIRouter

router = APIRouter()


@router.get("/anomalies")
async def list_anomalies():
    # Placeholder: return empty list
    return {"anomalies": []}


@router.patch("/anomalies/{id}/resolve")
async def resolve_anomaly(id: int):
    # Placeholder: mark anomaly resolved
    return {"id": id, "resolved": True}
