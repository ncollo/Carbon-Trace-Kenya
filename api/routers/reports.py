from fastapi import APIRouter

router = APIRouter()


@router.get("/reports/{id}/pdf")
async def get_report_pdf(id: int):
    # Placeholder: return a URL or streaming response in real implementation
    return {"id": id, "format": "pdf", "url": f"/downloads/{id}.pdf"}


@router.get("/reports/{id}/xbrl")
async def get_report_xbrl(id: int):
    return {"id": id, "format": "xbrl", "url": f"/downloads/{id}.xbrl"}
