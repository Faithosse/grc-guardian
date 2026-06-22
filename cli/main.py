"""
GRC Guardian - CLI (Agent Skills)
5 commands: check-compliance, assess-risk, run-audit, full-assessment, interactive
All commands now support --policy-file for real company assessments.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agents.compliance_agent import fetch_regulation, analyse_policy
from agents.risk_agent import calculate_risk_score, get_risk_register, suggest_mitigation
from agents.audit_agent import create_audit_entry, verify_audit_integrity, generate_audit_schedule, reset_audit_chain

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="grc-guardian")
def cli():
    """GRC Guardian - Governance, Risk, and Compliance for Non-Profits"""
    pass


def load_policy(policy_file):
    """Helper: Load policy file if it exists."""
    if policy_file and os.path.exists(policy_file):
        with open(policy_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# ═══════════════════════════════════════════════════════════════
# SKILL 1: Compliance Check
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option("--framework", "-f", default="GDPR", help="Framework: GDPR, NIST_CSF, ISO27001, CHARITY_COMMISSION")
@click.option("--query", "-q", required=True, help="Your compliance question")
@click.option("--policy-file", "-p", type=click.Path(), help="Path to policy file to analyse")
def check_compliance(framework, query, policy_file):
    """Check compliance against a regulatory framework."""
    console.print(Panel(f"[bold blue]Compliance Check: {framework}[/bold blue]", subtitle=query[:60] + "..." if len(query) > 60 else query))
    
    reg = json.loads(fetch_regulation(framework))
    console.print(f"\n[bold]Regulation:[/bold] {framework}")
    console.print(f"[bold]Key Info:[/bold] {reg.get('non_profit_specific', 'N/A')[:100]}...")
    
    policy_context = load_policy(policy_file)
    if policy_context:
        console.print(f"[dim]Policy loaded: {policy_file} ({len(policy_context)} chars)[/dim]")
        analysis = json.loads(analyse_policy(policy_context, framework))
        console.print(f"\n[bold]Policy Score:[/bold] {analysis['compliance_score']}/100")
        if analysis['gaps_found']:
            console.print("[bold red]Gaps Found:[/bold red]")
            for gap in analysis['gaps_found']:
                console.print(f"  • {gap}")
        if analysis['recommendations']:
            console.print("\n[bold green]Recommendations:[/bold green]")
            for rec in analysis['recommendations'][:3]:
                console.print(f"  ✓ {rec}")
    else:
        console.print("[dim]No policy file provided - using generic assessment[/dim]")
    
    console.print(f"\n[italic]Query: {query}[/italic]")


# ═══════════════════════════════════════════════════════════════
# SKILL 2: Risk Assessment (Policy-Aware)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option("--org-type", "-t", default="charity", help="Organisation type")
@click.option("--budget", "-b", default="low", help="Budget constraint: zero, low, medium")
@click.option("--policy-file", "-p", type=click.Path(), help="Policy document for context")
def assess_risk(org_type, budget, policy_file):
    """Assess organisational risks with scoring and mitigations."""
    console.print(Panel(f"[bold yellow]Risk Assessment: {org_type}[/bold yellow]", subtitle=f"Budget: {budget}"))
    
    policy_context = load_policy(policy_file)
    if policy_context:
        console.print(f"[dim]Policy context loaded: {policy_file} ({len(policy_context)} chars)[/dim]\n")
    
    risks = json.loads(get_risk_register(org_type))
    
    # Add policy-specific risks based on analyse_policy results
    policy_risks = []
    if policy_context:
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        gaps = analysis.get("gaps_found", [])
        
        # Map gaps to risks
        for gap in gaps:
            gap_lower = gap.lower()
            if "dpo" in gap_lower or "protection officer" in gap_lower:
                policy_risks.append({"id": "R-P01", "description": "No Data Protection Officer appointed", "category": "Compliance", "likelihood": 4, "impact": 5})
            elif "lawful basis" in gap_lower:
                policy_risks.append({"id": "R-P02", "description": "Missing lawful basis for processing activities", "category": "Compliance", "likelihood": 4, "impact": 4})
            elif "retention" in gap_lower:
                policy_risks.append({"id": "R-P03", "description": "No data retention schedule defined", "category": "Compliance", "likelihood": 3, "impact": 4})
            elif "subject rights" in gap_lower or "rights procedure" in gap_lower:
                policy_risks.append({"id": "R-P04", "description": "No data subject rights procedure", "category": "Compliance", "likelihood": 3, "impact": 4})
            elif "breach" in gap_lower or "notification" in gap_lower:
                policy_risks.append({"id": "R-P05", "description": "No breach notification process (72h rule)", "category": "Compliance", "likelihood": 3, "impact": 5})
            else:
                # Generic policy gap risk
                policy_risks.append({"id": f"R-P{len(policy_risks)+1:02d}", "description": f"Policy gap: {gap}", "category": "Compliance", "likelihood": 3, "impact": 4})
        
        # Also check for missing security keywords
        policy_lower = policy_context.lower()
        if "encryption" not in policy_lower and "encrypt" not in policy_lower:
            policy_risks.append({"id": "R-SEC01", "description": "No mention of encryption in policy", "category": "Operational", "likelihood": 3, "impact": 4})
        if "multi-factor" not in policy_lower and "two-factor" not in policy_lower and "2fa" not in policy_lower and "mfa" not in policy_lower:
            policy_risks.append({"id": "R-SEC02", "description": "No multi-factor authentication requirement", "category": "Operational", "likelihood": 3, "impact": 4})
        if "password" not in policy_lower:
            policy_risks.append({"id": "R-SEC03", "description": "No password policy defined", "category": "Operational", "likelihood": 3, "impact": 3})
        if "backup" not in policy_lower:
            policy_risks.append({"id": "R-SEC04", "description": "No backup procedure mentioned", "category": "Operational", "likelihood": 3, "impact": 4})
        
        risks.extend(policy_risks)
    
    table = Table(title=f"Risk Register ({len(risks)} risks)")
    table.add_column("ID", style="bold")
    table.add_column("Description")
    table.add_column("Score", justify="right")
    table.add_column("Level")
    table.add_column("Mitigation")
    
    for risk in risks:
        score = json.loads(calculate_risk_score(risk['likelihood'], risk['impact']))
        mitigations = json.loads(suggest_mitigation(risk['id'], score['level'], budget))
        color = {"Critical": "red", "High": "orange3", "Medium": "yellow", "Low": "green"}.get(score['level'], "white")
        top_mit = mitigations['suggestions'][0] if mitigations['suggestions'] else "Consult board"
        table.add_row(
            risk['id'],
            risk['description'][:40] + "...",
            str(score['score']),
            f"[{color}]{score['level']}[/{color}]",
            top_mit[:40] + "..."
        )
    
    console.print(table)
    
    # Priority actions based on policy
    console.print("\n[bold green]Priority Actions:[/bold green]")
    if policy_context:
        if "encryption" not in policy_context.lower() and "encrypt" not in policy_context.lower():
            console.print("  ⚡ Enable BitLocker (Windows) or FileVault (Mac) - free with OS")
        if "multi-factor" not in policy_context.lower() and "two-factor" not in policy_context.lower() and "2fa" not in policy_context.lower() and "mfa" not in policy_context.lower():
            console.print("  ⚡ Enable Google Workspace 2FA for all accounts - free")
        if "no formal breach notification" in policy_context.lower():
            console.print("  ⚡ Create GDPR breach response procedure - ICO template free")
        if "kept indefinitely" in policy_context.lower():
            console.print("  ⚡ Define data retention schedule - ICO template free")
        if "no formal password policy" in policy_context.lower():
            console.print("  ⚡ Implement password policy (12+ chars, complexity) - free")
        if "share donor data" in policy_context.lower():
            console.print("  ⚡ Document Data Processing Agreement with mailing house")
    else:
        console.print("  ⚡ Review top-scoring risks from register above")
    
    result = {"risks": risks, "org_type": org_type, "budget": budget, "policy_analysed": bool(policy_context), "timestamp": datetime.now().isoformat()}
    policy_count = len([r for r in risks if r['id'].startswith('R-P') or r['id'].startswith('R-SEC')])
    console.print(f"\n[dim]Analysed {len(risks)} risks including {policy_count} policy-specific findings[/dim]")


# ═══════════════════════════════════════════════════════════════
# SKILL 3: Audit Runner (Policy-Aware)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option("--type", "-t", default="general", help="Audit type")
@click.option("--schedule", is_flag=True, help="Generate future schedule")
@click.option("--policy-file", "-p", type=click.Path(), help="Policy document to audit against")
def run_audit(type, schedule, policy_file):
    """Run an audit with evidence collection and integrity checks."""
    console.print(Panel(f"[bold magenta]Audit: {type}[/bold magenta]"))
    
    policy_context = load_policy(policy_file)
    if policy_context:
        console.print(f"[dim]Auditing against policy: {policy_file} ({len(policy_context)} chars)[/dim]\n")
    
    reset_audit_chain()
    evidence = []
    
    if policy_context:
        # Evidence 1: Policy document hash
        import hashlib
        policy_hash = hashlib.sha256(policy_context.encode()).hexdigest()
        entry = json.loads(create_audit_entry(
            actor="audit_system",
            action="policy_document_review",
            result=f"Policy reviewed: {len(policy_context)} chars, SHA-256: {policy_hash[:16]}...",
            metadata=json.dumps({"source": policy_file, "hash": policy_hash})
        ))
        evidence.append(entry)
        console.print(f"  📋 Policy document evidence: {entry['hash'][:16]}...")
        
        # Evidence 2: Gap findings from policy analysis
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        gaps = analysis.get("gaps_found", [])
        
        # Also check for missing security controls
        policy_lower = policy_context.lower()
        security_gaps = []
        if "encryption" not in policy_lower and "encrypt" not in policy_lower:
            security_gaps.append("No encryption mentioned")
        if "multi-factor" not in policy_lower and "two-factor" not in policy_lower and "2fa" not in policy_lower and "mfa" not in policy_lower:
            security_gaps.append("No MFA requirement")
        if "password" not in policy_lower:
            security_gaps.append("No password policy")
        if "backup" not in policy_lower:
            security_gaps.append("No backup procedure")
        
        all_findings = gaps + security_gaps
        
        entry = json.loads(create_audit_entry(
            actor="audit_system",
            action="gap_identification",
            result=f"Identified {len(all_findings)} gaps: {', '.join(all_findings) if all_findings else 'None'}",
            metadata=json.dumps({"gaps": gaps, "security_gaps": security_gaps})
        ))
        evidence.append(entry)
        console.print(f"  📋 Gap identification evidence: {entry['hash'][:16]}...")
        
        # Evidence 3: Control assessment
        controls = []
        if "dpo" in policy_lower or "protection officer" in policy_lower:
            controls.append("DPO appointed")
        if "breach" in policy_lower and "72" in policy_lower:
            controls.append("Breach notification procedure (72h)")
        if "subject access" in policy_lower or "individual rights" in policy_lower:
            controls.append("Individual rights procedure")
        if "retention" in policy_lower:
            controls.append("Retention mentioned")
        if "password" in policy_lower:
            controls.append("Passwords mentioned")
        
        entry = json.loads(create_audit_entry(
            actor="audit_system",
            action="control_assessment",
            result=f"Controls assessed: {len(controls)} present, {len(all_findings)} gaps",
            metadata=json.dumps({"controls": controls, "gaps": all_findings})
        ))
        evidence.append(entry)
        console.print(f"  📋 Control assessment evidence: {entry['hash'][:16]}...")
    else:
        # Generic evidence if no policy
        for i in range(3):
            entry = json.loads(create_audit_entry(
                actor="audit_system",
                action=f"collect_evidence_{type}_{i}",
                result=f"Evidence collected for {type} audit item {i}"
            ))
            evidence.append(entry)
            console.print(f"  🔒 {entry['hash'][:16]}... | {entry['action']}")
    
    # Verify integrity
    integrity = json.loads(verify_audit_integrity(json.dumps(evidence)))
    status = "[green]✓ PASS[/green]" if integrity['integrity_status'] == "PASS" else "[red]✗ FAIL[/red]"
    console.print(f"\n[bold]Trail Integrity: {status}[/bold]")
    console.print(f"  Entries: {integrity['total_entries']} | Issues: {integrity['issues_found']}")
    
    # Schedule
    if schedule:
        sched = json.loads(generate_audit_schedule(type, "annual"))
        console.print(f"\n[bold]Next Audit:[/bold] {sched['next_audit'][:10]}")
        console.print(f"[bold]Preparation Reminder:[/bold] {sched['preparation_reminder'][:10]}")
    
    # Findings summary
    if policy_context:
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        gaps = analysis.get("gaps_found", [])
        policy_lower = policy_context.lower()
        
        console.print(f"\n[bold]Policy-Based Findings:[/bold]")
        for gap in gaps:
            console.print(f"  [red]MAJOR[/red] {gap}")
        
        # Security gaps
        if "encryption" not in policy_lower and "encrypt" not in policy_lower:
            console.print("  [orange3]MAJOR[/orange3] No encryption mentioned - data at rest/transit risk")
        if "multi-factor" not in policy_lower and "two-factor" not in policy_lower and "2fa" not in policy_lower and "mfa" not in policy_lower:
            console.print("  [orange3]MAJOR[/orange3] No MFA requirement - account compromise risk")
        if "password" not in policy_lower:
            console.print("  [yellow]MINOR[/yellow] No password policy defined")
        if "backup" not in policy_lower:
            console.print("  [yellow]MINOR[/yellow] No backup procedure mentioned")


# ═══════════════════════════════════════════════════════════════
# SKILL 4: Full Assessment (Policy-Aware)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option("--org-type", "-t", default="charity", help="Organisation type")
@click.option("--output", "-o", type=click.Path(), help="Save report to file")
@click.option("--policy-file", "-p", type=click.Path(), help="Policy document to analyse")
def full_assessment(org_type, output, policy_file):
    """Run complete GRC assessment using policy document."""
    console.print(Panel("[bold cyan]GRC Guardian - Full Assessment[/bold cyan]", subtitle=f"Organisation: {org_type}"))
    
    policy_context = load_policy(policy_file)
    if policy_context:
        console.print(f"[dim]Analysing policy: {policy_file} ({len(policy_context)} chars)[/dim]\n")
    
    # 1. Compliance
    console.print("[bold]1. Compliance Check[/bold]")
    compliance_score = 0
    gaps = []
    if policy_context:
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        compliance_score = analysis['compliance_score']
        gaps = analysis['gaps_found']
        console.print(f"  Score: {compliance_score}/100")
        console.print(f"  Gaps: {len(gaps)}")
        for gap in gaps[:3]:
            console.print(f"    • {gap}")
    else:
        console.print("  No policy file - using generic compliance check")
    
    # 2. Risk
    console.print("\n[bold]2. Risk Assessment[/bold]")
    risks = json.loads(get_risk_register(org_type))
    policy_risks = 0
    if policy_context:
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        policy_gaps = analysis.get("gaps_found", [])
        for gap in policy_gaps:
            gap_lower = gap.lower()
            if "dpo" in gap_lower:
                risks.append({"id": "R-P01", "description": "No DPO appointed", "likelihood": 4, "impact": 5})
                policy_risks += 1
            elif "lawful basis" in gap_lower:
                risks.append({"id": "R-P02", "description": "Missing lawful basis", "likelihood": 4, "impact": 4})
                policy_risks += 1
            elif "retention" in gap_lower:
                risks.append({"id": "R-P03", "description": "No retention schedule", "likelihood": 3, "impact": 4})
                policy_risks += 1
            elif "subject rights" in gap_lower or "rights procedure" in gap_lower:
                risks.append({"id": "R-P04", "description": "No subject rights procedure", "likelihood": 3, "impact": 4})
                policy_risks += 1
            elif "breach" in gap_lower:
                risks.append({"id": "R-P05", "description": "No breach notification procedure", "likelihood": 3, "impact": 5})
                policy_risks += 1
        
        policy_lower = policy_context.lower()
        if "encryption" not in policy_lower and "encrypt" not in policy_lower:
            risks.append({"id": "R-SEC01", "description": "No encryption mentioned", "likelihood": 3, "impact": 4})
            policy_risks += 1
        if "multi-factor" not in policy_lower and "two-factor" not in policy_lower and "2fa" not in policy_lower and "mfa" not in policy_lower:
            risks.append({"id": "R-SEC02", "description": "No MFA requirement", "likelihood": 3, "impact": 4})
            policy_risks += 1
        if "password" not in policy_lower:
            risks.append({"id": "R-SEC03", "description": "No password policy", "likelihood": 3, "impact": 3})
            policy_risks += 1
        if "backup" not in policy_lower:
            risks.append({"id": "R-SEC04", "description": "No backup procedure", "likelihood": 3, "impact": 4})
            policy_risks += 1
    
    high_risks = [r for r in risks if json.loads(calculate_risk_score(r['likelihood'], r['impact']))['level'] in ['High', 'Critical']]
    policy_risk_count = len([r for r in risks if r['id'].startswith('R-P') or r['id'].startswith('R-SEC')])
    console.print(f"  Total risks: {len(risks)} ({policy_risk_count} from policy)")
    console.print(f"  High/Critical: {len(high_risks)}")
    
    # 3. Audit
    console.print("\n[bold]3. Audit Trail[/bold]")
    reset_audit_chain()
    entry = json.loads(create_audit_entry("system", "full_assessment", "complete"))
    console.print(f"  Entry hash: {entry['hash'][:20]}...")
    
    # Synthesis
    console.print("\n[bold green]Synthesis[/bold green]")
    console.print("  ✓ Compliance framework checked")
    console.print("  ✓ Risk register generated with policy-specific findings")
    console.print("  ✓ Audit trail established")
    
    if policy_context:
        console.print("\n[bold]Policy-Specific Recommendations:[/bold]")
        rec_num = 1
        policy_lower = policy_context.lower()
        
        # Check analyse_policy gaps
        analysis = json.loads(analyse_policy(policy_context, "GDPR"))
        for gap in analysis.get("gaps_found", []):
            gap_lower = gap.lower()
            if "dpo" in gap_lower:
                console.print(f"  {rec_num}. Appoint a Data Protection Officer (DPO)")
                rec_num += 1
            elif "lawful basis" in gap_lower:
                console.print(f"  {rec_num}. Document lawful basis for all processing activities")
                rec_num += 1
            elif "retention" in gap_lower:
                console.print(f"  {rec_num}. Define specific data retention schedule (ICO template - free)")
                rec_num += 1
            elif "subject rights" in gap_lower or "rights procedure" in gap_lower:
                console.print(f"  {rec_num}. Create data subject rights procedure (ICO template - free)")
                rec_num += 1
            elif "breach" in gap_lower:
                console.print(f"  {rec_num}. Create GDPR breach response procedure (ICO template - free)")
                rec_num += 1
        
        # Security gaps
        if "encryption" not in policy_lower and "encrypt" not in policy_lower:
            console.print(f"  {rec_num}. Enable device encryption (BitLocker/FileVault - free with OS)")
            rec_num += 1
        if "multi-factor" not in policy_lower and "two-factor" not in policy_lower and "2fa" not in policy_lower and "mfa" not in policy_lower:
            console.print(f"  {rec_num}. Enable 2FA on all accounts (Google Workspace enforced 2FA - free)")
            rec_num += 1
        if "password" not in policy_lower:
            console.print(f"  {rec_num}. Implement password policy (12+ chars, complexity - free)")
            rec_num += 1
        if "backup" not in policy_lower:
            console.print(f"  {rec_num}. Set up automated backups and test restoration (low cost)")
            rec_num += 1
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "organisation_type": org_type,
        "policy_analysed": bool(policy_context),
        "policy_file": policy_file if policy_context else None,
        "compliance": {"framework": "GDPR", "score": compliance_score, "gaps": len(gaps)},
        "risk": {"total": len(risks), "high": len(high_risks), "policy_specific": policy_risk_count},
        "audit": {"entry_hash": entry['hash']}
    }
    
    if output:
        import os
        import glob
        
        base, ext = os.path.splitext(output)
        # Rolling log: keep 10 entries (filename_1.json through filename_10.json)
        existing = sorted(glob.glob(f"{base}_*[0-9]{ext}"))
        
        if not existing:
            output = f"{base}_1{ext}"
            report["sequence"] = 1
        else:
            highest = 0
            for fpath in existing:
                try:
                    num = int(os.path.splitext(fpath)[0].split("_")[-1])
                    highest = max(highest, num)
                except:
                    pass
            
            if highest >= 10:
                output = f"{base}_1{ext}"
                report["sequence"] = 1
                console.print(f"[dim]Rolling log full (10 entries). Overwriting {output}[/dim]")
            else:
                next_num = highest + 1
                output = f"{base}_{next_num}{ext}"
                report["sequence"] = next_num
        
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[dim]Report saved to {output} (entry {report['sequence']}/10)[/dim]")


# ═══════════════════════════════════════════════════════════════
# SKILL 5: Interactive Mode
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option("--policy-file", "-p", type=click.Path(), help="Load policy for context")
def interactive(policy_file):
    """Start interactive GRC Guardian session."""
    console.print(Panel("[bold green]GRC Guardian Interactive[/bold green]", subtitle="Type 'help' for commands, 'exit' to quit"))
    
    policy_context = load_policy(policy_file)
    if policy_context:
        console.print(f"[dim]Policy loaded: {policy_file} ({len(policy_context)} chars)[/dim]\n")
    
    while True:
        cmd = console.input("\n[bold blue]>[/bold blue] ").strip().lower()
        
        if cmd in ["exit", "quit", "q"]:
            console.print("[dim]Goodbye. Stay compliant.[/dim]")
            break
        
        elif cmd == "help":
            console.print("""
[bold]Commands:[/bold]
  compliance [framework]  - Check compliance (default: GDPR)
  risk [budget]           - Assess risks (default: low)
  audit [type]            - Run audit (default: general)
  gaps                    - Show policy gaps (if policy loaded)
  report                  - Generate quick report
  exit                    - Quit
            """)
        
        elif cmd.startswith("compliance"):
            parts = cmd.split()
            framework = parts[1].upper() if len(parts) > 1 else "GDPR"
            reg = json.loads(fetch_regulation(framework))
            console.print(f"\n[bold]{framework}:[/bold] {reg.get('non_profit_specific', 'N/A')[:100]}...")
            if policy_context:
                analysis = json.loads(analyse_policy(policy_context, framework))
                console.print(f"[bold]Your policy score:[/bold] {analysis['compliance_score']}/100")
        
        elif cmd.startswith("risk"):
            parts = cmd.split()
            budget = parts[1] if len(parts) > 1 else "low"
            risks = json.loads(get_risk_register("charity"))
            if policy_context:
                if "no encryption" in policy_context.lower():
                    risks.append({"id": "R-P01", "description": "Unencrypted devices", "likelihood": 4, "impact": 4})
            top = risks[0]
            score = json.loads(calculate_risk_score(top['likelihood'], top['impact']))
            console.print(f"\nTop risk: {top['description']} (Score: {score['score']})")
            mitigations = json.loads(suggest_mitigation(top['id'], score['level'], budget))
            console.print(f"Mitigation: {mitigations['suggestions'][0] if mitigations['suggestions'] else 'Consult board'}")
        
        elif cmd.startswith("audit"):
            reset_audit_chain()
            entry = json.loads(create_audit_entry("user", "interactive_check", "ok"))
            console.print(f"\nAudit entry: {entry['hash'][:16]}...")
        
        elif cmd == "gaps":
            if policy_context:
                analysis = json.loads(analyse_policy(policy_context, "GDPR"))
                console.print(f"\n[bold]Gaps found: {len(analysis['gaps_found'])}[/bold]")
                for gap in analysis['gaps_found']:
                    console.print(f"  • {gap}")
            else:
                console.print("\nNo policy loaded. Use --policy-file flag.")
        
        elif cmd == "report":
            if policy_context:
                analysis = json.loads(analyse_policy(policy_context, "GDPR"))
                console.print(f"\n[bold]Quick Report[/bold]")
                console.print(f"Compliance: {analysis['compliance_score']}/100")
                console.print(f"Gaps: {len(analysis['gaps_found'])}")
                console.print(f"Top action: {analysis['recommendations'][0] if analysis['recommendations'] else 'None'}")
            else:
                console.print("\nNo policy loaded. Use --policy-file flag.")
        
        else:
            console.print("Unknown command. Type 'help' for options.")


if __name__ == "__main__":
    cli()