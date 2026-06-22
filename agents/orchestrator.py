"""
GRC Guardian - Orchestrator Agent
Coordinates Compliance, Risk, and Audit agents.
"""

try:
    from google.adk.agents import LlmAgent, SequentialAgent
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
    class SequentialAgent:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name')
            self.sub_agents = kwargs.get('sub_agents', [])
    class FunctionTool:
        def __init__(self, func):
            self.func = func
            self.name = func.__name__
            self.description = func.__doc__ or ""

import json
from .compliance_agent import compliance_agent
from .risk_agent import risk_agent
from .audit_agent import audit_agent


def route_to_compliance(query: str) -> str:
    """Route a compliance-related query to the Compliance Agent."""
    return json.dumps({
        "agent": "compliance",
        "query": query,
        "reason": "Query contains compliance/regulation keywords"
    })


def route_to_risk(query: str) -> str:
    """Route a risk-related query to the Risk Agent."""
    return json.dumps({
        "agent": "risk",
        "query": query,
        "reason": "Query contains risk/threat keywords"
    })


def route_to_audit(query: str) -> str:
    """Route an audit-related query to the Audit Agent."""
    return json.dumps({
        "agent": "audit",
        "query": query,
        "reason": "Query contains audit/evidence keywords"
    })


def synthesise_outputs(compliance_result: str, risk_result: str, audit_result: str) -> str:
    """Synthesise outputs from all three agents into unified guidance."""
    return json.dumps({
        "summary": "Unified GRC assessment complete",
        "compliance": json.loads(compliance_result) if compliance_result else {},
        "risk": json.loads(risk_result) if risk_result else {},
        "audit": json.loads(audit_result) if audit_result else {},
        "actions": [
            "1. Review compliance gaps identified",
            "2. Prioritise high-scoring risks for treatment",
            "3. Schedule next audit based on findings"
        ],
        "confidence": "High"
    })


# Create the orchestrator - NO sub_agents here, uses tools for routing instead
if ADK_AVAILABLE:
    orchestrator_agent = LlmAgent(
        name="grc_orchestrator",
        model="gemini-2.0-flash",
        description="""You are the GRC Guardian Orchestrator. You coordinate three specialist agents:
- Compliance Agent: Handles regulations, policies, framework alignment
- Risk Agent: Identifies, scores, and mitigates risks
- Audit Agent: Creates audit trails, collects evidence, schedules reviews

Your job is to:
1. Understand the user's GRC-related query
2. Determine which specialist agent(s) to invoke
3. Synthesise their outputs into actionable, non-technical guidance
4. Ensure responses are suitable for non-profit staff with limited GRC expertise

Always provide clear, practical advice. Avoid jargon unless explained.""",
        instruction="""Analyse the user's request and determine which specialist agents to invoke.

For compliance questions: Use route_to_compliance
For risk questions: Use route_to_risk
For audit questions: Use route_to_audit
For complex queries: Use multiple tools then synthesise_outputs

Return a structured response with:
- summary: One-paragraph executive summary
- findings: Key points from specialist agent(s)
- actions: Specific, numbered next steps
- confidence: High/Medium/Low""",
        tools=[
            FunctionTool(func=route_to_compliance),
            FunctionTool(func=route_to_risk),
            FunctionTool(func=route_to_audit),
            FunctionTool(func=synthesise_outputs),
        ],
        # NO sub_agents here - agents cannot have two parents
    )
    
    # Sequential workflow owns the sub-agents exclusively
    full_assessment_workflow = SequentialAgent(
        name="full_assessment_pipeline",
        description="Runs compliance, risk, and audit assessments in sequence",
        sub_agents=[compliance_agent, risk_agent, audit_agent],
    )
else:
    orchestrator_agent = LlmAgent(
        name="grc_orchestrator",
        model="gemini-2.0-flash",
        description="Orchestrator",
        instruction="Coordinate agents",
        tools=[],
    )
    full_assessment_workflow = SequentialAgent(
        name="full_assessment_pipeline",
        sub_agents=[compliance_agent, risk_agent, audit_agent],
    )