import unittest
import os
import json
from src.rag_engine import RAGEngine
from src.tools import run_system_diagnostic, create_it_ticket, get_ticket_status, trigger_password_reset
from src.agent import ITHelpdeskAgent


class TestITHelpdeskAgent(unittest.TestCase):

    def test_rag_engine_search(self):
        rag = RAGEngine()
        results = rag.search("GlobalProtect VPN disconnect", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertTrue("VPN" in results[0]["title"] or "Network" in results[0]["category"])

    def test_system_diagnostic_tool(self):
        report = run_system_diagnostic(target="network")
        self.assertIn("overall_status", report)
        self.assertTrue(len(report["checks"]) > 0)

    def test_ticket_creation_and_status(self):
        t_res = create_it_ticket(
            user_email="test.user@company.com",
            subject="Test Unit Issue",
            description="Automated unit test ticket creation.",
            priority="Medium"
        )
        self.assertEqual(t_res["status"], "created")
        t_id = t_res["ticket_id"]

        status_res = get_ticket_status(t_id)
        self.assertEqual(status_res["status"], "found")
        self.assertEqual(status_res["ticket"]["user"], "test.user@company.com")

    def test_password_reset_tool(self):
        res = trigger_password_reset("alice@company.com")
        self.assertEqual(res["status"], "success")
        self.assertIn("alice@company.com", res["message"])

    def test_agent_end_to_end(self):
        agent = ITHelpdeskAgent()
        res = agent.process_query("My VPN is disconnecting frequently on Windows 11.")
        self.assertIn("answer", res)
        self.assertTrue(len(res["logs"]) > 0)
        self.assertTrue(len(res["citations"]) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
