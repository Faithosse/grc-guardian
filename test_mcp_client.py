#!/usr/bin/env python3
"""
GRC Guardian - MCP Client Test
Tests the MCP server by connecting via stdio and calling all 9 tools.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test all MCP tools."""
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=" * 60)
            print("MCP CLIENT TEST")
            print("GRC Guardian MCP Server")
            print("=" * 60)
            
            # 1. List tools
            tools = await session.list_tools()
            print(f"\n[1/9] Tools registered: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"  ✓ {tool.name}")
            
            # 2. Test fetch_regulation
            print("\n[2/9] Testing fetch_regulation...")
            result = await session.call_tool("fetch_regulation", {"regulation_name": "GDPR"})
            data = json.loads(result.content[0].text)
            print(f"  ✓ GDPR: {len(data['key_principles'])} principles found")
            
            # 3. Test analyse_policy
            print("\n[3/9] Testing analyse_policy...")
            result = await session.call_tool("analyse_policy", {
                "policy_text": "We collect data and keep it secure.",
                "framework": "GDPR"
            })
            data = json.loads(result.content[0].text)
            print(f"  ✓ Score: {data['compliance_score']}/100, Gaps: {len(data['gaps_found'])}")
            
            # 4. Test calculate_risk_score
            print("\n[4/9] Testing calculate_risk_score...")
            result = await session.call_tool("calculate_risk_score", {"likelihood": 4, "impact": 5})
            data = json.loads(result.content[0].text)
            print(f"  ✓ Score: {data['score']} ({data['level']})")
            
            # 5. Test get_risk_register
            print("\n[5/9] Testing get_risk_register...")
            result = await session.call_tool("get_risk_register", {"organisation_type": "charity"})
            data = json.loads(result.content[0].text)
            print(f"  ✓ {len(data)} risks for charity")
            
            # 6. Test create_audit_entry
            print("\n[6/9] Testing create_audit_entry...")
            result = await session.call_tool("create_audit_entry", {
                "actor": "test_user",
                "action": "test_action",
                "result": "success"
            })
            data = json.loads(result.content[0].text)
            print(f"  ✓ Hash: {data['hash'][:20]}...")
            
            # 7. Test verify_audit_integrity
            print("\n[7/9] Testing verify_audit_integrity...")
            result = await session.call_tool("verify_audit_integrity", {"log_entries": [data]})
            data = json.loads(result.content[0].text)
            print(f"  ✓ Integrity: {data['integrity_status']}")
            
            # 8. Test generate_audit_schedule
            print("\n[8/9] Testing generate_audit_schedule...")
            result = await session.call_tool("generate_audit_schedule", {
                "audit_type": "financial",
                "frequency": "annual"
            })
            data = json.loads(result.content[0].text)
            print(f"  ✓ Next audit: {data['next_audit'][:10]}")
            
            # 9. Test suggest_mitigation
            print("\n[9/9] Testing suggest_mitigation...")
            result = await session.call_tool("suggest_mitigation", {
                "risk_id": "R-C01",
                "risk_level": "High",
                "budget_constraint": "low"
            })
            data = json.loads(result.content[0].text)
            print(f"  ✓ Suggestions: {len(data['suggestions'])}")
            
            # 10. Test check_framework_alignment
            print("\n[10/9] Testing check_framework_alignment...")
            result = await session.call_tool("check_framework_alignment", {
                "current_frameworks": ["ISO27001"],
                "target_framework": "NIST_CSF"
            })
            data = json.loads(result.content[0].text)
            print(f"  ✓ Alignment: {data['alignment']}")
            
            print("\n" + "=" * 60)
            print("ALL MCP TOOLS TESTED SUCCESSFULLY")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())