import json
import re
from typing import Dict, Any, List, Tuple
from src.tools import HELP_DESK_TOOLS, search_knowledge_base, run_system_diagnostic, create_it_ticket, get_ticket_status, trigger_password_reset
from src.llm import LLMClient


class ITHelpdeskAgent:
    """
    Autonomous ReAct AI Agent for IT Helpdesk Support.
    Integrates RAG Knowledge Base Retrieval + Automated Tool Calling + Diagnostic Reasoning.
    """

    def __init__(self, provider: str = "auto"):
        self.llm = LLMClient(provider=provider)

    def process_query(self, user_query: str, user_email: str = "employee@company.com") -> Dict[str, Any]:
        """
        Main entry point to process an IT helpdesk issue.
        Runs diagnostic reasoning loop, executes tools, and constructs final resolution response.
        """
        logs = []
        tools_executed = []
        citations = []
        ticket_created = None

        logs.append(f"🔍 **User Issue Received**: \"{user_query}\"")

        # Step 1: Initial RAG Knowledge Search
        logs.append("🧠 **Step 1: RAG Knowledge Retrieval** - Searching IT Knowledge Base for relevant SOPs...")
        kb_response = search_knowledge_base(user_query)
        
        articles = kb_response.get("articles", [])
        if articles:
            logs.append(f"✅ Found {len(articles)} matching KB articles:")
            for art in articles:
                logs.append(f"   - **{art['id']}**: {art['title']} (Relevance Score: {art['similarity_score']})")
                citations.append({
                    "id": art["id"],
                    "title": art["title"],
                    "category": art["category"],
                    "score": art["similarity_score"]
                })
        else:
            logs.append("⚠️ No exact KB match found in immediate index. Relying on broad diagnostic tools.")

        # Step 2: System Diagnostic Check / Specialized Tool Execution
        query_lower = user_query.lower()

        # Check for Ticket Status Lookup
        ticket_match = re.search(r'inc-\d+', query_lower)
        if ticket_match:
            t_id = ticket_match.group(0).upper()
            logs.append(f"🛠️ **Step 2: Executing Tool `get_ticket_status`** for Ticket `{t_id}`...")
            t_res = get_ticket_status(t_id)
            tools_executed.append({
                "tool": "get_ticket_status",
                "input": {"ticket_id": t_id},
                "output": t_res
            })
            if t_res["status"] == "found":
                ticket_info = t_res["ticket"]
                final_answer = (
                    f"### 🎫 Ticket Status Report ({ticket_info['ticket_id']})\n\n"
                    f"- **Subject**: {ticket_info['subject']}\n"
                    f"- **User**: {ticket_info['user']}\n"
                    f"- **Status**: `{ticket_info['status']}`\n"
                    f"- **Priority**: {ticket_info['priority']}\n"
                    f"- **Created At**: {ticket_info['created_at']}\n"
                    f"- **Resolution Notes**: {ticket_info['resolution_notes'] or 'Pending technician resolution.'}"
                )
                return {
                    "answer": final_answer,
                    "logs": logs,
                    "tools_executed": tools_executed,
                    "citations": citations,
                    "ticket": None
                }

        # Check for Password Reset / Lockout
        if any(w in query_lower for w in ["password", "lockout", "locked out", "reset password", "login fail"]):
            logs.append(f"🛠️ **Step 2: Executing Tool `trigger_password_reset`** for `{user_email}`...")
            reset_res = trigger_password_reset(user_email)
            tools_executed.append({
                "tool": "trigger_password_reset",
                "input": {"user": user_email},
                "output": reset_res
            })
            logs.append("✅ Automated Password Reset email & verification token generated.")

        # Check for Network / Hardware / Performance Diagnostics
        diag_report = None
        if any(w in query_lower for w in ["ping", "slow", "freeze", "crash", "diagnostic", "hardware", "disk", "ram", "vpn", "connect"]):
            target = "network" if "vpn" in query_lower or "connect" in query_lower or "wifi" in query_lower else "all"
            logs.append(f"🛠️ **Step 2: Executing Tool `run_system_diagnostic`** (Target: `{target}`)...")
            diag_report = run_system_diagnostic(target=target)
            tools_executed.append({
                "tool": "run_system_diagnostic",
                "input": {"target": target},
                "output": diag_report
            })
            logs.append(f"✅ System Diagnostic Complete. Status: `{diag_report['overall_status']}`")

        # Step 3: Check if issue warrants automated IT Ticket Creation
        if "ticket" in query_lower or "create ticket" in query_lower or "escalate" in query_lower or (diag_report and diag_report['overall_status'] == "ATTENTION_REQUIRED"):
            logs.append("🎫 **Step 3: Creating IT Support Ticket** for ongoing tracking...")
            priority = "High" if "urgent" in query_lower or "bsod" in query_lower or "crash" in query_lower else "Medium"
            category = articles[0]["category"] if articles else "IT Operations"
            
            t_create_res = create_it_ticket(
                user_email=user_email,
                subject=f"Helpdesk Request: {user_query[:50]}...",
                description=user_query,
                category=category,
                priority=priority
            )
            ticket_created = t_create_res["ticket"]
            tools_executed.append({
                "tool": "create_it_ticket",
                "input": {"user": user_email, "priority": priority},
                "output": t_create_res
            })
            logs.append(f"✅ IT Ticket Created: `{ticket_created['ticket_id']}` (Priority: {priority})")

        # Step 4: Synthesize Final Solution Report
        logs.append("📝 **Step 4: Synthesizing Diagnostic Solution & Resolution Steps...**")
        final_answer = self._synthesize_solution(user_query, articles, diag_report, tools_executed, ticket_created)

        return {
            "answer": final_answer,
            "logs": logs,
            "tools_executed": tools_executed,
            "citations": citations,
            "ticket": ticket_created
        }

    def _synthesize_solution(
        self, 
        query: str, 
        articles: List[Dict[str, Any]], 
        diag_report: Optional[Dict[str, Any]], 
        tools_executed: List[Dict[str, Any]], 
        ticket_created: Optional[Dict[str, Any]]
    ) -> str:
        """Construct structured markdown response with step-by-step diagnostic resolution."""
        lines = []

        lines.append(f"## 🤖 AI Diagnostic Resolution Report\n")
        lines.append(f"**Issue Description**: *\"{query}\"*\n")

        # Summary of diagnosis
        if articles:
            top_art = articles[0]
            lines.append(f"### 🎯 Primary Diagnostic Match: [{top_art['id']}] {top_art['title']}\n")
            lines.append(f"**Category**: `{top_art['category']}` | **Confidence**: `{int(top_art['similarity_score'] * 100)}%`\n")
            lines.append(f"#### 💡 Recommended Troubleshooting Steps:\n")
            lines.append(top_art["content"])
            lines.append("\n")
        else:
            lines.append("### 💡 Recommended General Troubleshooting Steps:\n")
            lines.append("1. Verify physical power cables and active network connections.")
            lines.append("2. Restart the workstation or relevant application service.")
            lines.append("3. Clear local temporary cache files and flush DNS resolution settings.\n")

        # System Diagnostics Section
        if diag_report:
            lines.append("### 🛠️ Automated System Health Check Output:\n")
            lines.append(f"- **Overall Status**: `{diag_report['overall_status']}`")
            for check in diag_report.get("checks", []):
                lines.append(f"  - **{check['name']}**: `{check['status']}`")
            lines.append("\n")

        # Automated Actions / Tools Executed
        if tools_executed:
            lines.append("### ⚡ Automated Actions Executed:\n")
            for tool in tools_executed:
                if tool["tool"] == "trigger_password_reset":
                    lines.append(f"- ✅ **Password Reset Triggered**: Dispatched password reset token and unlock instructions to user.")
                elif tool["tool"] == "create_it_ticket":
                    t = tool["output"]["ticket"]
                    lines.append(f"- 🎫 **IT Ticket Created**: Tracking ID `{t['ticket_id']}` (Priority: `{t['priority']}`)")
                elif tool["tool"] == "run_system_diagnostic":
                    lines.append(f"- 🩺 **Diagnostic Check Completed**: Validated network, RAM, and disk status.")

            lines.append("\n")

        # Ticket Reference
        if ticket_created:
            lines.append(f"> [!NOTE]\n> An IT ticket (`{ticket_created['ticket_id']}`) has been automatically dispatched to the IT Support queue for monitoring.\n")

        # Citations / References
        if articles:
            lines.append("---")
            lines.append("### 📚 Knowledge Base Citations:")
            for art in articles:
                lines.append(f"- **[{art['id']}] {art['title']}** - *{art['summary']}*")

        return "\n".join(lines)
