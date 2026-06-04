import sys
import json
import os
from datetime import datetime
from analyser.static_runner import run_slither
from analyser.llm_runner import run_llm
from analyser.fusion import fuse

def analyse(contract_path):
    if not os.path.exists(contract_path):
        print(f"Error: file not found: {contract_path}")
        sys.exit(1)

    with open(contract_path, "r") as f:
        code = f.read()

    contract_name = os.path.basename(contract_path)
    print(f"\n{'='*50}")
    print(f"Analysing: {contract_name}")
    print(f"{'='*50}")

    print("\n[Stage 1] Static analysis")
    static_findings = run_slither(contract_path)

    print("\n[Stage 2] LLM reasoning")
    llm_result = run_llm(code, static_findings)

    print("\n[Stage 3] Fusion & ranking")
    final_findings = fuse(static_findings, llm_result)

    print(f"\n{'='*50}")
    print(f"RESULTS — {contract_name}")
    print(f"{'='*50}")
    print(f"Total findings : {len(final_findings)}")
    print(f"Static only    : {sum(1 for f in final_findings if f['tool']=='Slither')}")
    print(f"LLM added      : {sum(1 for f in final_findings if f['tool']=='LLM')}")
    dismissed = sum(1 for f in static_findings if 'DISMISSED' in f.get('status',''))
    print(f"FP dismissed   : {dismissed}")

    print(f"\nVerdict:\n{llm_result.get('verdict','')}")

    print("\nFindings:")
    for i, f in enumerate(final_findings, 1):
        print(f"\n  [{i}] {f['severity'].upper()} — {f['check']}")
        print(f"       Source : {f['tool']}")
        print(f"       Status : {f.get('status','')}")
        print(f"       Detail : {f['description'][:120]}...")

    os.makedirs("results", exist_ok=True)
    output = {
        "contract": contract_name,
        "timestamp": datetime.now().isoformat(),
        "static_findings": static_findings,
        "llm_result": llm_result,
        "final_findings": final_findings
    }
    out_path = f"results/{contract_name.replace('.sol','')}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull results saved to: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py contracts/yourcontract.sol")
        sys.exit(1)
    analyse(sys.argv[1])