from fastapi import APIRouter
from ..services.hr_copilot.hr_copilot_tool import HRCopilotTool

router = APIRouter()
hr = HRCopilotTool()

@router.post("/process_call")
def process_call(candidate_id: int, answers: list[str]):
    result = hr.run(answers)
    result["candidate_id"] = candidate_id
    return result
