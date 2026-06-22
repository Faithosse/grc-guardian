"""
GRC Guardian - Compliance Agent
Handles GDPR, NIST CSF, ISO 27001, Charity Commission rules.
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


def fetch_regulation(regulation_name: str) -> str:
    """Fetch current regulation text and requirements."""
    regulations = {
        "GDPR": {
            "key_principles": ["Lawfulness", "Fairness", "Transparency", "Data minimisation",
                              "Accuracy", "Storage limitation", "Integrity", "Accountability"],
            "non_profit_specific": "Charities must have lawful basis for processing donor data. Consent must be explicit.",
            "penalties": "Up to 4% of annual turnover or €20m, whichever is higher"
        },
        "NIST_CSF": {
            "functions": ["Identify", "Protect", "Detect", "Respond", "Recover"],
            "tiers": ["Partial", "Risk Informed", "Repeatable", "Adaptive"],
            "non_profit_note": "Tier 2 (Risk Informed) is realistic target for small non-profits"
        },
        "ISO27001": {
            "annexes": "A.5-A.18 cover organisational, people, physical, and technological controls",
            "certification": "Requires accredited body audit, typically £5k-£15k for small orgs"
        },
        "CHARITY_COMMISSION": {
            "duties": ["Public benefit", "Trustee duties", "Annual reporting", "Serious incident reporting"],
            "cyber_requirement": "Trustees must take reasonable steps to protect charity assets including digital assets"
        }
    }
    return json.dumps(regulations.get(regulation_name, {"error": "Regulation not found"}))


def analyse_policy(policy_text: str, framework: str) -> str:
    """Analyse a policy document against a compliance framework."""
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
    return json.dumps({
        "framework": framework,
        "gaps_found": gaps,
        "compliance_score": score,
        "recommendations": [f"Address: {gap}" for gap in gaps]
    })


def check_framework_alignment(current_frameworks: list, target_framework: str) -> str:
    """Check alignment between compliance frameworks."""
    mappings = {
        ("ISO27001", "NIST_CSF"): {
            "alignment": "High",
            "mapping_notes": "ISO 27001 A.5-A.18 map directly to NIST CSF categories",
            "gaps": ["NIST CSF includes supply chain risk (ID.SC) not explicit in ISO 27001:2013"]
        }
    }
    key = (current_frameworks[0], target_framework) if current_frameworks else (None, target_framework)
    return json.dumps(mappings.get(key, {"alignment": "Unknown", "note": "Mapping not yet defined"}))


if ADK_AVAILABLE:
    compliance_agent = LlmAgent(
        name="compliance_agent",
        model="gemini-2.0-flash",
        description="""You are the Compliance Specialist for GRC Guardian.
You help non-profit organisations understand and meet their regulatory obligations.
You specialise in: GDPR, UK Charity Commission rules, data protection,
NIST Cybersecurity Framework, and ISO 27001 basics.

Always explain regulations in plain English. Provide practical checklists.
Never assume legal authority - always recommend consulting a solicitor for complex cases.""",
        instruction="""Analyse compliance queries using the following process:

1. IDENTIFY: Determine which regulation or framework applies
2. FETCH: Use fetch_regulation tool to get current regulation text if needed
3. ASSESS: Compare the organisation's situation against requirements
4. GAP: Identify what is missing or non-compliant
5. REMEDIATE: Provide specific, actionable remediation steps

Output format:
- regulation: Name of applicable regulation
- applicability: Why this applies to the organisation
- gaps: List of compliance gaps
- actions: Specific remediation steps
- confidence: High/Medium/Low
- summary: One paragraph for non-technical stakeholders""",
        tools=[
            FunctionTool(func=fetch_regulation),
            FunctionTool(func=analyse_policy),
            FunctionTool(func=check_framework_alignment),
        ],
    )
else:
    compliance_agent = LlmAgent(
        name="compliance_agent",
        model="gemini-2.0-flash",
        description="Compliance specialist",
        instruction="Check compliance",
        tools=[]
    )