"""
GRC Guardian - MCP Server
Provides Model Context Protocol endpoints.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import json
import hashlib
from datetime import datetime, timedelta
from typing import Sequence

app = Server("grc-guardian-mcp")


@app.list_tools()
async def list_tools() -> Sequence[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="fetch_regulation",
            description="Fetch current regulation text and requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "regulation_name": {
                        "type": "string",
                        "description": "Name of regulation (GDPR, NIST_CSF, ISO27001, CHARITY_COMMISSION)"
                    }
                },
                "required": ["regulation_name"]
            }
        ),
        Tool(
            name="analyse_policy",
            description="Analyse a policy document against a compliance framework",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy_text": {"type": "string", "description": "Full text of the policy"},
                    "framework": {"type": "string", "description": "Framework to check against"}
                },
                "required": ["policy_text", "framework"]
            }
        ),
        Tool(
            name="calculate_risk_score",
            description="Calculate risk score using likelihood x impact matrix",
            inputSchema={
                "type": "object",
                "properties": {
                    "likelihood": {"type": "integer", "minimum": 1, "maximum": 5},
                    "impact": {"type": "integer", "minimum": 1, "maximum": 5}
                },
                "required": ["likelihood", "impact"]
            }
        ),
        Tool(
            name="get_risk_register",
            description="Get common risks for a non-profit organisation type",
            inputSchema={
                "type": "object",
                "properties": {
                    "organisation_type": {"type": "string", "enum": ["charity", "social_enterprise"]}
                },
                "required": ["organisation_type"]
            }
        ),
        Tool(
            name="create_audit_entry",
            description="Create a tamper-evident audit log entry with SHA-256 hash",
            inputSchema={
                "type": "object",
                "properties": {
                    "actor": {"type": "string"},
                    "action": {"type": "string"},
                    "result": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["actor", "action", "result"]
            }
        ),
        Tool(
            name="verify_audit_integrity",
            description="Verify integrity of an audit trail by checking hashes",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_entries": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["log_entries"]
            }
        ),
        Tool(
            name="generate_audit_schedule",
            description="Generate audit schedule with reminders",
            inputSchema={
                "type": "object",
                "properties": {
                    "audit_type": {"type": "string"},
                    "frequency": {"type": "string", "enum": ["monthly", "quarterly", "annual", "biannual"]},
                    "start_date": {"type": "string"}
                },
                "required": ["audit_type"]
            }
        ),
        Tool(
            name="suggest_mitigation",
            description="Suggest cost-appropriate risk mitigations for non-profits",
            inputSchema={
                "type": "object",
                "properties": {
                    "risk_id": {"type": "string"},
                    "risk_level": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                    "budget_constraint": {"type": "string", "enum": ["zero", "low", "medium"]}
                },
                "required": ["risk_id", "risk_level"]
            }
        ),
        Tool(
            name="check_framework_alignment",
            description="Check alignment between compliance frameworks",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_frameworks": {"type": "array", "items": {"type": "string"}},
                    "target_framework": {"type": "string"}
                },
                "required": ["current_frameworks", "target_framework"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool invocations."""

    if name == "fetch_regulation":
        regulation_name = arguments.get("regulation_name", "")
        regulations = {
            "GDPR": {
                "key_principles": ["Lawfulness", "Fairness", "Transparency", "Data minimisation",
                                  "Accuracy", "Storage limitation", "Integrity", "Accountability"],
                "non_profit_specific": "Charities must have lawful basis for processing donor data. Consent must be explicit and easily withdrawn.",
                "penalties": "Up to 4% of annual turnover or €20m, whichever is higher"
            },
            "NIST_CSF": {
                "functions": ["Identify", "Protect", "Detect", "Respond", "Recover"],
                "tiers": ["Partial", "Risk Informed", "Repeatable", "Adaptive"],
                "non_profit_note": "Tier 2 (Risk Informed) is realistic target for small non-profits within 12 months",
                "version": "2.0"
            },
            "ISO27001": {
                "annexes": "A.5-A.18 cover organisational, people, physical, and technological controls",
                "certification": "Requires accredited body audit, typically £5k-£15k for small orgs",
                "non_profit_path": "Start with ISO 27001:2022 Annex A self-assessment before pursuing certification"
            },
            "CHARITY_COMMISSION": {
                "duties": ["Public benefit", "Trustee duties", "Annual reporting", "Serious incident reporting"],
                "cyber_requirement": "Trustees must take reasonable steps to protect charity assets including digital assets and donor data",
                "reporting_threshold": "Cyber incidents affecting >1000 individuals or >£25k must be reported within 48 hours"
            }
        }
        result = regulations.get(regulation_name, {"error": f"Regulation '{regulation_name}' not found"})
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "analyse_policy":
        policy_text = arguments.get("policy_text", "")
        framework = arguments.get("framework", "")
        gaps = []
        if framework == "GDPR":
            checks = [
                ("data protection officer", "No mention of Data Protection Officer (DPO) role"),
                ("lawful basis", "Missing lawful basis for processing"),
                ("retention", "No data retention schedule defined"),
                ("subject rights", "No data subject rights procedure"),
                ("breach", "No breach notification process"),
            ]
            for keyword, gap in checks:
                if keyword not in policy_text.lower():
                    gaps.append(gap)
        score = max(0, 100 - len(gaps) * 15)
        return [TextContent(type="text", text=json.dumps({
            "framework": framework, "gaps_found": gaps, "compliance_score": score,
            "recommendations": [f"Address: {gap}" for gap in gaps]
        }, indent=2))]

    elif name == "calculate_risk_score":
        likelihood = arguments.get("likelihood", 1)
        impact = arguments.get("impact", 1)
        score = likelihood * impact
        level = "Low" if score <= 4 else "Medium" if score <= 9 else "High" if score <= 16 else "Critical"
        return [TextContent(type="text", text=json.dumps({
            "likelihood": likelihood, "impact": impact, "score": score, "level": level,
            "recommended_treatment": {
                "Low": "Accept with monitoring", "Medium": "Reduce through controls",
                "High": "Immediate treatment + escalation to board", "Critical": "Urgent board attention + consider stopping activity"
            }[level]
        }, indent=2))]

    elif name == "get_risk_register":
        org_type = arguments.get("organisation_type", "charity")
        risks = {
            "charity": [
                {"id": "R-C01", "description": "Loss of donor data through cyber breach", "category": "Operational", "likelihood": 3, "impact": 4},
                {"id": "R-C02", "description": "Key person dependency (founder/trustee)", "category": "Strategic", "likelihood": 4, "impact": 4},
                {"id": "R-C03", "description": "Funding shortfall due to economic downturn", "category": "Financial", "likelihood": 3, "impact": 5},
                {"id": "R-C04", "description": "Reputational damage from social media incident", "category": "Reputational", "likelihood": 3, "impact": 4},
                {"id": "R-C05", "description": "Volunteer misconduct or safeguarding failure", "category": "Operational", "likelihood": 2, "impact": 5},
            ],
            "social_enterprise": [
                {"id": "R-SE01", "description": "Cash flow interruption", "category": "Financial", "likelihood": 4, "impact": 5},
                {"id": "R-SE02", "description": "Contract dependency on single client", "category": "Strategic", "likelihood": 3, "impact": 4},
                {"id": "R-SE03", "description": "Mission drift from commercial pressures", "category": "Strategic", "likelihood": 3, "impact": 3},
            ]
        }
        return [TextContent(type="text", text=json.dumps(risks.get(org_type, []), indent=2))]

    elif name == "create_audit_entry":
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "actor": arguments.get("actor", "unknown"),
            "action": arguments.get("action", ""),
            "result": arguments.get("result", ""),
            "metadata": arguments.get("metadata", {}),
            "previous_hash": arguments.get("previous_hash", "0")
        }
        entry_str = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()
        return [TextContent(type="text", text=json.dumps(entry, indent=2))]

    elif name == "verify_audit_integrity":
        log_entries = arguments.get("log_entries", [])
        issues = []
        for i, entry in enumerate(log_entries):
            entry_copy = {k: v for k, v in entry.items() if k != "hash"}
            expected = hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()
            if entry.get("hash") != expected:
                issues.append(f"Entry {i}: Hash mismatch")
            if i > 0 and entry.get("previous_hash") != log_entries[i-1].get("hash"):
                issues.append(f"Entry {i}: Chain broken")
        return [TextContent(type="text", text=json.dumps({
            "total_entries": len(log_entries), "issues": issues,
            "integrity_status": "PASS" if not issues else "FAIL",
            "verified_at": datetime.utcnow().isoformat()
        }, indent=2))]

    elif name == "generate_audit_schedule":
        audit_type = arguments.get("audit_type", "General")
        frequency = arguments.get("frequency", "annual")
        start = datetime.fromisoformat(arguments.get("start_date", datetime.utcnow().isoformat()))
        days = {"monthly": 30, "quarterly": 90, "annual": 365, "biannual": 180}.get(frequency, 365)
        schedule = []
        for i in range(4):
            date = start + timedelta(days=days * i)
            schedule.append({
                "audit_number": i + 1, "planned_date": date.isoformat(),
                "reminder_date": (date - timedelta(days=14)).isoformat(),
                "type": audit_type, "status": "Scheduled"
            })
        return [TextContent(type="text", text=json.dumps({
            "audit_type": audit_type, "frequency": frequency, "schedule": schedule,
            "next_audit": schedule[0]["planned_date"], "preparation_reminder": schedule[0]["reminder_date"]
        }, indent=2))]

    elif name == "suggest_mitigation":
        risk_id = arguments.get("risk_id", "")
        risk_level = arguments.get("risk_level", "Medium")
        budget = arguments.get("budget_constraint", "low")
        mitigation_db = {
            "R-C01": ["Enable 2FA on all accounts (free)", "Use password manager (low cost)", "Train staff on phishing (free internal)", "Backup to encrypted cloud (low cost)"],
            "R-C02": ["Document critical processes (free)", "Cross-train volunteers (free)", "Maintain succession plan (free)"],
            "R-C03": ["Diversify funding sources (strategic)", "Build 3-month reserve (financial)", "Apply for emergency grants (reactive)"],
            "R-C04": ["Create social media policy (free)", "Designate single spokesperson (free)", "Monitor brand mentions (free tools)"],
            "R-C05": ["Implement DBS checks (low cost)", "Create safeguarding policy (free template)", "Train safeguarding lead (training cost)"],
            "R-SE01": ["Implement cash flow forecasting (free spreadsheet)", "Negotiate payment terms with suppliers (free)", "Maintain credit line (financial)"],
            "R-SE02": ["Diversify client base (strategic)", "Develop standard contract templates (free)", "Build pipeline of prospects (ongoing)"],
            "R-SE03": ["Document mission statement clearly (free)", "Board review of commercial decisions (free)", "Impact measurement framework (low cost)"],
        }
        suggestions = mitigation_db.get(risk_id, ["Review with board", "Consult sector peers"])
        if budget == "zero":
            suggestions = [s for s in suggestions if "free" in s.lower()]
        elif budget == "low":
            suggestions = [s for s in suggestions if "free" in s.lower() or "low cost" in s.lower()]
        return [TextContent(type="text", text=json.dumps({
            "risk_id": risk_id, "risk_level": risk_level, "budget_constraint": budget,
            "suggestions": suggestions, "priority": "Immediate" if risk_level in ["High", "Critical"] else "Planned"
        }, indent=2))]

    elif name == "check_framework_alignment":
        current = arguments.get("current_frameworks", [])
        target = arguments.get("target_framework", "")
        mappings = {
            ("ISO27001", "NIST_CSF"): {"alignment": "High", "mapping": "ISO 27001 A.5-A.18 map to NIST CSF categories", "gaps": ["Supply chain risk (ID.SC) not explicit in ISO 27001:2013"]},
            ("NIST_CSF", "ISO27001"): {"alignment": "High", "mapping": "NIST CSF functions cover ISO 27001 annexes", "gaps": ["ISO 27001 requires more formal documentation"]},
        }
        key = (current[0], target) if current else (None, target)
        result = mappings.get(key, {"alignment": "Unknown", "note": "Custom mapping required", "gaps": []})
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    """Run the MCP server over stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())