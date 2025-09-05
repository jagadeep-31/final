import streamlit as st
import xmlrpc.client
import re
from datetime import date
# ---------- CONFIG ----------
st.set_page_config(layout="wide", page_title="SBA Sprint Planning Assistant", page_icon=":clipboard:")
st.markdown("""
    <style>
        .section-header { color: #0263e0; font-weight: 650; }
        .star-rating-table td { text-align: center; }
    </style>
    """, unsafe_allow_html=True)
header_col1, header_col2 = st.columns([1,7])
with header_col1:
    st.image("sba logo.jpg", width=110)
with header_col2:
    st.markdown(
        "<h1 style='margin-bottom: 0.1em;'>SBA Sprint Planning Assistant</h1>"
        "<div style='color:#0263e0;font-weight:500;font-size:1.09em;margin-bottom: 25px;'>Automate The Mundane</div>",
        unsafe_allow_html=True
    )
# ------------------ CONSTANTS --------------------
ODOO_URL = "https://sba-info-solutions-pvt-ltd.odoo.com"
ODOO_DB = "sba-info-solutions-pvt-ltd"
PARENT_ARTICLE_NAME = "Weekly Sprint & Performance Tracker (2025-W26-Jul 7:11)"
CATEGORY_OPTIONS = ["R&D", "Client Projects", "Internal development"]
ASSIGNEES = {
    "Jagadeep": "jagadeep.k@sbainfo.in",
    "Sri Hari": "srihari.k@sbainfo.in",
    "Hari": "hari.r@sbainfo.in",
    "Ajith Kumar": "ajithkumar.r@sbainfo.in",
    "Nithiyanandham": "nithiyanandham.r@sbainfo.in"
}
KANBAN_EXAMPLES = {
    "Software Development": {"desc": "", "stages": ["Backlog", "Specification", "Development", "Tests", "Delivered"]},
    "Agile Scrum": {"desc": "", "stages": ["Backlog", "Sprint Backlog", "Sprint in progress", "Sprint Complete", "Old Completed Sprint"]},
    "Digital Marketing": {"desc": "", "stages": ["Ideas", "Researching", "Writing", "Editing", "Done"]},
    "Customer Feedback": {"desc": "", "stages": ["New", "In Development", "Done", "Refused"]},
    "Consulting": {"desc": "", "stages": ["New Projects", "Resources Allocation", "In Progress", "Done"]},
    "Research Project": {"desc": "", "stages": ["Brainstorm", "Research", "Draft", "Final Document"]},
    "Website Redesign": {"desc": "", "stages": ["Page Ideas", "Copywriting", "Design", "live"]},
    "T-shirt Printing": {"desc": "", "stages": ["New orders", "Logo Design", "To print", "Done"]},
    "Design": {"desc": "", "stages": ["New request", "Design", "Client Review", "handoff"]},
    "Publishing": {"desc": "", "stages": ["Ideas", "Writing", "Editing", "published"]},
    "Manufacturing": {"desc": "", "stages": ["New Orders", "Material Sourcing", "manufacturing", "Assembling", "Delivered"]},
    "Podcast and video production": {"desc": "", "stages": ["Research", "Script", "Recording", "Mixing", "Published"]},
}
MEMBER_NAMES = ["Srihari", "Hari R", "Ajith", "Jagadeep", "Nithiyanandham", "Sadeesh", "Venkatesh"]
# ---------------- TEMPLATES ------------------
TASK_DESCRIPTION_TEMPLATE = """**User Story:**
As a [user role], I want to [goal] so that I can [benefit].
**System Story:**
As an engineer, I need to [technical goal] so that [technical outcome].
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
**Sub-goals / Tasks:**
- [ ] Sub-task 1
- [ ] Sub-task 2
"""
PERFORMANCE_TEMPLATE = """ 
<div style="font-family: Arial, sans-serif;">
<h1 style="color:#0263e0;margin-bottom:0;">Weekly Sprint Performance Tracker</h1>
<div style="color:#444; font-size:1.29em; margin-bottom:35px; font-weight:500;">
  ({date_title})
</div>
<h2 style="color:#0263e0; margin:32px 0 16px 0;">Part A: Weekly Sprint Plan</h2>
<table border="1" cellpadding="12" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom:32px;">
  <tr style="background:#f7fafe;">
    <th style="width:250px; border:1px solid #222;">Field</th>
    <th style="border:1px solid #222;">Details</th>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;"><b>Sprint Number</b></td>
    <td style="border:1px solid #aaa;">{sprint_no}</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;"><b>Sprint Dates</b></td>
    <td style="border:1px solid #aaa;">{date_range}</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;"><b>Team Name</b></td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;"><b>Sprint Goal</b></td>
    <td style="border:1px solid #aaa;">
      <ul style="margin:0; padding-left:22px;">
        <li><b>Goal 1:</b> <span style="color:gray;">Describe key objective & owner</span></li>
        <li><b>Goal 2:</b> <span style="color:gray;">Describe key objective & owner</span></li>
        <li><b>Goal 3:</b> <span style="color:gray;">Describe key objective & owner</span></li>
      </ul>
    </td>
  </tr>
</table>
<div style="height:32px;"></div>
<h2 style="color:#0263e0; margin:32px 0 16px 0;">Part B: Task Board & Work Split</h2>
<table border="1" cellpadding="12" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom:32px;">
  <tr style="background:#eaf3fb;">
    <th style="border:1px solid #222;">Task ID</th>
    <th style="border:1px solid #222;">Task Name & Description</th>
    <th style="border:1px solid #222;">Project / Theme</th>
    <th style="border:1px solid #222;">Assigned To</th>
    <th style="border:1px solid #222;">Priority</th>
    <th style="border:1px solid #222;">Est. Points</th>
    <th style="border:1px solid #222;">Status</th>
  </tr>
  <tr><td style="border:1px solid #aaa;">T-01</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-02</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-03</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-04</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-05</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-06</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-07</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
  <tr><td style="border:1px solid #aaa;">T-08</td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;"></td><td style="border:1px solid #aaa;">To Do</td></tr>
</table>
<div style="height:32px;"></div>
<h2 style="color:#0263e0; margin:32px 0 16px 0;">Part C: Daily Developer Progress Notes</h2>
<table border="1" cellpadding="12" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom:32px;">
  <tr style="background:#fdf7ec;">
    <th style="border:1px solid #222;">Day</th>
    <th style="border:1px solid #222;">Developer Name</th>
    <th style="border:1px solid #222;">Today's Accomplishments</th>
    <th style="border:1px solid #222;">Blockers / Issues</th>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Monday</td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1. ajith<br>2. jagadeep <br>3. Nithiyanandham<br>4. Srihari<br>5. Hari<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Tuesday</td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1. ajith<br>2. jagadeep <br>3. Nithiyanandham<br>4. Srihari<br>5. Hari<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Wednesday</td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1. ajith<br>2. jagadeep <br>3. Nithiyanandham<br>4. Srihari<br>5. Hari<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Thursday</td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1. ajith<br>2. jagadeep <br>3. Nithiyanandham<br>4. Srihari<br>5. Hari<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Friday</td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1. ajith<br>2. jagadeep <br>3. Nithiyanandham<br>4. Srihari<br>5. Hari<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.<br></td>
    <td style="border:1px solid #aaa; vertical-align: top; padding: 12px;">1.<br>2.<br>3.<br>4.<br>5.</td>
  </tr>
</table>
<div style="height:32px;"></div>
<h2 style="color:#0263e0; margin:32px 0 16px 0;">Part D: Friday Weekly Summary Report</h2>
<table border="1" cellpadding="12" cellspacing="0" style="border-collapse:collapse; width:100%; margin-bottom:32px;">
  <tr style="background:#f8e9f6;">
    <th style="border:1px solid #222;">Section</th>
    <th style="border:1px solid #222;">Summary</th>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Executive Summary</td>
    <td style="border:1px solid #aaa;"> Success Summary<br><br>Partially Summary</td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Sprint Goal Outcome</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Completed Work</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Incomplete Work</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Not Started Work</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Key Challenges</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Goals for Next Week</td>
    <td style="border:1px solid #aaa;"></td>
  </tr>
</table>
<div style="height:32px;"></div>
<h2 style="color:#0263e0; margin:32px 0 16px 0;">Part E: Performance & Recognition</h2>
<table border="1" cellpadding="12" cellspacing="0" style="border-collapse:collapse; width:100%;">
  <tr style="background:#e9f3ec;">
    <th style="border:1px solid #222;">Metric</th>
    <th style="border:1px solid #222;">Details</th>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Team Velocity</td>
    <td style="border:1px solid #aaa;">
      Committed Effort: <br>
      Completed Effort: <br>
      Partially Completed: <br>
      Velocity %: <br>
      Total Priority Completed Points: <br>
    </td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Performance of the Week</td>
    <td style="border:1px solid #aaa;">
      Name:Developer Name  <br>
      Reason for Recognition: Specific Contribution or Achievement
    </td>
  </tr>
  <tr>
    <td style="border:1px solid #aaa;">Key Learnings & Action Items</td>
    <td style="border:1px solid #aaa;">
      What went well: <br><br>
      Tech: <br><br>
      What can be improved: <br><br>
      Action items for next sprint:
    </td>
  </tr>
</table>
</div>
"""
SPRINT_DIFFICULTY_TABLE = """
<table border="1" cellpadding="14" cellspacing="0" style="border-collapse:collapse; width:88%; margin:18px 0 20px 0; font-size:1.23em;">
  <thead style="background:#f7f7f7;">
    <tr>
      <th style="width:60%; text-align:left; padding:15px 10px;">Change</th>
      <th style="width:40%; text-align:center; padding:15px 10px;">Complexity</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:20px 18px;">Change 1</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
    <tr><td style="padding:20px 18px;">Change 2</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
    <tr><td style="padding:20px 18px;">Change 3</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
    <tr><td style="padding:20px 18px;">Change 4</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
    <tr><td style="padding:20px 18px;">Change 5</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
    <tr><td style="padding:20px 18px;">Change 6</td><td style="text-align:center; font-size:2em; color:#ccc;">☆☆☆☆☆</td></tr>
  </tbody>
</table>
"""
def build_final_retro_html():
    questions = [
        "On a scale of 1 to 5, how do you feel about your role in the company?",
        "On the same scale, how do you feel about the company as a whole?",
        "Why do you feel that way?",
        "What's one thing that would make you happier during the next Sprint?"
    ]
    html = "<div style='margin-top:30px; margin-bottom:15px; font-size:1.1em;'><b>Final Retrospective (Are we happy doing all this?)</b><ol style='margin-left:20px;'>"
    for q in questions:
        html += f"<li style='margin-bottom:8px;'>{q}</li>"
    html += "</ol></div>"
    for member in MEMBER_NAMES:
        html += f"<div style='margin-top:20px;'><b>{member}</b></div><ul style='margin-left: 30px; margin-bottom: 20px;'>"
        for i in range(1,5):
            html += f"<li style='min-height:25px;'><b>{i}.</b> &nbsp;</li>"
        html += "</ul>"
    return html
SPRINT_TEMPLATE = """
<div style='font-family: Arial, sans-serif; line-height: 1.75; padding-bottom:20px;'>
  <h1 style='color: #C03; font-size:2.15em; font-weight: bold;'>✍️ Sprint Review & Retrospective</h1>
  <div style='font-size:1.18em; margin-bottom: 25px; color:#444;'>
    <b>Date:</b> {date} &nbsp; <b>Sprint Number:</b> {sprint_num}
  </div>
  <div>
    <h3 style="margin-top:26px;">📝 Learnings – How can we ship faster, & produce world class solutions</h3>
    <p style="color:#222; margin-top:0; margin-bottom:0;">
      Explain in a few words, the key insights we learned during the sprint (technical, collaboration, efficiency, all aspects)
    </p>
    <ul style="margin-top:5px; padding-left:32px;">
      <li style="min-height:28px"></li>
      <li style="min-height:28px"></li>
      <li style="min-height:28px"></li>
    </ul>
    <h3 style="margin-top:40px;">🧠 Kaizen (Improvements to adopt)</h3>
    <p style="color:#222; margin-top:0;">
      List here all the changes to implement in next sprint.<br>
      <span style="font-size:0.97em; color:#888;">(Take inspiration from learnings above)</span>
    </p>
    <ul style="margin:2px 0 0 0; padding-left:32px;">
      <li style="min-height:28px"></li>
      <li style="min-height:28px"></li>
      <li style="min-height:28px"></li>
    </ul>
    <h3 style="margin-top:40px;">⚙ Difficulty of changes</h3>
    <div style="margin-bottom:6px; font-size:1.01em; color:#444;">
      Scrum master or Delivery head to fill this before launching next sprint.
    </div>
    {difficulty_table}
    <h3 style="margin-top:40px;">❓ Open Questions & Comments</h3>
    <div style="padding-top:2px; color:#555; font-size:1.05em;">
      <div style="margin-bottom:8px;">Lay here any remaining question or comments you wanna add</div>
      <ul style="margin-top:0; padding-left:32px;">
        <li style="min-height:23px"></li>
        <li style="min-height:23px"></li>
      </ul>
    </div>
    <div style="margin-top:45px;">{final_retro_html}</div>
    <div style="margin-top:15px; color:#888; font-style:italic;">User Review and their feedbacks</div>
  </div>
</div>
"""
def ensure_stages_for_project(uid, models, project_id, stages):
    existing_stages = models.execute_kw(
        ODOO_DB, uid, st.session_state['odoo_pass'],
        'project.task.type', 'search_read',
        [[['project_ids', 'in', [project_id]]]],
        {'fields': ['id', 'name'], 'order': 'sequence ASC'}
    )
    existing_names = {s['name'] for s in existing_stages}
    for stage_name in stages:
        if stage_name not in existing_names:
            global_stage = models.execute_kw(
                ODOO_DB, uid, st.session_state['odoo_pass'],
                'project.task.type', 'search', [[['name', '=', stage_name], ['project_ids', '=', False]]]
            )
            if global_stage:
                models.execute_kw(
                    ODOO_DB, uid, st.session_state['odoo_pass'],
                    'project.task.type', 'write', [[global_stage[0]], {'project_ids': [(4, project_id)]}]
                )
            else:
                models.execute_kw(
                    ODOO_DB, uid, st.session_state['odoo_pass'],
                    'project.task.type', 'create',
                    [{'name': stage_name, 'project_ids': [(4, project_id)]}]
                )
def odoo_connect():
    login = st.session_state.get("odoo_login")
    pw = st.session_state.get("odoo_pass")
    if not login or not pw:
        st.stop()
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    uid = common.authenticate(ODOO_DB, login, pw, {})
    if not uid:
        st.error("❌ Invalid credentials. Please try again.")
        st.stop()
    st.session_state["login_success"] = True
    return uid, models
# ------------------ APP WORKFLOW STARTS HERE ---------------------
st.markdown("<h3 class='section-header'>🔐 Login to Odoo</h3>", unsafe_allow_html=True)
st.text_input("Odoo Username or Email (login)", key="odoo_login")
st.text_input("Odoo Password", type="password", key="odoo_pass")
if st.session_state.get("odoo_login") and st.session_state.get("odoo_pass"):
    uid, models = odoo_connect()
    st.success(f"✅ Login successful! Welcome, {st.session_state['odoo_login']}")
    st.markdown("<h3 class='section-header'>📈 Create Weekly Sprint Performance Tracker Article</h3>", unsafe_allow_html=True)
    with st.form("create_perf_tracker_form"):
        perf_sprint_no = st.text_input("Sprint Number (e.g., W29)", value=f"W{date.today().isocalendar()[1]}")
        perf_date_range = st.text_input("Sprint Dates (e.g., Jul28:Aug1)", value="")
        perf_article_name = st.text_input("Article Title", value=f"Weekly Sprint Performance Tracker (2025-{perf_sprint_no}-{perf_date_range})")
        perf_submitted = st.form_submit_button("Create Weekly Tracker")
    parent_id_list = models.execute_kw(
        ODOO_DB, uid, st.session_state["odoo_pass"],
        'knowledge.article', 'search',
        [[['name', '=', PARENT_ARTICLE_NAME]]]
    )
    if perf_submitted:
        if parent_id_list:
            parent_id = parent_id_list[0]
            existing = models.execute_kw(
                ODOO_DB, uid, st.session_state["odoo_pass"],
                'knowledge.article', 'search',
                [[['name', '=', perf_article_name], ['parent_id', '=', parent_id]]]
            )
            if existing:
                st.warning(f"Weekly Performance Tracker '{perf_article_name}' already exists under the parent.")
            else:
                perf_content = PERFORMANCE_TEMPLATE.format(
                    sprint_no=perf_sprint_no, 
                    date_range=perf_date_range, 
                    date_title=f"2025-{perf_sprint_no}-{perf_date_range}"
                )
                try:
                    created_id = models.execute_kw(
                        ODOO_DB, uid, st.session_state["odoo_pass"],
                        'knowledge.article', 'create',
                        [{'name': perf_article_name, 'body': perf_content, 'parent_id': parent_id}]
                    )
                    st.success(f"Created tracker '{perf_article_name}' under '{PARENT_ARTICLE_NAME}' (id: {created_id})")
                except Exception as e:
                    st.error(f"Failed to create tracker: {e}")
        else:
            st.error(f"Parent Knowledge Article '{PARENT_ARTICLE_NAME}' not found! Please create it in Odoo.")
    st.markdown("<h3 class='section-header'>🚀 Create Sprint Review & Retrospective Article</h3>", unsafe_allow_html=True)
    with st.form("create_sprint_review_form"):
        sprint_date = st.date_input("Sprint Date", value=date.today())
        sprint_num = st.text_input("Sprint Number", value="01")
        sprint_article_name = st.text_input("Sprint Review Article Title",
                                            value=f"✍️Sprint Review & Retrospective ({sprint_date.isoformat()}) [#{sprint_num}]")
        submitted_sprint = st.form_submit_button("Create Sprint Review Template")
    if submitted_sprint:
        if parent_id_list:
            parent_id = parent_id_list[0]
            existing = models.execute_kw(
                ODOO_DB, uid, st.session_state["odoo_pass"],
                'knowledge.article', 'search',
                [[['name', '=', sprint_article_name], ['parent_id', '=', parent_id]]]
            )
            if existing:
                st.warning(f"Sprint Review '{sprint_article_name}' already exists under the parent.")
            else:
                final_retro_html = build_final_retro_html()
                content = SPRINT_TEMPLATE.format(
                    date=sprint_date.isoformat(),
                    sprint_num=sprint_num,
                    difficulty_table=SPRINT_DIFFICULTY_TABLE,
                    final_retro_html=final_retro_html
                )
                article_vals = {
                    "name": sprint_article_name,
                    "body": content,
                    "parent_id": parent_id
                }
                try:
                    article_id = models.execute_kw(
                        ODOO_DB, uid, st.session_state["odoo_pass"],
                        'knowledge.article', 'create', [article_vals]
                    )
                    st.success(f"Successfully created Sprint Review & Retrospective under '{PARENT_ARTICLE_NAME}' (id: {article_id})")
                except Exception as e:
                    st.error(f"Error creating the sprint review article: {e}")
        else:
            st.error(f"Parent Knowledge Article '{PARENT_ARTICLE_NAME}' not found! Please create it in Odoo.")
    # ---- Fetch projects for project/task management ----
    project_list = models.execute_kw(
        ODOO_DB, uid, st.session_state["odoo_pass"],
        "project.project", "search_read",
        [],
        {"fields": ["id", "name"]}
    )
    project_options = {proj["name"]: proj["id"] for proj in project_list}
    # ---- Kanban Example Selector ----
    st.markdown("## Kanban Examples")
    kanban_options = list(KANBAN_EXAMPLES.keys())
    selected_kanban = st.radio("Choose a Kanban Example", kanban_options, horizontal=True)
    kanban_example = KANBAN_EXAMPLES[selected_kanban]
    # ---- Project Creator ----
    st.markdown('<h3 class="section-header">Create New Project</h3>', unsafe_allow_html=True)
    with st.expander("Project Details", expanded=True):
        proj_name = st.text_input("Project Name")
        proj_category = st.selectbox("Project Kanban Column", CATEGORY_OPTIONS)
        proj_desc = st.text_area("Overall Project Description")
        if st.button("Create Project"):
            description_html = re.sub(r'**(.+?)**', r'<b>\1</b>', proj_desc).replace('\n', '<br>')
            stage_ids = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.project.stage', 'search', [[['name', '=', proj_category]]])
            project_vals = {'name': proj_name, 'active': True, 'description': description_html}
            if stage_ids:
                project_vals['stage_id'] = stage_ids[0]
            project_id = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.project', 'create', [project_vals])
            ensure_stages_for_project(uid, models, project_id, kanban_example["stages"])
            st.session_state.update({'project_id': project_id, 'project_name': proj_name,
                                     'kanban_stages': kanban_example["stages"], 'selected_kanban': selected_kanban})
            st.success(f"Project '{proj_name}' created with Kanban '{selected_kanban}'.")
    # ---- Add Task to Existing Project (with Subtasks)----
    st.markdown("<h3 class='section-header'>Add Task to Existing Project</h3>", unsafe_allow_html=True)
    with st.expander("Select Project to Add Task", expanded=True):
        sel_project_name = st.selectbox("Select Existing Project", list(project_options.keys()))
        sel_project_id = project_options[sel_project_name]
        sel_project_stages = models.execute_kw(
            ODOO_DB, uid, st.session_state['odoo_pass'],
            'project.task.type', 'search_read',
            [[['project_ids', 'in', [sel_project_id]]]],
            {'fields': ['id', 'name'], 'order': 'sequence ASC'}
        )
        sel_stages_names = [stage["name"] for stage in sel_project_stages] if sel_project_stages else kanban_example["stages"]
        with st.form("add_task_existing_project"):
            task_title = st.text_input("Task Title", key="task_title_existing")
            task_desc = st.text_area("Task Description", key="task_desc_existing", height=250, value=TASK_DESCRIPTION_TEMPLATE)
            subtasks_text = st.text_area("Subtasks (one per line, optional)", key="subtasks_existing", help="Enter one subtask per line")
            tags = st.text_input("Tags (comma-separated)", key="task_tags_existing")
            assignees_selected = st.multiselect("Assign Task To", list(ASSIGNEES.keys()), key="task_assignees_existing")
            kanban_stage = st.selectbox("Select Stage / Column", sel_stages_names, key="task_stage_existing")
            submitted_existing = st.form_submit_button("Add Task to Existing Project")
            
            if submitted_existing:
                tag_ids = []
                for tag in tags.split(","):
                    tag = tag.strip()
                    if tag:
                        tag_id = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.tags', 'search', [[['name', '=', tag]]])
                        if not tag_id:
                            tag_id = [models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.tags', 'create', [{'name': tag}])]
                        tag_ids.append(tag_id[0])
                user_ids = [models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'res.users', 'search', [[['login', '=', ASSIGNEES[name]]]])[0]
                            for name in assignees_selected if name in ASSIGNEES]
                project_stages = sel_project_stages
                stage_id = next((stage['id'] for stage in project_stages if stage['name'] == kanban_stage), None)
                task_vals = {
                    "name": task_title,
                    "project_id": sel_project_id,
                    "description": re.sub(r'**(.+?)**', r'<b>\1</b>', task_desc).replace('\n', '<br>'),
                    "tag_ids": [(6, 0, tag_ids)] if tag_ids else [],
                    "user_ids": [(6, 0, user_ids)] if user_ids else [],
                }
                if stage_id:
                    task_vals["stage_id"] = stage_id
                task_id = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.task', 'create', [task_vals])
                
                subtask_lines = [line.strip() for line in subtasks_text.split("\n") if line.strip()]
                for subtask_line in subtask_lines:
                    subtask_vals = {
                        "name": subtask_line,
                        "project_id": sel_project_id,
                        "parent_id": task_id,
                        "stage_id": stage_id if stage_id else False,
                        "user_ids": [(6, 0, user_ids)] if user_ids else [],  # --- ASSIGNEE FIX ---
                    }
                    models.execute_kw(
                        ODOO_DB, uid, st.session_state['odoo_pass'],
                        'project.task', 'create', [subtask_vals]
                    )
                
                st.success(f"Task '{task_title}' created in project '{sel_project_name}' with {len(subtask_lines)} subtasks.")
                st.rerun()
    # ---- Add Tasks to Current/Newly Created Project (with Subtasks) ----
    if 'project_id' in st.session_state:
        st.markdown(f'<h3 class="section-header">Add Tasks to Project: {st.session_state["project_name"]}</h3>', unsafe_allow_html=True)
        stages_for_project = st.session_state.get('kanban_stages', [])
        
        with st.form("task_form"):
            task_title = st.text_input("Task Title", key="task_title_newproj")
            task_desc = st.text_area("Task Description", key="task_desc_newproj", height=250, value=TASK_DESCRIPTION_TEMPLATE)
            subtasks_text_new = st.text_area("Subtasks (one per line, optional)", key="subtasks_new", help="Enter one subtask per line")
            tags = st.text_input("Tags (comma-separated)", key="task_tags_newproj")
            assignees_selected = st.multiselect("Assign Task To", list(ASSIGNEES.keys()), key="task_assignees_newproj")
            kanban_stage = st.selectbox("Select Stage / Column", stages_for_project, key="task_stage_newproj")
            submitted_new = st.form_submit_button("Add Task")
            
            if submitted_new:
                tag_ids = []
                for tag in tags.split(","):
                    tag = tag.strip()
                    if tag:
                        tag_id = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.tags', 'search', [[['name', '=', tag]]])
                        if not tag_id:
                            tag_id = [models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.tags', 'create', [{'name': tag}])]
                        tag_ids.append(tag_id[0])
                user_ids = [models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'res.users', 'search', [[['login', '=', ASSIGNEES[name]]]])[0]
                            for name in assignees_selected if name in ASSIGNEES]
                project_stages_data = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.task.type',
                                                   'search_read',
                                                   [[['project_ids', 'in', [st.session_state['project_id']]]]],
                                                   {'fields': ['id', 'name']})
                stage_id = next((stage['id'] for stage in project_stages_data if stage['name'] == kanban_stage), None)
                task_vals = {
                    "name": task_title,
                    "project_id": st.session_state['project_id'],
                    "description": re.sub(r'**(.+?)**', r'<b>\1</b>', task_desc).replace('\n', '<br>'),
                    "tag_ids": [(6, 0, tag_ids)] if tag_ids else [],
                    "user_ids": [(6, 0, user_ids)] if user_ids else [],
                }
                if stage_id:
                    task_vals["stage_id"] = stage_id
                task_id = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.task', 'create', [task_vals])
                
                subtask_lines = [line.strip() for line in subtasks_text_new.split("\n") if line.strip()]
                for subtask_line in subtask_lines:
                    subtask_vals = {
                        "name": subtask_line,
                        "project_id": st.session_state['project_id'],
                        "parent_id": task_id,
                        "stage_id": stage_id if stage_id else False,
                        "user_ids": [(6, 0, user_ids)] if user_ids else [],  # --- ASSIGNEE FIX ---
                    }
                    models.execute_kw(
                        ODOO_DB, uid, st.session_state['odoo_pass'],
                        'project.task', 'create', [subtask_vals]
                    )
                
                st.success(f"Task '{task_title}' created in stage '{kanban_stage}' with {len(subtask_lines)} subtasks.")
                st.rerun()
                
        st.markdown("### Tasks by Kanban Stage")
        tasks = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.task', 'search_read',
                                  [[['project_id', '=', st.session_state['project_id']]]],
                                  {'fields': ['id', 'name', 'stage_id', 'parent_id']})
        project_stages_display = models.execute_kw(ODOO_DB, uid, st.session_state['odoo_pass'], 'project.task.type', 'search_read',
                                           [[['project_ids', 'in', [st.session_state['project_id']]]]],
                                           {'fields': ['id', 'name']})
        stage_id_name = {stage['id']: stage['name'] for stage in project_stages_display}
        columns = st.columns(len(stages_for_project))
        for idx, stage_name in enumerate(stages_for_project):
            with columns[idx]:
                st.markdown(f"#### {stage_name}")
                for task in tasks:
                    task_stage_id = task.get('stage_id')
                    task_stage_name = stage_id_name.get(task_stage_id[0] if isinstance(task_stage_id, list) else task_stage_id,
                                                        '') if task_stage_id else ''
                    if task_stage_name == stage_name and not task.get('parent_id'):
                        st.markdown(f"- {task['name']}")
