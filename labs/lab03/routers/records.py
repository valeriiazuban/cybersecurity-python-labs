import sqlite3

from fastapi import APIRouter, HTTPException, Path, Query, status

from labs.lab03 import repository
from labs.lab03.config import VALUE_MAX, VALUE_MIN
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=list[RecordRead])
def list_records(
    category_id: int | None = Query(None, gt=0),
    status_filter: str | None = Query(None, alias="status"),
    min_value: float | None = Query(None, ge=VALUE_MIN, le=VALUE_MAX),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return repository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int = Path(..., gt=0)):
    rec = repository.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено"
        )
    return rec


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: RecordCreate):
    try:
        return repository.create_record(
            code=payload.code,
            title=payload.title,
            category_id=payload.category_id,
            value=payload.value,
            status=payload.status,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказану категорію не знайдено",
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )


@router.put("/{record_id}", response_model=RecordRead)
def update_record(payload: RecordReplace, record_id: int = Path(..., gt=0)):
    try:
        updated = repository.update_record(
            record_id=record_id,
            code=payload.code,
            title=payload.title,
            category_id=payload.category_id,
            value=payload.value,
            status=payload.status,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено"
            )
        return updated
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказану категорію не знайдено",
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int = Path(..., gt=0)):
    deleted = repository.delete_record(record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено"
        )


@router.post(
    "/bulk", response_model=list[RecordRead], status_code=status.HTTP_201_CREATED
)
def create_records_bulk(payload: list[RecordCreate]):
    if not 1 <= len(payload) <= 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Розмір пакета повинен бути від 1 до 100 елементів",
        )
    try:
        records_data = [item.model_dump() for item in payload]
        return repository.create_records_bulk(records_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Неіснуюча категорія в пакеті: {e}",
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфлікт унікальності або повтор коду в пакеті",
        )
