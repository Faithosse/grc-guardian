# GRC Guardian

**Agents for Good | Kaggle 5-Day AI Agents Capstone**

> AI-powered Governance, Risk, and Compliance for non-profits with limited resources.

---

## Problem

Non-profits face identical regulatory pressures to corporations---GDPR, safeguarding, financial audit---yet **68% of small charities have no formal risk process**. Dedicated GRC staff are unaffordable.

## Solution

GRC Guardian is a multi-agent system using **Google ADK** that provides:

- **Compliance checks** against GDPR, NIST CSF, ISO 27001, Charity Commission rules
- **Risk assessment** with quantitative scoring and budget-constrained mitigations
- **Tamper-evident audit trails** with SHA-256 hashing for funder review

---

## Architecture

+-------------------------------------------------------------+
|                     GRC Guardian                            |
+-------------------------------------------------------------+
|                                                             |
|  +----------------+  +----------------+  +----------------+ |
|  |   Compliance   |  |     Risk       |  |     Audit      | |
|  |     Agent      |  |    Agent       |  |    Agent       | |
|  |  - GDPR        |  |  - Scoring     |  |  - SHA-256     | |
|  |  - NIST        |  |  - Mitigations |  |  - Integrity   | |
|  |  - Policies    |  |  - Register    |  |  - Schedule    | |
|  +--------+-------+  +--------+-------+  +--------+-------+ |
|           |                   |                   |          |
|           +-------------------+-------------------+          |
|                               |                             |
|                    +----------v----------+                  |
|                    |   Orchestrator      |                  |
|                    | (Intent + Synthesis)|                  |
|                    +----------+----------+                  |
|                               |                             |
|                    +----------v----------+                  |
|                    |    MCP Server       |                  |
|                    |  9 tools via stdio  |                  |
|                    +---------------------+                  |
|                                                             |
+-------------------------------------------------------------+
|
+---------v---------+
|  CLI / Skills     |
|  5 Click commands |
+-------------------+



---

## Key Concepts Demonstrated

| Concept | Where | Evidence |
|---------|-------|----------|
| **ADK Multi-Agent** | `agents/*.py` | 4 agents: Orchestrator, Compliance, Risk, Audit |
| **MCP Server** | `mcp_server/server.py` | 9 tools via stdio transport |
| **Antigravity** | `.antigravity/` | Agent manifest, skills, deploy config |
| **Security** | `agents/audit_agent.py` | SHA-256 tamper-evident trails |
| **Deployability** | `Dockerfile`, `health_server.py` | Container + K8s ready |
| **Agent Skills/CLI** | `cli/main.py` | 5 Click commands |

---

## Installation

### Step 1: Clone or Extract Project

```bash
cd grc-guardian

### Step 2: Create Virtual Environment
python -m venv venv 
---

### Step 3: Activate Virtual Environment
venv\Scripts\activate

### Step 4: Install Dependencies
pip install -r requirements.txt

### Step 5: Configure Environment
GOOGLE_API_KEY=your_google_api_key_here

### Project Structure
grc-guardian/
├── agents/                    # ADK Multi-Agent System
│   ├── __init__.py
│   ├── orchestrator.py        # Intent routing + synthesis
│   ├── compliance_agent.py    # GDPR, NIST, ISO checks
│   ├── risk_agent.py          # Risk scoring + mitigations
│   └── audit_agent.py         # SHA-256 audit trails
├── mcp_server/                # Model Context Protocol
│   ├── __init__.py
│   └── server.py              # 9 tools via stdio
├── cli/                       # Agent Skills / CLI
│   ├── __init__.py
│   └── main.py                # 5 Click commands
├── tests/                     # Unit tests
│   └── test_grc_guardian.py
├── sample_data/               # Example inputs
│   ├── sample_policy.md
│   └── sample_risk_register.json
├── demo.py                    # Interactive demonstration
├── fetch_policy.py            # Real-world policy fetcher
├── health_server.py           # Health check endpoint
├── mcp_config.json            # MCP server configuration
├── requirements.txt           # Dependencies
├── .env.example               # Config template
├── .gitignore
└── README.md                  # This file

### Running the Project
1. Run the Demo (All Agents)
bash
python demo.py
This runs all 4 demos sequentially:
Demo 1: Compliance Check (GDPR)
Demo 2: Risk Assessment (Charity, Low Budget)
Demo 3: Audit Trail (Financial)
Demo 4: MCP Server Tools Integration
2. Run the MCP Server (Separate Terminal)
bash
python mcp_server/server.py
The MCP server runs continuously and exposes 9 tools via stdio transport:
fetch_regulation
analyse_policy
calculate_risk_score
get_risk_register
create_audit_entry
verify_audit_integrity
generate_audit_schedule
suggest_mitigation
check_framework_alignment
3. Run the CLI / Agent Skills
bash
# Check compliance against a framework
python cli/main.py check-compliance -f GDPR -q "We collect donor emails"

# Assess risk for a charity with low budget
python cli/main.py assess-risk -t charity -b low

# Run an audit with scheduling
python cli/main.py run-audit -t financial --schedule

# Full assessment (compliance + risk + audit)
python cli/main.py full-assessment -t charity -o report.json

# Interactive mode
python cli/main.py interactive
4. Run the Health Check Server
bash
python health_server.py
Test the health endpoint:
bash
curl http://localhost:8080/health
5. Fetch a Real-World Policy
bash
python fetch_policy.py
This downloads St Elizabeth's data protection policy. Note: it saves as PDF but uses the local .txt copy for analysis.
6. Run the Tests
bash
python tests/test_grc_guardian.py
7. Test the MCP Client
bash
python test_mcp_client.py
This connects to the MCP server via stdio and tests all 9 tools end-to-end.

Sample Data Files
Table
File	Description
st_elizabeths_policy.txt	Real charity data protection policy (St Elizabeth's Centre)
their_policy.txt	Sample charity policy (Hope for Children) with known gaps
sample_policy.md	Example policy for testing
sample_risk_register.json	Pre-built risk register template

Docker Deployment

Build the Image
bash
docker build -t grc-guardian .

Run the Container
bash
docker run -p 8080:8080 --env-file .env grc-guardian
Docker Compose (Optional)
bash
docker-compose up
MCP Configuration
The mcp_config.json file configures two MCP servers:
GRC MCP Server --- local Python server with 9 GRC tools
Google Search --- live web search for current regulations
To use with Claude Desktop or other MCP clients, copy mcp_config.json to your MCP config directory.
Environment Variables
Table

Variable	Required	Description

GOOGLE_API_KEY	Yes	Google AI API key for ADK agents
MCP_LOG_LEVEL	No	MCP server log level (default: info)
PYTHONPATH	No	Set to . for local imports
PORT	No	Health server port (default: 8080)
Quick Start Commands
bash

# Full setup from scratch
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your GOOGLE_API_KEY

# Run everything
python demo.py                          # See all agents in action
python mcp_server/server.py             # Start MCP server (terminal 2)
python cli/main.py full-assessment -t charity -o report.json
python test_mcp_client.py             # Test all MCP tools
python health_server.py                 # Start health endpoint
Track
Agents for Good --- democratising GRC for resource-constrained non-profits.
License
MIT License
plain

---




