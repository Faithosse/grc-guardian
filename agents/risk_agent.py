"""
GRC Guardian - Risk Agent
Handles risk identification, scoring, and mitigation.
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


def calculate_risk_score(likelihood: int, impact: int) -> str:
    """Calculate risk score using likelihood x impact matrix."""
    score = likelihood * impact
    if score <= 4:
        level = "Low"
    elif score <= 9:
        level = "Medium"
    elif score <= 16:
        level = "High"
    else:
        level = "Critical"
    return json.dumps({
        "likelihood": likelihood, "impact": impact, "score": score, "level": level,
        "recommended_treatment": {
            "Low": "Accept with monitoring",
            "Medium": "Reduce through controls",
            "High": "Immediate treatment + escalation",
            "Critical": "Urgent board attention + consider stopping activity"
        }[level]
    })


def get_risk_register(organisation_type: str) -> str:
    """Get common risks for a non-profit organisation type."""
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
    return json.dumps(risks.get(organisation_type, []))


def suggest_mitigation(risk_id: str, risk_level: str, budget_constraint: str = "low") -> str:
    """Suggest cost-appropriate risk mitigations for non-profits."""
    mitigation_db = {
        "R-C01": ["Enable 2FA on all accounts (free)", "Use password manager (low cost)", "Train staff on phishing (free internal)", "Backup to encrypted cloud (low cost)"],
        "R-C02": ["Document critical processes (free)", "Cross-train volunteers (free)", "Maintain succession plan (free)"],
        "R-C03": ["Diversify funding sources (strategic)", "Build 3-month reserve (financial)", "Apply for emergency grants (reactive)"],
        "R-C04": ["Create social media policy (free)", "Designate single spokesperson (free)", "Monitor brand mentions (free tools)"],
        "R-C05": ["Implement DBS checks (low cost)", "Create safeguarding policy (free template)", "Train safeguarding lead (training cost)"],
        "R-SE01": ["Implement cash flow forecasting (free spreadsheet)", "Negotiate payment terms with suppliers (free)", "Maintain credit line (financial)"],
        "R-SE02": ["Diversify client base (strategic)", "Develop standard contract templates (free)", "Build pipeline of prospects (ongoing)"],
        "R-SE03": ["Document mission statement clearly (free)", "Board review of commercial decisions (free)", "Impact measurement framework (low cost)"],
        "R-SEC01": ["Enable BitLocker/FileVault on all devices (free with OS)", "Use encrypted cloud storage (low cost)", "Document encryption requirements in policy (free)"],
        "R-SEC02": ["Enable 2FA on all accounts (free)", "Use Google Workspace enforced 2FA (free)", "Document MFA requirement in policy (free)"],
        "R-SEC03": ["Implement password policy (12+ chars, complexity) (free)", "Use password manager for shared accounts (low cost)", "Enforce password rotation (free)"],
        "R-SEC04": ["Set up automated cloud backups (low cost)", "Test backup restoration monthly (free)", "Document backup procedure in policy (free)"],
    }
    suggestions = mitigation_db.get(risk_id, ["Review with board", "Consult sector peers"])
    
    if budget_constraint == "zero":
        filtered = [s for s in suggestions if "free" in s.lower()]
        suggestions = filtered if filtered else suggestions
    elif budget_constraint == "low":
        filtered = [s for s in suggestions if "free" in s.lower() or "low cost" in s.lower()]
        suggestions = filtered if filtered else suggestions
    
    return json.dumps({
        "risk_id": risk_id, "risk_level": risk_level, "budget_constraint": budget_constraint,
        "suggestions": suggestions,
        "priority": "Immediate" if risk_level in ["High", "Critical"] else "Planned"
    })


# Create the agent
if ADK_AVAILABLE:
    risk_agent = LlmAgent(
        name="risk_agent",
        model="gemini-2.0-flash",
        description="""You are the Risk Management Specialist for GRC Guardian.
You help non-profits identify, assess, and manage operational and strategic risks.
You use ISO 31000 principles adapted for small organisations.

Focus on practical risk treatment - non-profits rarely have budget for expensive controls.
Prioritise low-cost, high-impact mitigations.""",
        instruction="""Analyse risk queries using this process:

1. IDENTIFY: What risks are mentioned or implied?
2. ANALYSE: Assess likelihood (1-5) and impact (1-5)
3. EVALUATE: Calculate risk score (likelihood x impact)
4. TREAT: Propose mitigation options (Avoid, Reduce, Transfer, Accept)
5. MONITOR: Suggest review frequency

Risk scoring matrix:
- 1-4: Low (Accept or minimal treatment)
- 5-9: Medium (Reduce through controls)
- 10-16: High (Immediate treatment required)
- 17-25: Critical (Urgent board/trustee attention)

Use get_risk_register for sector-specific templates, calculate_risk_score for scoring,
and suggest_mitigation for budget-appropriate treatments.""",
        tools=[
            FunctionTool(func=calculate_risk_score),
            FunctionTool(func=get_risk_register),
            FunctionTool(func=suggest_mitigation),
        ],
    )
else:
    risk_agent = LlmAgent(
        name="risk_agent",
        model="gemini-2.0-flash",
        description="Risk specialist",
        instruction="Assess risks",
        tools=[]
    )