"""
GRC Guardian - Audit Agent
Creates tamper-evident audit trails with SHA-256 hashing.
"""

try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

    class LlmAgent:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
            self.model = kwargs.get('model')
            self.description = kwargs.get('description')
            self.instruction = kwargs.get('instruction')
            self.tools = kwargs.get('tools', [])
            self.sub_agents = kwargs.get('sub_agents', [])

    class FunctionTool:
        def __init__(self, func):
            self.func = func
            self.name = func.__name__
            self.description = func.__doc__ or ""

import json
import hashlib
from datetime import datetime, timedelta


_last_hash = "0"

def create_audit_entry(actor: str, action: str, result: str, metadata: str = "{}", previous_hash: str = None) -> str:
    """Create a tamper-evident audit log entry with SHA-256 hash."""
    global _last_hash
    meta = json.loads(metadata) if isinstance(metadata, str) else metadata
    prev = previous_hash if previous_hash is not None else _last_hash
    entry = {
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "action": action,
        "result": result,
        "metadata": meta,
        "previous_hash": prev
    }
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()
    _last_hash = entry["hash"]
    return json.dumps(entry)

def reset_audit_chain():
    """Reset the audit hash chain. Call before creating a new independent trail."""
    global _last_hash
    _last_hash = "0"


def verify_audit_integrity(log_entries: str) -> str:
    """Verify integrity of an audit trail by checking hashes."""
    entries = json.loads(log_entries) if isinstance(log_entries, str) else log_entries
    issues = []
    for i, entry in enumerate(entries):
        entry_copy = {k: v for k, v in entry.items() if k != "hash"}
        expected = hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()
        if entry.get("hash") != expected:
            issues.append(f"Entry {i}: Hash mismatch - potential tampering")
        if i > 0 and entry.get("previous_hash") != entries[i-1].get("hash"):
            issues.append(f"Entry {i}: Chain broken")
    return json.dumps({
        "total_entries": len(entries),
        "issues_found": len(issues),
        "issues": issues,
        "integrity_status": "PASS" if not issues else "FAIL",
        "verified_at": datetime.utcnow().isoformat()
    })


def generate_audit_schedule(audit_type: str, frequency: str = "annual", start_date: str = None) -> str:
    """Generate audit schedule with reminders."""
    start = datetime.fromisoformat(start_date) if start_date else datetime.utcnow()
    days = {"monthly": 30, "quarterly": 90, "annual": 365, "biannual": 180}.get(frequency, 365)
    schedule = []
    for i in range(4):
        date = start + timedelta(days=days * i)
        schedule.append({
            "audit_number": i + 1,
            "planned_date": date.isoformat(),
            "reminder_date": (date - timedelta(days=14)).isoformat(),
            "type": audit_type,
            "status": "Scheduled"
        })
    return json.dumps({
        "audit_type": audit_type,
        "frequency": frequency,
        "schedule": schedule,
        "next_audit": schedule[0]["planned_date"],
        "preparation_reminder": schedule[0]["reminder_date"]
    })


if ADK_AVAILABLE:
    audit_agent = LlmAgent(
        name="audit_agent",
        model="gemini-2.0-flash",
        description="""You are the Audit Specialist for GRC Guardian.
You help non-profits maintain proper audit trails, schedule reviews,
and prepare for external audits (funder, regulator, or independent).

You ensure all evidence is timestamped, attributed, and tamper-evident.
You understand that non-profits often lack dedicated audit staff,
so you provide practical, low-burden approaches.""",
        instruction="""Handle audit queries using this process:

1. SCOPE: Determine what is being audited (financial, operational, compliance, IT)
2. PLAN: Identify evidence needed and sources
3. COLLECT: Gather evidence with proper chain of custody using create_audit_entry
4. VERIFY: Check evidence completeness and reliability using verify_audit_integrity
5. REPORT: Generate findings with clear recommendations

For audit trails:
- Every entry must have: timestamp, actor, action, result, hash
- Use SHA-256 for tamper detection
- Maintain append-only log structure
- Separate log storage from application data

Use generate_audit_schedule for planning future audits.""",
        tools=[
            FunctionTool(func=create_audit_entry),
            FunctionTool(func=verify_audit_integrity),
            FunctionTool(func=generate_audit_schedule),
        ],
    )
else:
    audit_agent = LlmAgent(
        name="audit_agent",
        model="gemini-2.0-flash",
        description="Audit specialist",
        instruction="Run audits",
        tools=[]
    )