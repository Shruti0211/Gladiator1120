"""Human approval handling. Approval records are written; no stock is moved."""
from datetime import datetime, timezone
import uuid

from object_storage import write_json_to_object_storage


def record_decision(recommendation: str, decision: str) -> str:
    if decision not in {"approved", "rejected"}:
        raise ValueError("decision must be 'approved' or 'rejected'")

    record_id = str(uuid.uuid4())
    payload = {
        "record_id": record_id,
        "decision": decision,
        "recommendation": recommendation,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_manual_execution" if decision == "approved" else "rejected",
    }
    object_key = f"approvals/{record_id}.json"
    write_json_to_object_storage(object_key, payload)
    return object_key
