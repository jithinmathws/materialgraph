from fastapi import HTTPException


def ensure_material_found(result: dict) -> None:
    if result.get("mp_id") is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found",
        )