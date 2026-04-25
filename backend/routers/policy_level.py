from fastapi import APIRouter

from schemas.policy_level import PolicyLevelRequest, PolicyLevelResponse
from services.policy_level_classifier import PolicyLevelClassifier

router = APIRouter()


@router.post("/classify", response_model=PolicyLevelResponse)
async def classify_policy_level(payload: PolicyLevelRequest):
    classifier = PolicyLevelClassifier()

    return classifier.classify(
        text=payload.text,
        category=payload.category,
        asta_cita=payload.asta_cita,
        report_count=payload.report_count,
        unique_regions=payload.unique_regions,
    )