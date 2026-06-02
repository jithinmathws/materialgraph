import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.graph_job import JobStatus


class GraphJobCreate(BaseModel):
    job_type: str
    input_json: dict[str, Any] = Field(default_factory=dict)


class GraphJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_type: str
    status: JobStatus
    input_json: dict[str, Any]
    result_json: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None