def fuse(static_findings, llm_result):
    confirmed_checks = {c["check"] for c in llm_result.get("confirmed", [])}
    dismissed_checks = {d["check"] for d in llm_result.get("dismissed", [])}

    final = []

    for f in static_findings:
        check = f["check"]
        if check in dismissed_checks:
            reasoning = next((d["reasoning"] for d in llm_result["dismissed"] if d["check"] == check), "")
            f["status"] = "DISMISSED by LLM"
            f["llm_note"] = reasoning
        else:
            f["status"] = "CONFIRMED" if check in confirmed_checks else "UNREVIEWED"
            if check in confirmed_checks:
                reasoning = next((c["reasoning"] for c in llm_result["confirmed"] if c["check"] == check), "")
                f["llm_note"] = reasoning
            final.append(f)

    for nf in llm_result.get("new_findings", []):
        final.append({
            "tool": "LLM",
            "check": nf["title"],
            "severity": nf["severity"],
            "confidence": "LLM-detected",
            "description": nf["description"],
            "status": "NEW — static tool missed this"
        })

    return final