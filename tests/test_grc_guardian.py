"""
GRC Guardian - Test Suite
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.compliance_agent import fetch_regulation, analyse_policy, check_framework_alignment
from agents.risk_agent import calculate_risk_score, get_risk_register, suggest_mitigation
from agents.audit_agent import create_audit_entry, verify_audit_integrity, generate_audit_schedule, reset_audit_chain
from agents.orchestrator import route_to_compliance, route_to_risk, route_to_audit, synthesise_outputs


class TestCompliance(unittest.TestCase):
    def test_fetch_gdpr(self):
        result = json.loads(fetch_regulation("GDPR"))
        self.assertIn("key_principles", result)
        self.assertEqual(len(result["key_principles"]), 8)

    def test_fetch_unknown(self):
        result = json.loads(fetch_regulation("UNKNOWN"))
        self.assertIn("error", result)

    def test_analyse_policy_gdpr(self):
        policy = "We collect data."
        result = json.loads(analyse_policy(policy, "GDPR"))
        self.assertTrue(len(result["gaps_found"]) > 0)
        self.assertTrue(result["compliance_score"] < 100)

    def test_framework_alignment(self):
        result = json.loads(check_framework_alignment(["ISO27001"], "NIST_CSF"))
        self.assertEqual(result["alignment"], "High")


class TestRisk(unittest.TestCase):
    def test_score_low(self):
        result = json.loads(calculate_risk_score(1, 1))
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["level"], "Low")

    def test_score_critical(self):
        result = json.loads(calculate_risk_score(5, 5))
        self.assertEqual(result["score"], 25)
        self.assertEqual(result["level"], "Critical")

    def test_risk_register_charity(self):
        result = json.loads(get_risk_register("charity"))
        self.assertEqual(len(result), 5)

    def test_mitigation_zero_budget(self):
        result = json.loads(suggest_mitigation("R-C01", "High", "zero"))
        for suggestion in result["suggestions"]:
            self.assertIn("free", suggestion.lower())

    def test_all_risk_levels(self):
        test_cases = [(1, 1, "Low"), (2, 2, "Low"), (3, 2, "Medium"), (3, 3, "Medium"), (4, 3, "High"), (5, 4, "Critical")]
        for likelihood, impact, expected in test_cases:
            result = json.loads(calculate_risk_score(likelihood, impact))
            self.assertEqual(result["level"], expected)


class TestAudit(unittest.TestCase):
    def test_create_entry(self):
        result = json.loads(create_audit_entry("test", "action", "result"))
        self.assertIn("timestamp", result)
        self.assertIn("hash", result)
        self.assertEqual(len(result["hash"]), 64)

    def test_verify_integrity_pass(self):
        reset_audit_chain()
        entries = [
            json.loads(create_audit_entry("a", "b", "c")),
            json.loads(create_audit_entry("d", "e", "f")),
        ]
        result = json.loads(verify_audit_integrity(json.dumps(entries)))
        self.assertEqual(result["integrity_status"], "PASS")

    def test_verify_integrity_fail(self):
        entry = json.loads(create_audit_entry("a", "b", "c"))
        entry["result"] = "tampered"
        result = json.loads(verify_audit_integrity(json.dumps([entry])))
        self.assertEqual(result["integrity_status"], "FAIL")

    def test_schedule_generation(self):
        result = json.loads(generate_audit_schedule("financial", "annual"))
        self.assertEqual(len(result["schedule"]), 4)


class TestOrchestrator(unittest.TestCase):
    def test_route_compliance(self):
        result = json.loads(route_to_compliance("GDPR question"))
        self.assertEqual(result["agent"], "compliance")

    def test_route_risk(self):
        result = json.loads(route_to_risk("Risk question"))
        self.assertEqual(result["agent"], "risk")

    def test_route_audit(self):
        result = json.loads(route_to_audit("Audit question"))
        self.assertEqual(result["agent"], "audit")

    def test_synthesis(self):
        result = json.loads(synthesise_outputs("{}", "{}", "{}"))
        self.assertIn("actions", result)
        self.assertEqual(result["confidence"], "High")


class TestSecurity(unittest.TestCase):
    def test_no_hardcoded_secrets(self):
        import re
        patterns = [
            r'api[_-]?key\s*=\s*["\']\\w+',
            r'password\s*=\s*["\']\\w+',
            r'secret\s*=\s*["\']\\w+',
        ]
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root_dir, dirs, files in os.walk(root):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        self.assertEqual(len(matches), 0, f"Potential secret in {filepath}")


if __name__ == "__main__":
    unittest.main(verbosity=2)