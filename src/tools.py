import json
import os
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.rag_engine import RAGEngine

# Shared RAG instance
rag_engine = RAGEngine()

TICKETS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tickets.json")


def load_tickets() -> List[Dict[str, Any]]:
    """Load tickets from JSON storage."""
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_tickets(tickets: List[Dict[str, Any]]) -> bool:
    """Save tickets to JSON storage."""
    try:
        os.makedirs(os.path.dirname(TICKETS_FILE), exist_ok=True)
        with open(TICKETS_FILE, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving tickets: {e}")
        return False


# --- TOOL IMPLEMENTATIONS ---

def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    Tool: Search IT Knowledge Base for SOPs, troubleshooting guides, and policies.
    """
    results = rag_engine.search(query=query, top_k=3)
    if not results:
        return {
            "status": "not_found",
            "message": f"No specific KB articles found for query: '{query}'",
            "articles": []
        }
    return {
        "status": "success",
        "count": len(results),
        "articles": results
    }


def run_system_diagnostic(target: str = "network") -> Dict[str, Any]:
    """
    Tool: Run diagnostic checks on system hardware, network adapter, DNS, disk, or memory.
    `target` can be: 'network', 'disk', 'memory', 'vpn', or 'all'.
    """
    target = target.lower().strip()
    
    diagnostic_report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target": target,
        "checks": []
    }

    if target in ["network", "vpn", "all"]:
        # Ping check
        ping_latency = random.randint(12, 45)
        dns_status = "PASS" if random.random() > 0.1 else "FAIL (DNS resolution timeout)"
        gateway_ping = "PASS (192.168.1.1)"
        
        diagnostic_report["checks"].append({
            "name": "Gateway Ping Test",
            "status": gateway_ping,
            "latency_ms": ping_latency
        })
        diagnostic_report["checks"].append({
            "name": "DNS Lookup Test (corporate.domain)",
            "status": dns_status,
            "detail": "Subnet DNS adapter response"
        })

    if target in ["disk", "hardware", "all"]:
        free_space_gb = round(random.uniform(15.5, 120.0), 1)
        disk_health = "HEALTHY" if free_space_gb > 20 else "WARNING (Low Disk Space)"
        diagnostic_report["checks"].append({
            "name": "System Disk Storage (C:)",
            "status": disk_health,
            "free_space_gb": free_space_gb
        })

    if target in ["memory", "hardware", "all"]:
        ram_usage_pct = random.randint(45, 92)
        ram_status = "NORMAL" if ram_usage_pct < 85 else "HIGH (Potential memory leak detected)"
        diagnostic_report["checks"].append({
            "name": "Physical RAM Usage",
            "status": ram_status,
            "usage_percentage": f"{ram_usage_pct}%"
        })

    overall_status = "PASS" if all("PASS" in c["status"] or "NORMAL" in c["status"] or "HEALTHY" in c["status"] for c in diagnostic_report["checks"]) else "ATTENTION_REQUIRED"
    diagnostic_report["overall_status"] = overall_status
    
    return diagnostic_report


def create_it_ticket(user_email: str, subject: str, description: str, category: str = "General IT", priority: str = "Medium") -> Dict[str, Any]:
    """
    Tool: Create a new IT Support Ticket in the ticketing database.
    """
    tickets = load_tickets()
    ticket_count = len(tickets) + 1001
    ticket_id = f"INC-{ticket_count}"

    new_ticket = {
        "ticket_id": ticket_id,
        "user": user_email,
        "subject": subject,
        "category": category,
        "priority": priority,
        "status": "Open",
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_notes": ""
    }

    tickets.append(new_ticket)
    save_tickets(tickets)

    return {
        "status": "created",
        "ticket_id": ticket_id,
        "ticket": new_ticket
    }


def get_ticket_status(ticket_id: str) -> Dict[str, Any]:
    """
    Tool: Query status and details of an existing IT ticket by Ticket ID (e.g. INC-1001).
    """
    tickets = load_tickets()
    ticket_id = ticket_id.upper().strip()
    
    for ticket in tickets:
        if ticket["ticket_id"] == ticket_id:
            return {
                "status": "found",
                "ticket": ticket
            }

    return {
        "status": "not_found",
        "message": f"Ticket ID '{ticket_id}' was not found in the database."
    }


def trigger_password_reset(username_or_email: str) -> Dict[str, Any]:
    """
    Tool: Initiate automated account unlock / password reset email for a user.
    """
    reset_token = f"RST-{random.randint(100000, 999999)}"
    return {
        "status": "success",
        "user": username_or_email,
        "action": "Password Reset Link Triggered",
        "message": f"A self-service password reset link and MFA verification code (Token: {reset_token}) have been dispatched to {username_or_email}'s registered secondary email and mobile authenticator app.",
        "expires_in_minutes": 15
    }


# Map of available tools for agent invocation
HELP_DESK_TOOLS = {
    "search_knowledge_base": {
        "func": search_knowledge_base,
        "description": "Searches the IT Knowledge Base for troubleshooting articles, SOPs, and error code fixes.",
        "parameters": {"query": "string"}
    },
    "run_system_diagnostic": {
        "func": run_system_diagnostic,
        "description": "Runs automated system health diagnostics on network, VPN, disk, memory, or all components.",
        "parameters": {"target": "string (network/disk/memory/vpn/all)"}
    },
    "create_it_ticket": {
        "func": create_it_ticket,
        "description": "Creates an official IT support ticket for unresolved issues or hardware requests.",
        "parameters": {
            "user_email": "string",
            "subject": "string",
            "description": "string",
            "category": "string",
            "priority": "string (Low/Medium/High/Critical)"
        }
    },
    "get_ticket_status": {
        "func": get_ticket_status,
        "description": "Fetches the current status and notes of an IT support ticket using ticket ID (e.g. INC-1001).",
        "parameters": {"ticket_id": "string"}
    },
    "trigger_password_reset": {
        "func": trigger_password_reset,
        "description": "Initiates an automated password reset and account unlock link for locked-out users.",
        "parameters": {"username_or_email": "string"}
    }
}
