import http.server
import socketserver
import json
import os
import urllib.parse
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import ITHelpdeskAgent
from src.rag_engine import RAGEngine
from src.tools import load_tickets, save_tickets, run_system_diagnostic

PORT = 8000
agent = ITHelpdeskAgent()
rag = RAGEngine()

class ITDeskHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html_content = self.get_index_html()
            self.wfile.write(html_content.encode("utf-8"))
            return
            
        elif parsed_path.path == "/api/kb":
            self.send_json_response(rag.articles)
            return

        elif parsed_path.path == "/api/tickets":
            tickets = load_tickets()
            self.send_json_response(tickets)
            return

        super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        if parsed_path.path == "/api/chat":
            user_query = data.get("query", "")
            user_email = data.get("email", "john.doe@company.com")
            
            result = agent.process_query(user_query=user_query, user_email=user_email)
            self.send_json_response(result)
            return

        elif parsed_path.path == "/api/diagnostic":
            target = data.get("target", "all")
            report = run_system_diagnostic(target=target)
            self.send_json_response(report)
            return

        elif parsed_path.path == "/api/update_ticket":
            t_id = data.get("ticket_id")
            new_status = data.get("status")
            notes = data.get("notes", "")
            
            tickets = load_tickets()
            updated = False
            for t in tickets:
                if t["ticket_id"] == t_id:
                    t["status"] = new_status
                    if notes:
                        t["resolution_notes"] = notes
                    updated = True
            if updated:
                save_tickets(tickets)
                self.send_json_response({"status": "success", "message": f"Ticket {t_id} updated."})
            else:
                self.send_json_response({"status": "error", "message": "Ticket not found."})
            return

        self.send_error(404, "Endpoint Not Found")

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def get_index_html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI IT Helpdesk Agent</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar-brand { font-weight: 700; color: #0d6efd !important; }
        .chat-box { height: 420px; overflow-y: auto; background: #ffffff; border-radius: 8px; border: 1px solid #dee2e6; padding: 15px; }
        .msg-user { background: #e3f2fd; color: #0d47a1; border-radius: 12px; padding: 10px 15px; margin-bottom: 10px; max-width: 80%; align-self: flex-end; }
        .msg-agent { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; max-width: 90%; }
        .trace-card { background: #1e1e1e; color: #4af626; font-family: monospace; font-size: 0.85rem; padding: 10px; border-radius: 6px; margin-top: 8px; }
        .card-custom { border-radius: 10px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .badge-open { background: #fff3cd; color: #664d03; }
        .badge-inprogress { background: #cff4fc; color: #055160; }
        .badge-resolved { background: #d1e7dd; color: #0f5132; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid px-4">
            <a class="navbar-brand" href="#"><i class="bi bi-display me-2"></i>AI IT Helpdesk Agent</a>
            <span class="navbar-text text-light small">Use Case #4 (Agent + RAG + Tools)</span>
        </div>
    </nav>

    <div class="container-fluid px-4 my-4">
        <ul class="nav nav-pills mb-4" id="mainTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="chat-tab" data-bs-toggle="pill" data-bs-target="#chat-pane"><i class="bi bi-chat-dots me-1"></i> AI Diagnostic Chat</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="kb-tab" data-bs-toggle="pill" data-bs-target="#kb-pane" onclick="loadKB()"><i class="bi bi-book me-1"></i> Knowledge Base Explorer</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="tickets-tab" data-bs-toggle="pill" data-bs-target="#tickets-pane" onclick="loadTickets()"><i class="bi bi-ticket-perforated me-1"></i> IT Support Tickets</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="diag-tab" data-bs-toggle="pill" data-bs-target="#diag-pane"><i class="bi bi-activity me-1"></i> System Diagnostics</button>
            </li>
        </ul>

        <div class="tab-content" id="tabContent">
            <!-- TAB 1: CHAT -->
            <div class="tab-pane fade show active" id="chat-pane">
                <div class="row">
                    <div class="col-md-9">
                        <div class="card card-custom p-3">
                            <h5 class="card-title text-primary"><i class="bi bi-robot me-2"></i>Interactive AI IT Assistant</h5>
                            <div class="chat-box d-flex flex-column" id="chatBox">
                                <div class="msg-agent">
                                    <strong>AI Agent:</strong> Hello! Describe your IT issue, error code, or account request below.
                                </div>
                            </div>
                            <div class="input-group mt-3">
                                <input type="text" id="queryInput" class="form-control" placeholder="e.g. My VPN keeps disconnecting on Windows 11..." onkeypress="if(event.key==='Enter') sendQuery()">
                                <button class="btn btn-primary" onclick="sendQuery()"><i class="bi bi-send-fill"></i> Send</button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-custom p-3">
                            <h6>Sample Scenarios</h6>
                            <button class="btn btn-outline-primary btn-sm text-start mb-2" onclick="setQuery('My GlobalProtect VPN keeps disconnecting every few minutes.')">VPN Dropping</button>
                            <button class="btn btn-outline-danger btn-sm text-start mb-2" onclick="setQuery('My laptop crashed with blue screen CRITICAL_PROCESS_DIED.')">Windows BSOD</button>
                            <button class="btn btn-outline-warning btn-sm text-start mb-2" onclick="setQuery('Account locked out after 3 wrong passwords.')">Password Reset</button>
                            <button class="btn btn-outline-info btn-sm text-start" onclick="setQuery('Outlook stuck on updating inbox.')">Outlook Sync</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: KB -->
            <div class="tab-pane fade" id="kb-pane">
                <div class="card card-custom p-4">
                    <h5>IT Knowledge Base Articles & SOPs</h5>
                    <div id="kbList" class="mt-3">Loading KB data...</div>
                </div>
            </div>

            <!-- TAB 3: TICKETS -->
            <div class="tab-pane fade" id="tickets-pane">
                <div class="card card-custom p-4">
                    <h5>Active IT Support Tickets</h5>
                    <div id="ticketList" class="mt-3">Loading tickets...</div>
                </div>
            </div>

            <!-- TAB 4: DIAGNOSTIC -->
            <div class="tab-pane fade" id="diag-pane">
                <div class="card card-custom p-4">
                    <h5>System Diagnostic Sandbox</h5>
                    <div class="row g-3 align-items-center mb-3">
                        <div class="col-auto">
                            <select id="diagTarget" class="form-select">
                                <option value="all">All Components</option>
                                <option value="network">Network & VPN</option>
                                <option value="disk">Disk Storage</option>
                                <option value="memory">RAM Memory</option>
                            </select>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-success" onclick="runDiagnostic()"><i class="bi bi-play-circle me-1"></i> Run Diagnostic Test</button>
                        </div>
                    </div>
                    <div id="diagResult"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function setQuery(text) {
            document.getElementById('queryInput').value = text;
            sendQuery();
        }

        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            if (!query) return;

            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `<div class="msg-user"><strong>You:</strong> ${query}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chatBox.innerHTML += `<div class="msg-agent" id="${loadingId}"><em>Analyzing issue & running diagnostics...</em></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, email: 'user@company.com'})
                });
                const data = await res.json();
                
                document.getElementById(loadingId).remove();

                let logsHtml = '<div class="trace-card"><strong>Execution Trace:</strong><br>';
                data.logs.forEach(l => logsHtml += `• ${l}<br>`);
                logsHtml += '</div>';

                chatBox.innerHTML += `<div class="msg-agent"><strong>AI Agent:</strong><br>${data.answer.replace(/\\n/g, '<br>')}${logsHtml}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                document.getElementById(loadingId).innerHTML = 'Error processing request.';
            }
        }

        async function loadKB() {
            const res = await fetch('/api/kb');
            const articles = await res.json();
            let html = '';
            articles.forEach(a => {
                html += `<div class="card mb-3 p-3">
                    <h6>[${a.id}] ${a.title} <span class="badge bg-secondary">${a.category}</span></h6>
                    <p class="text-muted small mb-1"><strong>Tags:</strong> ${a.tags.join(', ')}</p>
                    <p class="mb-2">${a.summary}</p>
                    <pre class="bg-light p-2 rounded small">${a.content}</pre>
                </div>`;
            });
            document.getElementById('kbList').innerHTML = html;
        }

        async function loadTickets() {
            const res = await fetch('/api/tickets');
            const tickets = await res.json();
            let html = '';
            tickets.forEach(t => {
                const badgeClass = t.status === 'Open' ? 'badge-open' : (t.status === 'In Progress' ? 'badge-inprogress' : 'badge-resolved');
                html += `<div class="card mb-3 p-3">
                    <div class="d-flex justify-content-between">
                        <h6>${t.ticket_id}: ${t.subject}</h6>
                        <span class="badge ${badgeClass}">${t.status}</span>
                    </div>
                    <p class="mb-1"><strong>User:</strong> ${t.user} | <strong>Priority:</strong> ${t.priority} | <strong>Category:</strong> ${t.category}</p>
                    <p class="mb-1">${t.description}</p>
                    ${t.resolution_notes ? `<div class="alert alert-info py-1 px-2 small">Notes: ${t.resolution_notes}</div>` : ''}
                </div>`;
            });
            document.getElementById('ticketList').innerHTML = html;
        }

        async function runDiagnostic() {
            const target = document.getElementById('diagTarget').value;
            const res = await fetch('/api/diagnostic', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target})
            });
            const data = await res.json();
            let html = `<div class="alert alert-success">Overall Status: <strong>${data.overall_status}</strong> (Timestamp: ${data.timestamp})</div><ul>`;
            data.checks.forEach(c => {
                html += `<li><strong>${c.name}:</strong> <code>${c.status}</code></li>`;
            });
            html += '</ul>';
            document.getElementById('diagResult').innerHTML = html;
        }
    </script>
</body>
</html>"""

def run_server():
    with socketserver.TCPServer(("", PORT), ITDeskHTTPRequestHandler) as httpd:
        print(f"=======================================================")
        print(f"Native Web Server Running on http://localhost:{PORT}")
        print(f"=======================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
