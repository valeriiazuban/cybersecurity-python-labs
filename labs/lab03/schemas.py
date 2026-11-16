"""Моделі Pydantic для перевірки та форматування даних API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.lab03.config import VALUE_MAX, VALUE_MIN


class CategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(..., min_length=2, max_length=40)


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int = Field(..., gt=0)


class RecordBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    code: str = Field(..., min_length=3, max_length=40)
    title: str = Field(..., min_length=3, max_length=120)
    category_id: int = Field(..., gt=0)
    value: float = Field(..., ge=VALUE_MIN, le=VALUE_MAX, allow_inf_nan=False)
    status: Literal["new", "in_progress", "done"]


class RecordCreate(RecordBase):
    pass


class RecordReplace(RecordBase):
    pass


class RecordRead(RecordBase):
    id: int = Field(..., gt=0)
    category_name: str
