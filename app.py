import os
import io
import time
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from interviewer import Interviewer
from adaptive import compute_confidence_score, pick_next_question
from scoring import deep_evaluate
from voice import tts_speak, stt_from_file
from reporter import generate_pdf_report
from db import init_db, save_interview, save_answer, list_interviews
from db import get_answers, get_interview, export_interviews_to_excel
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="AI Interview Agent", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS for 3D effects and responsive design
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main container with 3D background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem;
    }
    
    /* 3D Card Effect */
    .stCard, [data-testid="stCard"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3),
                    0 0 0 1px rgba(255, 255, 255, 0.1);
        transform-style: preserve-3d;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stCard:hover, [data-testid="stCard"]:hover {
        transform: translateY(-10px) rotateX(5deg);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.3);
    }
    
    /* 3D Button Effects */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform-style: preserve-3d;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02);
    }
    
    .stButton > button::before:hover {
        left: 100%;
    }
    
    /* 3D Title */
    h1 {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        transform: perspective(1000px) rotateX(10deg);
        letter-spacing: -1px;
    }
    
    h2, h3 {
        color: #333;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    /* Sidebar 3D Effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 247, 250, 0.98) 100%);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.3);
        border-right: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    /* Progress bars with 3D effect */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    /* Text areas with 3D effect */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1),
                    inset 0 2px 5px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3),
                    inset 0 2px 5px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
    /* Selectbox 3D effect */
    .stSelectbox > div > div {
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric cards with 3D effect */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Chat messages with 3D cards */
    .stMarkdown {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.8);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }
    
    .stMarkdown:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Responsive Design */
    @media (max-width: 1024px) {
        .main {
            padding: 1.5rem;
        }
        
        h1 {
            font-size: 2.5rem;
        }
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        .main {
            padding: 1rem;
        }
        
        .stCard, [data-testid="stCard"] {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 15px;
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        .stButton > button {
            padding: 0.6rem 1.5rem;
            font-size: 0.95rem;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem;
        }
        
        h2 {
            font-size: 1.3rem;
        }
        
        h3 {
            font-size: 1.1rem;
        }
        
        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            width: 100%;
        }
        
        .main {
            padding: 0.5rem;
        }
        
        .stCard, [data-testid="stCard"] {
            padding: 0.75rem;
        }
    }
    
    /* Tablet specific */
    @media (min-width: 481px) and (max-width: 768px) {
        .stButton > button {
            padding: 0.65rem 1.75rem;
        }
    }
    
    /* Animation for page load */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main > div {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Info boxes with 3D effect */
    .stInfo {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Warning boxes */
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.2);
    }
    
    /* Spinner with 3D effect */
    .stSpinner > div {
        border: 4px solid rgba(102, 126, 234, 0.2);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* File uploader with 3D effect */
    .stFileUploader {
        border-radius: 15px;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Plotly charts container */
    .js-plotly-plot {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        overflow: hidden;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

def main():
    # Main title with enhanced styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🎤 AI Interview Agent</h1>
        <p style="font-size: 1.2rem; color: #666; margin-top: 0;">Intelligent Interviewing Platform</p>
    </div>
    """, unsafe_allow_html=True)

    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "interview_id" not in st.session_state:
        st.session_state.interview_id = None

    roles = [
        "Software Engineer",
        "Data Scientist",
        "DevOps Engineer",
        "Product Manager",
        "Frontend Engineer",
    ]

    personas = ["Friendly", "Strict", "HR-style", "Technical lead", "Behavioral", "Academic"]

    difficulty_levels = ["Beginner", "Intermediate", "Expert"]

    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #000000; font-weight: 700; text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem;">⚙️ Interview Setup</h2>
        </div>
        """, unsafe_allow_html=True)
        role = st.selectbox("Select job role", roles)
        persona = st.selectbox("Interviewer persona", personas)
        difficulty = st.selectbox("Starting difficulty", difficulty_levels, index=1)
        voice_mode = st.checkbox("Enable voice mode (TTS/STT)")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if st.session_state.agent is None:
        # Read API key from environment only to avoid exposing it in the UI
        initial_key = os.getenv("OPENAI_API_KEY", None)
        st.session_state.agent = Interviewer(api_key=initial_key, model=model)

    init_db()

    # Simple page router
    if st.session_state.get("page") == "dashboard":
        # Render HR Activity Dashboard
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">📊 HR Activity Dashboard</h1>
            <p style="font-size: 1.2rem; color: #666;">Manage and analyze all interviews</p>
        </div>
        """, unsafe_allow_html=True)
        ints = list_interviews()
        if not ints:
            st.info("No interviews recorded yet.")
        if st.button("🔙 Back to Interview", use_container_width=True, key="back_to_interview_1"):
            st.session_state.page = None
            st.rerun()
            return

        df = pd.DataFrame(ints)
        st.markdown("#### 📋 All Interviews")
        st.dataframe(df[["id", "role", "persona", "total_score"]], use_container_width=True)

        sel = st.selectbox("🔍 Select interview to inspect", options=[i["id"] for i in ints])
        if sel:
            it = get_interview(sel)
            st.markdown(f"### 📝 Interview {sel} - {it.get('role')} ({it.get('persona')})")
            answers = get_answers(sel)
            for idx, a in enumerate(answers, 1):
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 15px;
                            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); margin: 1rem 0;">
                    <h4 style="color: #667eea;">❓ Question {idx}</h4>
                    <p style="font-size: 1.1rem; margin-bottom: 1rem;">{a['question']}</p>
                    <h4 style="color: #764ba2;">💬 Answer</h4>
                    <p>{a['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
                meta = a.get('metadata', {})
                ev = meta.get('eval') if isinstance(meta, dict) else None
                if ev:
                    with st.expander(f"📊 Evaluation Details for Question {idx}"):
                        st.write(ev)

            # Generate a lightweight report from DB
            if st.button("📄 Generate PDF Report", use_container_width=True):
                # Build report structure similar to interviewer.end_interview output
                total = 0.0
                breakdown_acc = {"relevance": 0.0, "technical_depth": 0.0, "clarity": 0.0, "structure": 0.0}
                items = []
                for a in answers:
                    ev = a.get('metadata', {}).get('eval', {})
                    score = ev.get('score', 0) if isinstance(ev, dict) else 0
                    total += score
                    bd = ev.get('breakdown', {}) if isinstance(ev, dict) else {}
                    for k in breakdown_acc:
                        breakdown_acc[k] += bd.get(k, 0)
                    items.append({"question": a['question'], "answer": a['answer'], "evaluation": ev})
                count = max(1, len(answers))
                avg = total / count
                breakdown_avg = {k: (v / count) for k, v in breakdown_acc.items()}
                decision = "Hire" if avg >= 75 else ("Consider" if avg >= 50 else "Reject")
                report = {"role": it.get('role'), "total_score": avg, "breakdown_avg": breakdown_avg, "decision": decision, "items": items}
                pdf_path = generate_pdf_report(report, out_path=f"interview_{sel}_report.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", data=f, file_name=f"interview_{sel}_report.pdf", mime="application/pdf")

        # Export all interviews to excel
        if st.button("📊 Export all interviews to Excel", use_container_width=True):
            excel_path = export_interviews_to_excel()
            with open(excel_path, "rb") as ef:
                st.download_button("Download Excel", data=ef, file_name=excel_path, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.markdown("---")
        st.markdown("### 📈 Compare Candidates")
        sel_multi = st.multiselect("Select interviews to compare", options=[i["id"] for i in ints])
        if sel_multi:
            comp = [get_interview(i) for i in sel_multi]
            comp_df = pd.DataFrame(comp)
            fig = px.bar(comp_df, x="id", y="total_score", color="role", title="Candidate comparison by total score")
            st.plotly_chart(fig, use_container_width=True)

        if st.button("🔙 Back to Interview", use_container_width=True):
            st.session_state.page = None
            st.rerun()
        return

    # Action buttons with enhanced styling
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🚀 Start Interview", use_container_width=True):
            st.session_state.agent.start_interview(role)
            st.session_state.interview_started_at = time.time()
            st.session_state.asked_questions = [st.session_state.agent.history[-1]["text"]] if st.session_state.agent.history else []
            st.session_state.metrics = {"confidence": 60, "missed_topics": []}
            st.session_state.persona = persona
            # create a DB entry placeholder
            st.session_state.interview_id = save_interview(role, persona, 0.0)
            st.rerun()
    with col2:
        if st.button("⏹️ End Interview", use_container_width=True):
            report = st.session_state.agent.end_interview()
            st.session_state.report = report
            st.rerun()
    with col3:
        if st.button("📊 Open HR Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("---")

    if not st.session_state.agent.in_progress:
        st.info("👆 Press 'Start Interview' to begin your AI-powered interview experience!")
        return

    chat_col, input_col = st.columns([2, 1])

    with chat_col:
        st.markdown("### 💬 Conversation")
        # Create a scrollable container for chat
        chat_container = st.container()
        with chat_container:
            for i, item in enumerate(st.session_state.agent.history):
                role_tag = "Interviewer" if item["from"] == "system" else "Candidate"
                icon = "🤖" if item["from"] == "system" else "👤"
                # Use columns for better chat bubble effect
                if item["from"] == "system":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 1rem; border-radius: 15px; margin: 0.5rem 0;
                                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
                        <strong>{icon} {role_tag}:</strong><br>{item['text']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.9); 
                                color: #333; padding: 1rem; border-radius: 15px; margin: 0.5rem 0;
                                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); border-left: 4px solid #667eea;">
                        <strong>{icon} {role_tag}:</strong><br>{item['text']}
                    </div>
                    """, unsafe_allow_html=True)

    # Live scoring widgets with enhanced 3D cards
    st.markdown("---")
    st.markdown("### 📊 Live Scoring & Analytics")
    metrics = st.session_state.get("metrics", {"confidence": 60})
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🎯 Confidence Score")
        confidence_val = int(metrics.get("confidence", 60))
        st.progress(confidence_val / 100)
        st.markdown(f"<div style='text-align: center; font-size: 2rem; font-weight: bold; color: #667eea;'>{confidence_val}%</div>", unsafe_allow_html=True)
        # radar chart with enhanced styling
        radar_df = pd.DataFrame({
            "metric": ["Clarity", "Technical", "Relevance", "Structure", "Confidence"],
            "score": [st.session_state.get("last_eval", {}).get("breakdown", {}).get("clarity", 12),
                      st.session_state.get("last_eval", {}).get("breakdown", {}).get("technical_depth", 12),
                      st.session_state.get("last_eval", {}).get("breakdown", {}).get("relevance", 12),
                      st.session_state.get("last_eval", {}).get("breakdown", {}).get("structure", 12),
                      metrics.get("confidence", 60)]
        })
        fig = px.line_polar(radar_df, r="score", theta="metric", line_close=True,
                           color_discrete_sequence=['#667eea'],
                           template="plotly_white")
        fig.update_traces(fill='toself', line=dict(width=3))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 100], showticklabels=True, ticks=""),
                angularaxis=dict(showticklabels=True)
            ),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.markdown("#### 📈 Detailed Breakdown")
        bd = st.session_state.get("last_eval", {}).get("breakdown", {})
        if bd:
            for k, v in bd.items():
                progress_val = int(min(100, (v / 25.0) * 100))
                st.markdown(f"**{k.replace('_', ' ').title()}**")
                st.progress(progress_val / 100)
                st.markdown(f"<div style='text-align: right; color: #667eea; font-weight: 600;'>{v:.1f}/25</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("Complete an answer to see detailed breakdown")

    with input_col:
        st.markdown("### ✍️ Your Answer")
        if voice_mode:
            st.markdown("#### 🎤 Voice Input")
            audio_file = st.file_uploader("Record or upload audio answer (wav/mp3)", type=["wav", "mp3", "m4a"])
            if audio_file is not None:
                with st.spinner("🎙️ Transcribing audio..."):
                    text_answer = stt_from_file(audio_file, api_key=os.getenv("OPENAI_API_KEY"))
                st.text_area("📝 Transcription", value=text_answer, height=100)
                user_input = st.text_area("✏️ Your answer (edit if needed)", value=text_answer, key="answer_input", height=150)
            else:
                user_input = st.text_area("✏️ Your answer", key="answer_input", height=150)
        else:
            user_input = st.text_area("✏️ Type your answer here...", key="answer_input", height=200)

        if st.button("✅ Submit Answer", use_container_width=True):
            if not user_input.strip():
                st.warning("Please enter an answer before submitting.")
            else:
                with st.spinner("Evaluating..."):
                    result = st.session_state.agent.receive_answer(user_input)
                    st.session_state.last_eval = result
                    # deep evaluation
                    last_q = st.session_state.agent.history[-2]["text"] if len(st.session_state.agent.history) >= 2 else ""
                    ideal = None
                    # try to find ideal from prompts
                    try:
                        import prompts
                        role_templ = prompts.QUESTION_TEMPLATES.get(st.session_state.agent.role, {})
                        # naive lookup
                        for sec in role_templ.values():
                            for itm in sec:
                                if isinstance(itm, dict) and itm.get("q") == last_q:
                                    ideal = itm.get("ideal")
                    except Exception:
                        ideal = None
                    deep = deep_evaluate(last_q, user_input, ideal_answer=ideal, api_key=os.getenv("OPENAI_API_KEY"))
                    # compute confidence and update metrics
                    conf = compute_confidence_score(user_input, result.get("breakdown", {}))
                    st.session_state.metrics = {"confidence": conf, "missed_topics": []}
                    # save to DB
                    try:
                        save_answer(st.session_state.interview_id, last_q, user_input, result.get("score", 0), metadata={"eval": result, "deep": deep})
                    except Exception:
                        pass

                    # Advance question adaptively
                    try:
                        import prompts
                        next_q = pick_next_question(prompts.QUESTION_TEMPLATES.get(st.session_state.agent.role, {}), st.session_state.asked_questions, difficulty, st.session_state.metrics)
                        st.session_state.asked_questions.append(next_q.get("q"))
                        st.session_state.agent._append_system(next_q.get("q"))
                    except Exception:
                        if st.session_state.agent.queue:
                            st.session_state.agent._append_system(st.session_state.agent._pop_next())

    st.markdown("---")

    if "last_eval" in st.session_state and st.session_state.last_eval:
        st.markdown("---")
        st.markdown("### ⭐ Last Evaluation")
        ev = st.session_state.last_eval
        eval_col1, eval_col2, eval_col3 = st.columns(3)
        with eval_col1:
            st.metric("📊 Overall Score", f"{ev['score']:.1f}/100")
        with eval_col2:
            decision_color = "#28a745" if ev['score'] >= 75 else ("#ffc107" if ev['score'] >= 50 else "#dc3545")
            decision_text = "✅ Excellent" if ev['score'] >= 75 else ("⚠️ Good" if ev['score'] >= 50 else "❌ Needs Improvement")
            st.markdown(f"<div style='text-align: center; padding: 1rem; background: {decision_color}20; border-radius: 10px;'><strong style='color: {decision_color}; font-size: 1.2rem;'>{decision_text}</strong></div>", unsafe_allow_html=True)
        with eval_col3:
            st.markdown("<br>", unsafe_allow_html=True)
        # Breakdown in a nice card format
        st.markdown("#### 📋 Score Breakdown")
        breakdown_cols = st.columns(len(ev.get("breakdown", {})))
        for idx, (k, v) in enumerate(ev.get("breakdown", {}).items()):
            with breakdown_cols[idx]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 1rem; border-radius: 10px; text-align: center;
                            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);">
                    <div style="font-size: 0.9rem; opacity: 0.9;">{k.replace('_', ' ').title()}</div>
                    <div style="font-size: 1.8rem; font-weight: bold;">{v:.1f}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">/25</div>
                </div>
                """, unsafe_allow_html=True)

    if "report" in st.session_state:
        st.markdown("---")
        st.markdown("### 📄 Final Interview Report")
        report = st.session_state.report
        # Display report in a nice card format
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2); margin: 1rem 0;">
            <h4 style="color: #667eea; margin-bottom: 1rem;">📊 Interview Summary</h4>
            <p><strong>Role:</strong> {report.get('role', 'N/A')}</p>
            <p><strong>Total Score:</strong> <span style="font-size: 1.5rem; color: #667eea; font-weight: bold;">{report.get('total_score', 0):.1f}/100</span></p>
            <p><strong>Decision:</strong> <span style="font-size: 1.2rem; font-weight: bold;">{report.get('decision', 'N/A')}</span></p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📋 View Detailed Report"):
            st.write(report)

if __name__ == "__main__":
    main()
