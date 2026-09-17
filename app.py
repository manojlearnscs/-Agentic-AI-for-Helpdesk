import streamlit as st
import os
import json
import time
from src.agent import ITHelpdeskAgent
from src.rag_engine import RAGEngine
from src.tools import load_tickets, save_tickets, run_system_diagnostic, create_it_ticket

# Page Configuration
st.set_page_config(
    page_title="AI IT Helpdesk Agent",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .badge-open {
        background-color: #ffecb3;
        color: #b78103;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-inprogress {
        background-color: #bbdefb;
        color: #0d47a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-resolved {
        background-color: #c8e6c9;
        color: #1b5e20;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = ITHelpdeskAgent()
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Navigation
with st.sidebar:
    st.title("🖥️ IT Helpdesk Hub")
    st.markdown("**Use Case #4: AI IT Helpdesk Agent**")
    st.caption("Agent + RAG + Tool Execution Engine")
    
    st.divider()
    
    nav_selection = st.radio(
        "Navigation",
        ["💬 AI Diagnostic Chat", "📚 Knowledge Base Explorer", "🎫 IT Support Ticket Queue", "🩺 Diagnostic Sandbox"],
        index=0
    )
    
    st.divider()
    
    user_email_input = st.text_input("User Email", "john.doe@company.com")
    
    st.divider()
    st.info("💡 **Capabilities Enabled**:\n- RAG Vector Knowledge Base\n- Auto System Diagnostics\n- Password Reset Automation\n- Ticket Lifecycle Management")

# HEADER
st.markdown('<div class="main-header">🛠️ AI IT Helpdesk Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated technical issue diagnosis, knowledge retrieval, and troubleshooting agent</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: AI DIAGNOSTIC CHAT
# ---------------------------------------------------------
if nav_selection == "💬 AI Diagnostic Chat":
    st.subheader("💬 Ask the AI Helpdesk Agent")
    
    st.write("Click a sample issue below or type your technical problem:")
    col1, col2, col3, col4 = st.columns(4)
    
    sample_prompt = None
    if col1.button("🌐 VPN Connection Dropping"):
        sample_prompt = "My GlobalProtect VPN keeps disconnecting every few minutes on Windows 11."
    if col2.button("💻 Windows BSOD Crash"):
        sample_prompt = "My computer crashed with a blue screen error CRITICAL_PROCESS_DIED."
    if col3.button("🔑 Account Locked Out"):
        sample_prompt = "I entered the wrong password 3 times and my domain account is locked out."
    if col4.button("📧 Outlook Sync Issue"):
        sample_prompt = "Outlook is stuck on updating inbox and won't send or receive emails."

    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "logs" in message and message["logs"]:
                with st.expander("🔍 View Agent Execution Trace & Tools Used"):
                    for log_item in message["logs"]:
                        st.markdown(log_item)

    # Input Box
    prompt_input = st.chat_input("Describe your IT issue, error code, or ticket request...")
    query_to_process = sample_prompt or prompt_input

    if query_to_process:
        # User message
        st.session_state.chat_history.append({"role": "user", "content": query_to_process})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        # Agent processing
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent analyzing issue, querying RAG index, and running diagnostics..."):
                response_data = st.session_state.agent.process_query(
                    user_query=query_to_process, 
                    user_email=user_email_input
                )
                
                answer = response_data["answer"]
                logs = response_data["logs"]
                
                st.markdown(answer)
                
                with st.expander("🔍 View Agent Execution Trace & Tools Used", expanded=True):
                    for log_item in logs:
                        st.markdown(log_item)
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer,
                    "logs": logs
                })

# ---------------------------------------------------------
# TAB 2: KNOWLEDGE BASE EXPLORER
# ---------------------------------------------------------
elif nav_selection == "📚 Knowledge Base Explorer":
    st.subheader("📚 IT Knowledge Base & RAG Index")
    
    col_search, col_add = st.tabs(["🔍 Search & View Articles", "➕ Add New KB Article"])
    
    with col_search:
        search_query = st.text_input("Search Knowledge Base (Semantic RAG Search)", "")
        
        if search_query:
            results = st.session_state.rag.search(search_query, top_k=5)
            st.write(f"Found **{len(results)}** matching articles:")
            for art in results:
                with st.expander(f"[{art['id']}] {art['title']} (Score: {art.get('similarity_score', 'N/A')})"):
                    st.write(f"**Category**: {art['category']}")
                    st.write(f"**Tags**: {', '.join(art.get('tags', []))}")
                    st.write(f"**Summary**: {art['summary']}")
                    st.divider()
                    st.markdown(f"**Troubleshooting SOP**:\n{art['content']}")
        else:
            all_articles = st.session_state.rag.articles
            st.write(f"Showing all **{len(all_articles)}** indexed KB SOP articles:")
            for art in all_articles:
                with st.expander(f"[{art['id']}] {art['title']} — {art['category']}"):
                    st.write(f"**Summary**: {art['summary']}")
                    st.markdown(f"**Content**:\n{art['content']}")

    with col_add:
        st.write("Add a new Standard Operating Procedure (SOP) to the RAG vector index:")
        with st.form("add_kb_form"):
            new_title = st.text_input("Article Title")
            new_cat = st.selectbox("Category", ["Network & Security", "Hardware & OS", "Software & Apps", "Identity & Access Management", "System Diagnostics"])
            new_tags = st.text_input("Tags (comma separated)", "vpn, windows, software")
            new_summary = st.text_area("Summary")
            new_content = st.text_area("Full Troubleshooting Content / SOP Steps", height=150)
            
            submit_kb = st.form_submit_button("Publish KB Article")
            if submit_kb:
                if new_title and new_content:
                    tags_list = [t.strip() for t in new_tags.split(",") if t.strip()]
                    added = st.session_state.rag.add_article(
                        title=new_title,
                        category=new_cat,
                        tags=tags_list,
                        summary=new_summary,
                        content=new_content
                    )
                    st.success(f"Article `{added['id']}` published and re-indexed into RAG Engine successfully!")
                else:
                    st.error("Title and Content are required fields.")

# ---------------------------------------------------------
# TAB 3: IT SUPPORT TICKET QUEUE
# ---------------------------------------------------------
elif nav_selection == "🎫 IT Support Ticket Queue":
    st.subheader("🎫 IT Support Ticket Management Center")
    
    tickets = load_tickets()
    
    col_filter1, col_filter2 = st.columns(2)
    filter_status = col_filter1.selectbox("Filter Status", ["All", "Open", "In Progress", "Resolved"])
    filter_priority = col_filter2.selectbox("Filter Priority", ["All", "Critical", "High", "Medium", "Low"])
    
    filtered_tickets = tickets
    if filter_status != "All":
        filtered_tickets = [t for t in filtered_tickets if t["status"] == filter_status]
    if filter_priority != "All":
        filtered_tickets = [t for t in filtered_tickets if t["priority"] == filter_priority]

    st.write(f"Total Tickets: **{len(filtered_tickets)}**")
    
    for t in filtered_tickets:
        badge_class = "badge-open" if t["status"] == "Open" else ("badge-inprogress" if t["status"] == "In Progress" else "badge-resolved")
        
        with st.expander(f"{t['ticket_id']}: {t['subject']} — Priority: {t['priority']}"):
            st.markdown(f"**Status**: <span class='{badge_class}'>{t['status']}</span>", unsafe_allow_html=True)
            st.write(f"**User**: `{t['user']}` | **Category**: `{t['category']}`")
            st.write(f"**Created At**: {t['created_at']}")
            st.write(f"**Description**: {t['description']}")
            if t.get("resolution_notes"):
                st.info(f"**Resolution Notes**: {t['resolution_notes']}")
            
            # Status update controls
            c1, c2, c3 = st.columns([2, 3, 2])
            new_st = c1.selectbox("Update Status", ["Open", "In Progress", "Resolved"], key=f"st_{t['ticket_id']}")
            res_note = c2.text_input("Resolution Note", key=f"res_{t['ticket_id']}")
            if c3.button("Save Update", key=f"btn_{t['ticket_id']}"):
                for real_t in tickets:
                    if real_t["ticket_id"] == t["ticket_id"]:
                        real_t["status"] = new_st
                        if res_note:
                            real_t["resolution_notes"] = res_note
                save_tickets(tickets)
                st.success(f"Ticket {t['ticket_id']} updated!")
                st.rerun()

# ---------------------------------------------------------
# TAB 4: DIAGNOSTIC SANDBOX
# ---------------------------------------------------------
elif nav_selection == "🩺 Diagnostic Sandbox":
    st.subheader("🩺 On-Demand System Diagnostics Runner")
    st.write("Execute simulated diagnostic sweeps for immediate workstation health assessment:")
    
    diag_target = st.selectbox("Select Target Component", ["all", "network", "vpn", "disk", "memory", "hardware"])
    
    if st.button("🚀 Run Diagnostics Now"):
        with st.spinner("Executing diagnostic tests..."):
            time.sleep(0.8)
            report = run_system_diagnostic(target=diag_target)
            
            st.success(f"Diagnostic Completed! Overall Status: **{report['overall_status']}**")
            st.write(f"**Timestamp**: `{report['timestamp']}`")
            
            for check in report["checks"]:
                st.write(f"• **{check['name']}**: `{check['status']}`")
                st.json(check)
