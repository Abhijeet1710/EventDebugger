from typing import Literal

from pydantic import BaseModel


class TimelineItem(BaseModel):
    type: Literal["STAGE", "ERROR"]

    name: str

    status: Literal[
        "SUCCESS",
        "FAILED",
        "NOT_FOUND",
        "FILTERED_OUT",
        "NOT_REACHED",
        "UNKNOWN"
    ]

    timestamp: str | None = None
    evidence: str | None = None
    description: str | None = None


class InvestigationResult(BaseModel):
    event_id: str

    service: str

    overall_status: Literal[
        "SUCCESS",
        "FAILED",
        "NOT_FOUND",
        "UNKNOWN"
    ]

    timeline: list[TimelineItem]

    summary: str