import subprocess
import json
import os

def run_slither(contract_path):
    print(f"  Running Slither on {contract_path}...")
    try:
        result = subprocess.run(
            ["slither", contract_path, "--json", "-"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout:
            data = json.loads(result.stdout)
            findings = []
            for detector in data.get("results", {}).get("detectors", []):
                findings.append({
                    "tool": "Slither",
                    "check": detector.get("check", "unknown"),
                    "severity": detector.get("impact", "Unknown"),
                    "confidence": detector.get("confidence", "Unknown"),
                    "description": detector.get("description", "").strip()
                })
            print(f"  Slither found {len(findings)} issue(s)")
            return findings
        else:
            print("  Slither: no issues found or could not parse output")
            return []
    except Exception as e:
        print(f"  Slither error: {e}")
        return []