"""Agent tools for accessing inventory data."""
from typing import Any

from object_storage import read_csv_from_object_storage


def get_inventory(product_id: str | None = None, store_id: str | None = None) -> list[dict[str, Any]]:
    """
    Read inventory.csv from object storage and optionally filter by product/store.
    This function is the tool exposed to the agent.
    """
    rows = read_csv_from_object_storage("inventory.csv")

    filtered = []
    for row in rows:
        if product_id and row.get("product_id", "").lower() != product_id.lower():
            continue
        if store_id and row.get("store_id", "").lower() != store_id.lower():
            continue

        # Normalize numeric fields for downstream reasoning.
        for field in ("quantity", "daily_demand", "reorder_point"):
            if row.get(field) not in (None, ""):
                try:
                    row[field] = float(row[field])
                except ValueError:
                    pass
        filtered.append(row)

    return filtered


# OpenAI-compatible function-tool schema.
INVENTORY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_inventory",
        "description": (
            "Read inventory.csv from Akamai Object Storage. "
            "Use it to retrieve inventory rows, optionally filtered by product_id or store_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Optional product identifier"},
                "store_id": {"type": "string", "description": "Optional store identifier"},
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name != "get_inventory":
        raise ValueError(f"Unknown tool: {name}")
    return get_inventory(**arguments)
