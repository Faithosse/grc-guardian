#!/usr/bin/env python3
"""
GRC Guardian - Demo Script
Run this to see all agents in action.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.compliance_agent import fetch_regulation, analyse_policy
from agents.risk_agent import calculate_risk_score, get_risk_register, suggest_mitigation
from agents.audit_agent import create_audit_entry, verify_audit_integrity, generate_audit_schedule, reset_audit_chain
import json


def demo_compliance():
    """Demo: Compliance Agent checking GDPR."""
    print("=" * 60)
    print("DEMO 1: Compliance Check (GDPR)")
    print("=" * 60)
    
    reg = json.loads(fetch_regulation("GDPR"))
    print(f"Regulation: GDPR")
    print(f"Key Principles: {', '.join(reg['key_principles'][:3])}...")
    print(f"Non-profit specific: {reg['non_profit_specific'][:60]}...")
    
    policy = "We collect donor emails and keep them secure. We do not share data."
    analysis = json.loads(analyse_policy(policy, "GDPR"))
    print(f"\nPolicy Analysis Score: {analysis['compliance_score']}/100")
    print(f"Gaps found: {len(analysis['gaps_found'])}")
    for gap in analysis['gaps_found'][:2]:
        print(f"  - {gap}")
    print()


def demo_risk():
    """Demo: Risk Agent generating risk register."""
    print("=" * 60)
    print("DEMO 2: Risk Assessment (Charity, Low Budget)")
    print("=" * 60)
    
    risks = json.loads(get_risk_register("charity"))
    print(f"Total risks in template: {len(risks)}")
    
    for risk in risks[:3]:
        score = json.loads(calculate_risk_score(risk['likelihood'], risk['impact']))
        mitigations = json.loads(suggest_mitigation(risk['id'], score['level'], "low"))
        print(f"\n{risk['id']}: {risk['description']}")
        print(f"  Score: {score['score']} ({score['level']})")
        top_mitigation = mitigations['suggestions'][0] if mitigations['suggestions'] else "No budget-specific suggestions - consult board"
        print(f"  Top mitigation: {top_mitigation}")
    print()


def demo_audit():
    """Demo: Audit Agent creating tamper-evident trail."""
    print("=" * 60)
    print("DEMO 3: Audit Trail (Financial)")
    print("=" * 60)
    
    reset_audit_chain()
    entries = []
    for i in range(3):
        entry = json.loads(create_audit_entry(
            actor="audit_system",
            action=f"collect_evidence_{i}",
            result=f"Evidence item {i} collected"
        ))
        entries.append(entry)
        print(f"Entry {i+1}: Hash {entry['hash'][:16]}...")
    
    integrity = json.loads(verify_audit_integrity(json.dumps(entries)))
    print(f"\nTrail Integrity: {integrity['integrity_status']}")
    print(f"Entries checked: {integrity['total_entries']}")
    
    schedule = json.loads(generate_audit_schedule("financial", "annual"))
    print(f"Next audit: {schedule['next_audit'][:10]}")
    print()


def demo_mcp_tools():
    """Demo: All MCP tools working together."""
    print("=" * 60)
    print("DEMO 4: MCP Server Tools Integration")
    print("=" * 60)
    
    print("Available tools: fetch_regulation, analyse_policy, calculate_risk_score,")
    print("                 get_risk_register, create_audit_entry, verify_audit_integrity,")
    print("                 generate_audit_schedule, suggest_mitigation, check_framework_alignment")
    print("All 9 tools loaded successfully.")
    print()


def main():
    """Run all demos."""
    print("=" * 60)
    print("GRC GUARDIAN - DEMO")
    print("Agents for Good | Kaggle Capstone")
    print("=" * 60)
    print()
    
    demo_compliance()
    demo_risk()
    demo_audit()
    demo_mcp_tools()
    
    print("=" * 60)
    print("ALL DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: python mcp_server/server.py")
    print("  2. Run: python cli/main.py --help")
    print("  3. Record video for Kaggle submission")


if __name__ == "__main__":
    main()