"""Головний модуль FastAPI-застосунку."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from labs.lab03.config import DOMAIN_DESCRIPTION, DOMAIN_TITLE, THRESHOLD, UNIT
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared import student


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=DOMAIN_TITLE,
    description=f"{DOMAIN_DESCRIPTION} Одиниця вимірювання: {UNIT}, поріг: {THRESHOLD}.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["System"])
def ping():
    return {"status": "ok"}


@app.get("/student", tags=["System"])
def get_student():
    return {
        "student_name": student.STUDENT_NAME,
        "group_name": student.GROUP_NAME,
        "variant_number": student.VARIANT_NUMBER,
    }
