"""Agent orchestration: tool call -> inventory data -> Akamai inference recommendations."""
import json
import os
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv

from inventory_tools import INVENTORY_TOOL, execute_tool

load_dotenv()


SYSTEM_PROMPT = """
You are an inventory rescue agent for a retail supply chain.
Use the get_inventory tool before making inventory recommendations.
Identify stores at stockout risk using quantity and daily_demand.
Look for other stores with transferable surplus. Be conservative:
- Do not recommend transferring more than the source store's available surplus.
- Explain assumptions and show the source and destination stores.
- If the data is insufficient, say so rather than inventing facts.
- Do not claim that a transfer has been executed. Recommendations require human approval.
Return concise, actionable recommendations with product, stores, quantities, and reasoning.
"""


def _client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["AKAMAI_INFERENCE_API_KEY"],
        base_url=os.environ["AKAMAI_INFERENCE_BASE_URL"],
    )


def run_agent(user_request: str) -> str:
    """
    Run a tool-calling loop against an OpenAI-compatible Akamai inference endpoint.
    The model decides when to call get_inventory; tool output is then supplied
    back to the model to produce recommendations.
    """
    client = _client()
    model = os.environ["AKAMAI_INFERENCE_MODEL"]

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_request},
    ]

    # Permit a small number of tool-call rounds to keep the demo bounded.
    for _ in range(3):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[INVENTORY_TOOL],
            tool_choice="auto",
            temperature=0.2,
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))

        tool_calls = assistant_message.tool_calls or []
        if not tool_calls:
            return assistant_message.content or "The model returned an empty response."

        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")
            result = execute_tool(name, arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

    # One final inference call after tool execution.
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )
    return final_response.choices[0].message.content or "No recommendation was generated."
