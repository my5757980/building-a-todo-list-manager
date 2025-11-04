# todo_app.py
# ToDo Master Pro – Organize Your Life!
# Streamlit + Pandas = Smart Task Manager

import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# Page Config
st.set_page_config(
    page_title="ToDo Master Pro",
    page_icon="Checkmark",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);}
    .stApp {background-color: #0f1621;}
    h1 {color: #ffd700 !important; text-align: center; font-family: 'Arial';}
    .stButton > button {background: #00ff88; color: black; font-weight: bold; border-radius: 12px;}
    .task-card {background: #1a1a2e; padding: 15px; border-radius: 12px; margin: 8px 0; border-left: 5px solid #00ff88;}
    .completed {background: #16213e; text-decoration: line-through; opacity: 0.6;}
    .high {border-left-color: #ff4d4d;}
    .medium {border-left-color: #ffaa00;}
    .low {border-left-color: #00d4ff;}
    .tag {background: #ffd93d; color: black; padding: 2px 8px; border-radius: 8px; font-size: 0.8em; margin-right: 5px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Checkmark ToDo Master Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>Add tasks. Set priority. Crush goals. Export reports.</p>", unsafe_allow_html=True)

# Session State
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# -----------------------------
# ADD TASK
# -----------------------------
with st.form("add_task", clear_on_submit=True):
    st.subheader("Add New Task")
    col1, col2 = st.columns(2)
    with col1:
        task_name = st.text_input("Task Name", placeholder="e.g., Finish report")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    with col2:
        due_date = st.date_input("Due Date", date.today())
        tags = st.text_input("Tags (comma separated)", placeholder="work, urgent")
    
    submitted = st.form_submit_button("Add Task")
    if submitted and task_name:
        st.session_state.tasks.append({
            'id': str(uuid.uuid4()),
            'name': task_name,
            'priority': priority,
            'due_date': due_date,
            'tags': [t.strip() for t in tags.split(",") if t.strip()],
            'completed': False,
            'created_at': datetime.now()
        })
        st.success("Task added!")
        st.rerun()

# -----------------------------
# TASK LIST
# -----------------------------
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    df['due_date'] = pd.to_datetime(df['due_date']).dt.date
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_priority = st.multiselect("Filter Priority", ["High", "Medium", "Low"], default=[])
    with col2:
        filter_status = st.multiselect("Status", ["Pending", "Completed"], default=["Pending"])
    with col3:
        search = st.text_input("Search Task")

    # Apply Filters
    filtered = df.copy()
    if filter_priority:
        filtered = filtered[filtered['priority'].isin(filter_priority)]
    if "Pending" in filter_status and "Completed" not in filter_status:
        filtered = filtered[~filtered['completed']]
    if "Completed" in filter_status and "Pending" not in filter_status:
        filtered = filtered[filtered['completed']]
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False)]

    # Sort
    filtered = filtered.sort_values(['completed', 'due_date', 'priority'], 
                                  ascending=[True, True, False])

    st.markdown(f"### Tasks ({len(filtered)})")
    
    for _, task in filtered.iterrows():
        priority_class = task['priority'].lower()
        completed_class = "completed" if task['completed'] else ""
        card_class = f"task-card {priority_class} {completed_class}"
        
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 2])
            with col1:
                if st.checkbox("Checkmark", value=task['completed'], key=f"check_{task['id']}"):
                    for t in st.session_state.tasks:
                        if t['id'] == task['id']:
                            t['completed'] = True
                    st.rerun()
            with col2:
                st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
                st.markdown(f"**{task['name']}**")
                st.markdown(f"Due: {task['due_date']} | Priority: **{task['priority']}**")
                if task['tags']:
                    tag_html = " ".join([f"<span class='tag'>{tag}</span>" for tag in task['tags']])
                    st.markdown(tag_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col3:
                if st.button("Delete", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(df))
    with col2:
        st.metric("Completed", len(df[df['completed']]))
    with col3:
        overdue = len(df[(df['due_date'] < date.today()) & (~df['completed'])])
        st.metric("Overdue", overdue)

    # Export
    csv = df.to_csv(index=False)
    st.download_button("Export CSV", csv, "todo_list.csv", "text/csv")

else:
    st.info("No tasks yet! Add one above to get started.")

# -----------------------------
# PREMIUM
# -----------------------------
st.markdown("---")
st.info("**Premium ($2.99/mo):** Cloud Sync, Email Reminders, Calendar View, PDF Reports, Mobile App!")
if st.button("Unlock Pro"):
    st.balloons()

st.caption("Built with Streamlit + uv | Master Your Day!")