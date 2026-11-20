# Akamai Inventory Rescue Agent

A small demo that:
1. Reads `inventory.csv` from Akamai/Linode Object Storage.
2. Exposes that read operation as an agent tool.
3. Uses an OpenAI-compatible Akamai inference endpoint for tool selection and recommendations.
4. Shows recommendations in a Streamlit chat UI.
5. Collects human approval/rejection and writes the decision to Object Storage.

**Safety:** Approval only records a decision under `approvals/`. It does not move inventory or call a production transfer API.

## Repository layout

```text
.
├── object_storage.py   # File 1: S3-compatible object storage read/write
├── inventory_tools.py  # File 2: inventory function + agent tool schema
├── chat_app.py         # File 3: Streamlit chat interface
├── agent.py            # File 4: tool-calling agent + Akamai inference
├── approval.py         # File 5: approval/rejection persistence
├── data/inventory.csv # Sample data to upload
├── .env.example
└── requirements.txt
```

## 1. Create and configure Object Storage

Create an Akamai/Linode Object Storage bucket and access keys. Upload the sample CSV to the bucket root with the exact object key:

```text
inventory.csv
```

The object storage endpoint is region-specific. Set the values in `.env` using the endpoint and credentials from your Akamai console/workshop.

## 2. Configure inference

Set `AKAMAI_INFERENCE_BASE_URL`, `AKAMAI_INFERENCE_API_KEY`, and `AKAMAI_INFERENCE_MODEL` to the values supplied by the workshop.

This demo uses the OpenAI Python SDK's Chat Completions interface and expects the configured inference endpoint to support OpenAI-compatible chat completions and function/tool calling. If your workshop endpoint uses a different API contract, adapt `_client()` and the request in `agent.py`.

## 3. Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your actual values

set -a && source .env && set +a # macOS/Linux
# PowerShell alternative:
# Get-Content .env | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object {
#   $name, $value = $_ -split '=', 2
#   [Environment]::SetEnvironmentVariable($name, $value)
# }

streamlit run chat_app.py
```

## 4. Try it

Ask:

> Find stores at risk of stocking out of P100 and recommend an inventory transfer.

The model should call `get_inventory`, receive the filtered CSV rows, and then generate a recommendation. Review it and click Approve or Reject. The decision JSON is written to `approvals/<uuid>.json`.

## Notes

- Do not commit `.env`; it contains credentials.
- The agent tool only reads inventory. It cannot alter stock.
- The approval step records human intent; execution should be a separate, authenticated workflow.
- For a production system, add input validation, authentication, audit logging, least-privilege object-storage credentials, and idempotency.
- The sample data is illustrative. Upload your own `inventory.csv` with the same columns.
