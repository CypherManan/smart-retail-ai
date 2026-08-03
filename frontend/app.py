"""
Module C — Production-Grade Frontend/Dashboard
Streamlit UI that talks to the FastAPI backend over HTTP.
Run the FastAPI server first (uvicorn app.main:app), then run this file
with `streamlit run frontend/app.py`.
"""
import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"
API_KEY = "demo-key-123"
HEADERS = {"X-API-Key": API_KEY}

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Smart Retail AI Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. CUSTOM CSS — Clean, Professional, Explicit Colors
# ============================================================
# We inject CSS that explicitly sets colors on every custom element.
# This avoids Streamlit theme conflicts (light vs dark mode).
CUSTOM_CSS = """
<style>
/* ── Base font ── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* ── Explicit text color on all custom HTML wrappers ── */
[data-testid="stMarkdown"] div[style*="color"] { color: inherit; }

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px !important;
    background: #f1f5f9 !important;
    padding: 4px !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab"] {
    height: 40px !important;
    padding: 0 18px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: #475569 !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #ffffff !important;
    color: #0f172a !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #4f46e5 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);
    transform: translateY(-1px);
}
[data-testid="stMetric"] > div:first-child {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #2563eb !important; opacity: 0.85;
}
[data-testid="stMetric"] > div:nth-child(2) {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #2563eb !important;
    margin-top: 6px !important;
    font-variant-numeric: tabular-nums !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    transition: all 0.2s ease !important;
    height: 40px !important;
}
.stButton > button:hover {
    background: #4338ca !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    background: #ffffff !important;
    color: #0f172a !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #1e3a5f !important; opacity: 0.6;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5 !important;
    background: #eef2ff !important;
}
[data-testid="stFileUploader"] > div > small {
    color: #64748b !important;
}

/* ── Chat messages ── */
.stChatMessage {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stChatMessage [data-testid="stChatMessageAvatar"] {
    background: #eef2ff !important;
    color: #4f46e5 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .stTabs [data-baseweb="tab"] {
        padding: 0 10px !important;
        font-size: 12px !important;
    }
    [data-testid="stMetric"] { padding: 12px !important; }
    [data-testid="stMetric"] > div:nth-child(2) { font-size: 20px !important; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# 3. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 16px 0 20px;">
            <div style="font-size:36px; margin-bottom:6px;">🛍️</div>
            <div style="font-size:16px; font-weight:700; ">Smart Retail AI</div>
            <div style="font-size:12px; opacity:0.65; margin-top:4px;">Intelligence Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        "<p style='font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; opacity:0.55; margin-bottom:8px;'>System Status</p>",
        unsafe_allow_html=True,
    )

    api_online = False
    try:
        resp = requests.get(f"{API_BASE_URL}/dashboard/stats", headers=HEADERS, timeout=2)
        api_online = resp.status_code == 200
    except Exception:
        api_online = False

    if api_online:
        st.markdown(
            '<span style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:#d1fae5;color:#065f46;">● API Online</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:#fee2e2;color:#991b1b;">● API Offline</span>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        "<p style='font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; opacity:0.55; margin-bottom:8px;'>Configuration</p>",
        unsafe_allow_html=True,
    )
    API_BASE_URL = st.text_input("API Base URL", value=API_BASE_URL, label_visibility="collapsed")
    API_KEY = st.text_input("API Key", value=API_KEY, type="password", label_visibility="collapsed")
    HEADERS = {"X-API-Key": API_KEY}
    st.divider()
    st.caption("v2.0.0 · © 2026 Smart Retail AI")

# ============================================================
# 4. MAIN HEADER
# ============================================================
st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="margin:0 0 4px 0; font-size:24px; font-weight:700; letter-spacing:-0.02em;">Smart Retail & Customer Intelligence</h1>
        <p style="font-size:15px; margin:0; opacity:0.7;">Face recognition · Product classification · Sentiment analysis · Chatbot</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 5. TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "😊 Sentiment", "💬 Chatbot", "📦 Products", "🧑 Face ID"]
)

# ---------------------------------------------------------------- Dashboard
with tab1:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#eef2ff; color:#4f46e5; font-size:15px;">📊</div>
            <div style="font-size:15px; font-weight:600; ">Live Analytics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh stats", key="refresh_stats"):
        st.rerun()

    try:
        resp = requests.get(f"{API_BASE_URL}/dashboard/stats", headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            stats = resp.json()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Visits", f"{stats['total_visits']:,}")
            with col2:
                st.metric("Returning Customers", f"{stats['returning_customers']:,}")
            with col3:
                st.metric("Feedback Analyzed", f"{stats['total_feedback_analyzed']:,}")

            if stats.get("sentiment_breakdown"):
                st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                        <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#d1fae5; color:#065f46; font-size:15px;">📈</div>
                        <div style="font-size:15px; font-weight:600; ">Sentiment Breakdown</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.bar_chart(stats["sentiment_breakdown"], use_container_width=True)
            else:
                st.info("No sentiment data yet — try the Sentiment tab to analyze feedback.")
        else:
            st.error(f"API returned {resp.status_code}: {resp.text}")
    except requests.exceptions.ConnectionError:
        st.error("Can't reach the API. Is `uvicorn app.main:app` running on port 8000?")
    except Exception as e:
        st.error(f"Error: {e}")

# ---------------------------------------------------------------- Sentiment
with tab2:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#dbeafe; color:#1e40af; font-size:15px;">😊</div>
            <div style="font-size:15px; font-weight:600; ">Customer Sentiment Analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([2, 1])
    with col_left:
        text_input = st.text_area(
            "Enter a review or feedback message",
            placeholder="This product is amazing! The quality exceeded my expectations...",
            height=160,
        )
        analyze_btn = st.button("🔍 Analyze Sentiment", key="analyze_sentiment", use_container_width=True)

    with col_right:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); color:#1e3a5f;">
                <div style="font-size:14px; font-weight:600; margin-bottom:6px;">💡 Tips</div>
                <div style="font-size:13px; color:#1e3a5f; opacity:0.75; line-height:1.6;">
                    Write a detailed review for best results. The model analyzes tone, word choice, and context to determine sentiment polarity.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if analyze_btn:
        if not text_input.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Analyzing sentiment..."):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/analyze-sentiment",
                        headers=HEADERS,
                        json={"text": text_input},
                        timeout=5,
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        sentiment = result["sentiment"].upper()
                        confidence = result["confidence"] * 100
                        badge_bg = "#d1fae5" if sentiment == "POSITIVE" else "#fee2e2" if sentiment == "NEGATIVE" else "#fef3c7"
                        badge_color = "#065f46" if sentiment == "POSITIVE" else "#991b1b" if sentiment == "NEGATIVE" else "#92400e"

                        st.markdown(
                            f"""
                            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); margin-top:12px; color:#1e3a5f;">
                                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                                    <div>
                                        <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; opacity:0.55; margin-bottom:4px;">Detected Sentiment</div>
                                        <div style="font-size:22px; font-weight:700; ">{sentiment}</div>
                                    </div>
                                    <span style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:{badge_bg};color:{badge_color};">{confidence:.1f}% confidence</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.bar_chart(result["scores"], use_container_width=True)
                    else:
                        st.error(f"API returned {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Can't reach the API. Is `uvicorn app.main:app` running on port 8000?")

# ------------------------------------------------------------------ Chatbot
with tab3:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#fef3c7; color:#92400e; font-size:15px;">💬</div>
            <div style="font-size:15px; font-weight:600; ">AI Support Chatbot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([2, 1])
    with col_left:
        message = st.text_input("Your message", placeholder="Where is my order? How do I return an item?", label_visibility="collapsed")
        send_btn = st.button("📤 Send Message", key="send_chat", use_container_width=True)

    with col_right:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); color:#1e3a5f;">
                <div style="font-size:14px; font-weight:600; margin-bottom:6px;">🤖 Capabilities</div>
                <div style="font-size:13px; color:#1e3a5f; opacity:0.75; line-height:1.6;">
                    Order tracking, returns, product recommendations, store hours, and general support questions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if send_btn:
        if not message.strip():
            st.warning("Please enter a message first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/chatbot", headers=HEADERS, json={"message": message}, timeout=5
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        st.chat_message("assistant").write(result["reply"])
                        st.caption(f"Detected intent: `{result['intent']}` ({result['confidence']*100:.1f}% confidence)")
                    else:
                        st.error(f"API returned {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Can't reach the API. Is `uvicorn app.main:app` running on port 8000?")

# ------------------------------------------------------- Product Classifier
with tab4:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#fce7f3; color:#9d174d; font-size:15px;">📦</div>
            <div style="font-size:15px; font-weight:600; ">Product Image Classifier</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        uploaded_file = st.file_uploader("Upload a product photo", type=["jpg", "jpeg", "png"], key="product")
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded image", width=280)
            classify_btn = st.button("🔮 Classify Product", key="classify_product", use_container_width=True)

            if classify_btn:
                with st.spinner("Classifying image..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        resp = requests.post(f"{API_BASE_URL}/classify-product", headers=HEADERS, files=files, timeout=10)
                        if resp.status_code == 200:
                            result = resp.json()
                            if result.get("category"):
                                st.markdown(
                                    f"""
                                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); margin-top:10px; color:#1e3a5f;">
                                        <div style="display:flex; align-items:center; justify-content:space-between;">
                                            <div>
                                                <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; opacity:0.55; margin-bottom:4px;">Category</div>
                                                <div style="font-size:20px; font-weight:700; ">{result['category']}</div>
                                            </div>
                                            <span style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;background:#dbeafe;color:#1e40af;">{result['confidence']*100:.1f}% confidence</span>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.error(result.get("error", "Unknown error"))
                        else:
                            st.error(f"API returned {resp.status_code}: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Can't reach the API. Is `uvicorn app.main:app` running on port 8000?")

    with col_right:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); color:#1e3a5f;">
                <div style="font-size:14px; font-weight:600; margin-bottom:6px;">📋 Supported Categories</div>
                <div style="font-size:13px; color:#1e3a5f; opacity:0.75; line-height:1.6;">
                    The classifier recognizes major retail categories including apparel, electronics, home goods, food & beverages, beauty, sports, and more. Upload a clear, well-lit photo for best accuracy.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------------- Face Recognition
with tab5:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
            <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; background:#ede9fe; color:#5b21b6; font-size:15px;">🧑</div>
            <div style="font-size:15px; font-weight:600; ">Customer Face Recognition</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        uploaded_face = st.file_uploader("Upload a face photo", type=["jpg", "jpeg", "png"], key="face")
        if uploaded_face is not None:
            st.image(uploaded_face, caption="Uploaded image", width=280)
            recognize_btn = st.button("🔍 Recognize Customer", key="recognize_face", use_container_width=True)

            if recognize_btn:
                with st.spinner("Analyzing face..."):
                    try:
                        files = {"file": (uploaded_face.name, uploaded_face.getvalue(), uploaded_face.type)}
                        resp = requests.post(f"{API_BASE_URL}/recognize-face", headers=HEADERS, files=files, timeout=10)
                        if resp.status_code == 200:
                            result = resp.json()
                            status = result.get("status")

                            if status == "returning_customer":
                                st.markdown(
                                    f"""
                                    <div style="background:#ffffff; border:1px solid #10b981; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); margin-top:10px; color:#1e3a5f;">
                                        <div style="display:flex; align-items:center; gap:10px;">
                                            <div style="font-size:22px;">👋</div>
                                            <div>
                                                <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; opacity:0.55; margin-bottom:4px;">Welcome back</div>
                                                <div style="font-size:18px; font-weight:700; ">{result['customer_id']}</div>
                                                <div style="font-size:12px; color:#1e3a5f; opacity:0.65; margin-top:2px;">Distance: {result['distance']}</div>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            elif status == "unknown_customer":
                                st.info(f"New/unrecognized customer (distance: {result['distance']})")
                            elif status == "no_face_detected":
                                st.warning("No face detected in the image.")
                            else:
                                st.error(result.get("error", "Unknown error"))
                        else:
                            st.error(f"API returned {resp.status_code}: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Can't reach the API. Is `uvicorn app.main:app` running on port 8000?")

    with col_right:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); color:#1e3a5f;">
                <div style="font-size:14px; font-weight:600; margin-bottom:6px;">🔒 Privacy Notice</div>
                <div style="font-size:13px; color:#1e3a5f; opacity:0.75; line-height:1.6;">
                    Face data is processed securely and only used for customer identification. Images are not stored permanently. Ensure the customer's consent before using this feature.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )