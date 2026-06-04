import os
import json
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are an expert smart contract security auditor specialising in Solidity.
You will receive Solidity source code and findings from a static analysis tool (Slither).
Your job is to:
1. CONFIRM or DISMISS each static finding with clear reasoning
2. IDENTIFY any semantic or logic vulnerabilities the static tool missed
3. Provide a plain-English verdict

Respond ONLY with valid JSON in exactly this format:
{
  "confirmed": [{"check": "...", "reasoning": "..."}],
  "dismissed": [{"check": "...", "reasoning": "..."}],
  "new_findings": [{"severity": "High/Medium/Low", "title": "...", "description": "..."}],
  "verdict": "One paragraph plain English summary of the contract security."
}"""

def run_llm(contract_code, static_findings):
    print("  Sending to LLM (Gemini Flash)...")
    findings_text = json.dumps(static_findings, indent=2) if static_findings else "None"
    prompt = f"""{SYSTEM_PROMPT}

Static analysis findings:
{findings_text}

Solidity contract source code:
```solidity
{contract_code}
```

Respond with JSON only."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        print(f"  LLM confirmed {len(result.get('confirmed',[]))}, "
              f"dismissed {len(result.get('dismissed',[]))}, "
              f"added {len(result.get('new_findings',[]))} new finding(s)")
        return result
    except Exception as e:
        print(f"  LLM error: {e}")
        return {"confirmed": [], "dismissed": [], "new_findings": [], "verdict": "LLM analysis failed."}