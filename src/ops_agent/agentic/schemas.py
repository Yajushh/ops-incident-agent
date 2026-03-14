"""Pydantic schemas for agent outputs and structured responses."""

from typing import Any

from pydantic import BaseModel, Field


class IncidentActionPlan(BaseModel):
    """Final structured response schema for incident triage and response planning."""

    summary: str = Field(..., description="Executive summary of the incident and analysis")
    most_likely_cause: str = Field(..., description="Primary hypothesis for root cause")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score for most_likely_cause (0.0-1.0)"
    )
    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="References to evidence supporting the hypothesis (tool result IDs, signal IDs)",
    )
    immediate_mitigations: list[str] = Field(
        default_factory=list, description="Immediate actions to mitigate the incident"
    )
    verification_steps: list[str] = Field(
        default_factory=list,
        description="Steps to verify the root cause and confirm resolution",
    )
    comms_template: str = Field(
        default="", description="Template for stakeholder communication"
    )
    followups: list[str] = Field(
        default_factory=list, description="Follow-up actions after immediate resolution"
    )
    risk_notes: str = Field(
        default="", description="Risk assessment and potential impact notes"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()