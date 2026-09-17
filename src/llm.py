import os
import json
import re
from typing import Dict, Any, List, Optional

class LLMClient:
    """
    Flexible LLM Provider wrapper supporting OpenAI, Gemini, or Smart Local Fallback.
    Works offline or online out-of-the-box.
    """

    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if provider == "auto":
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            elif os.getenv("GEMINI_API_KEY"):
                self.provider = "gemini"
            else:
                self.provider = "local"
        else:
            self.provider = provider

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response given prompt and system instruction."""
        if self.provider == "openai" and self.api_key:
            try:
                import urllib.request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                body = json.dumps({
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }).encode('utf-8')
                req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body, headers=headers)
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"OpenAI API call failed: {e}. Falling back to local engine.")

        # Local Smart Fallback Engine
        return self._local_fallback(prompt, system_prompt)

    def _local_fallback(self, prompt: str, system_prompt: str) -> str:
        """
        Smart offline response generator that mimics ReAct reasoning & tool execution.
        """
        prompt_lower = prompt.lower()

        # Rule 1: Ticket status lookup request
        ticket_match = re.search(r'inc-\d+', prompt_lower)
        if ticket_match:
            t_id = ticket_match.group(0).upper()
            return f"Action: get_ticket_status\nAction Input: {{\x22ticket_id\x22: \x22{t_id}\x22}}"

        # Rule 2: Account lockout / Password reset
        if any(w in prompt_lower for w in ["password", "lockout", "locked out", "reset password", "login failure"]):
            # Extract possible email or username
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', prompt)
            user_id = email_match.group(0) if email_match else "user@company.com"
            return f"Action: trigger_password_reset\nAction Input: {{\x22username_or_email\x22: \x22{user_id}\x22}}"

        # Rule 3: Diagnostic request
        if any(w in prompt_lower for w in ["ping", "slow", "freeze", "crash", "diagnostic", "hardware", "disk", "ram"]):
            target = "all"
            if "network" in prompt_lower or "vpn" in prompt_lower:
                target = "network"
            elif "disk" in prompt_lower:
                target = "disk"
            elif "ram" in prompt_lower or "memory" in prompt_lower:
                target = "memory"
            return f"Action: run_system_diagnostic\nAction Input: {{\x22target\x22: \x22{target}\x22}}"

        # Default RAG Search tool invocation
        query_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', prompt).strip()
        return f"Action: search_knowledge_base\nAction Input: {{\x22query\x22: \x22{query_cleaned}\x22}}"
