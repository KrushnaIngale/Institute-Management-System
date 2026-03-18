import streamlit as st
import pandas as pd
import requests
import time
import re
from io import StringIO
from datetime import datetime
from urllib.parse import quote

SHEET_ID = "1yvXENG5MVpnLiiuwcN20iTIaW48QxhnM9LhWnqDvAGk"
AUTO_REFRESH_SECS = 30

# Display label → actual Google Sheet tab name (as it appears in the sheet)
SHEET_MAP = {
    "📋 Dashboard":           "📋 Dashboard",
    "🏫 Colleges":            "🏫 Colleges",
    "🏢 Departments":         "🏢 Departments",
    "👨‍🏫 Faculty_Master":    "👨‍🏫 Faculty_Master",
    "🎓 Student_Master":      "🎓 Student_Master",
    "📅 Fac_Attendance_Sem1": "📅 Fac_Attendance_Sem1",
    "📅 Fac_Attendance_Sem2": "📅 Fac_Attendance_Sem2",
    "📅 Stu_Attendance_Sem1": "📅 Stu_Attendance_Sem1",
    "📅 Stu_Attendance_Sem2": "📅 Stu_Attendance_Sem2",
    "📝 Marks_Sem1":          "📝 Marks_Sem1",
    "📝 Marks_Sem2":          "📝 Marks_Sem2",
}

SHEETS = list(SHEET_MAP.keys())

st.set_page_config(
    page_title="IMS · SGGS Nanded",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = (
    "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>"
    "<style>"
    "html,body,.stApp,[class*='css']{font-family:'Inter',sans-serif!important;background:#F0F2F6!important;color:#1C1C1E!important;}"
    ".block-container{padding:1rem 2rem 2rem 2rem!important;max-width:100%!important;}"
    "section[data-testid='stSidebar']>div{background:#1E293B!important;}"
    "section[data-testid='stSidebar'] p,section[data-testid='stSidebar'] span,section[data-testid='stSidebar'] label,section[data-testid='stSidebar'] div{color:#E2E8F0!important;}"
    "section[data-testid='stSidebar'] hr{border-color:#334155!important;margin:0.5rem 0!important;}"
    "section[data-testid='stSidebar'] .stRadio label{font-size:0.85rem!important;padding:6px 10px!important;border-radius:6px!important;display:block!important;width:100%!important;word-break:break-word!important;}"
    "section[data-testid='stSidebar'] button{background:#3B82F6!important;color:#fff!important;border:none!important;border-radius:7px!important;}"
    ".card{background:#FFFFFF!important;border-radius:10px!important;border:1px solid #DDE1E7!important;padding:16px 20px!important;margin-bottom:14px!important;box-shadow:0 1px 4px rgba(0,0,0,0.06)!important;}"
    ".banner{display:flex;justify-content:space-between;align-items:center;}"
    ".btitle{font-size:1.2rem;font-weight:700;color:#0F172A;margin:0;}"
    ".bsub{font-size:0.8rem;color:#64748B;margin:2px 0 0 0;}"
    ".lpill{background:#F0FDF4;border:1px solid #86EFAC;color:#166534;border-radius:20px;padding:4px 12px;font-size:0.75rem;font-weight:600;display:inline-flex;align-items:center;gap:5px;}"
    ".dot{width:7px;height:7px;background:#22C55E;border-radius:50%;display:inline-block;animation:blink 1.8s infinite;}"
    "@keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}}"
    ".tsm{font-size:0.74rem;color:#64748B;margin-top:4px;}"
    ".krow{display:flex;gap:12px;margin-bottom:16px;}"
    ".kcard{flex:1;background:#FFFFFF;border-radius:10px;border:1px solid #DDE1E7;padding:14px 16px;border-top:3px solid var(--kc);box-shadow:0 1px 3px rgba(0,0,0,0.05);}"
    ".knum{font-size:1.8rem;font-weight:700;line-height:1.1;}"
    ".klbl{font-size:0.74rem;color:#64748B;font-weight:500;margin-top:3px;}"
    ".sbar{background:#FFFFFF;border-radius:10px;border:1px solid #DDE1E7;padding:11px 16px;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);}"
    ".stitle{font-size:1rem;font-weight:600;color:#0F172A;}"
    ".bgrp{display:flex;gap:7px;align-items:center;}"
    ".bdg{border-radius:20px;padding:3px 11px;font-size:0.74rem;font-weight:500;border:1px solid;display:inline-block;}"
    ".bdgb{background:#EFF6FF;color:#1D4ED8;border-color:#BFDBFE;}"
    ".bdgs{background:#F8FAFC;color:#475569;border-color:#CBD5E1;}"
    ".fbox{background:#F8FAFC;border-radius:8px;border:1px solid #E2E8F0;padding:12px 16px;margin-bottom:12px;}"
    ".fttl{font-size:0.7rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px;}"
    ".rbar{font-size:0.81rem;color:#475569;margin-bottom:8px;display:flex;align-items:center;gap:5px;}"
    ".rnum{font-weight:700;color:#0F172A;}"
    ".stTextInput label{font-size:0.8rem!important;font-weight:500!important;color:#374151!important;}"
    ".stTextInput input{background:#FFFFFF!important;border:1.5px solid #CBD5E1!important;border-radius:7px!important;color:#0F172A!important;font-size:0.88rem!important;}"
    ".stTextInput input:focus{border-color:#3B82F6!important;box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important;}"
    ".stMultiSelect label{font-size:0.8rem!important;font-weight:500!important;color:#374151!important;}"
    "[data-baseweb='select']>div{background:#FFFFFF!important;border:1.5px solid #CBD5E1!important;border-radius:7px!important;color:#0F172A!important;}"
    # Light mode dataframe via gdg CSS vars
    ":root{--gdg-bg-cell:#FFFFFF;--gdg-bg-cell-medium:#F8FAFC;--gdg-bg-header:#F1F5F9;--gdg-text-header:#1E293B;--gdg-text-dark:#1E293B;--gdg-text-medium:#475569;--gdg-border-color:#E2E8F0;--gdg-accent-color:#3B82F6;}"
    "[data-testid='stDataFrame']{background:#FFFFFF!important;border-radius:8px!important;border:1px solid #DDE1E7!important;overflow:hidden!important;}"
    "[data-testid='stDataFrame']>div{background:#FFFFFF!important;}"
    ".stButton>button{background:#3B82F6!important;color:#FFFFFF!important;border:none!important;border-radius:7px!important;font-weight:500!important;}"
    ".stButton>button:hover{background:#2563EB!important;}"
    ".stDownloadButton>button{background:#FFFFFF!important;color:#374151!important;border:1.5px solid #CBD5E1!important;border-radius:7px!important;font-size:0.84rem!important;}"
    ".stDownloadButton>button:hover{border-color:#3B82F6!important;color:#2563EB!important;background:#EFF6FF!important;}"
    ".sec-title{font-size:0.7rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #F1F5F9;}"
    ".stAlert{border-radius:8px!important;}"
    "</style>"
)
st.markdown(CSS, unsafe_allow_html=True)


# ── Data loading — try multiple URL strategies ─────────────────────
@st.cache_data(ttl=AUTO_REFRESH_SECS, show_spinner=False)
def load_sheet(display_name: str) -> tuple[pd.DataFrame, str]:
    """Returns (dataframe, error_message). error_message is '' on success."""
    tab_name = SHEET_MAP.get(display_name, display_name)

    # Strategy 1: gviz/tq with encoded emoji tab name
    # Strategy 2: strip emoji, use only the word part after the space
    # Strategy 3: export?format=csv with encoded tab name
    clean_name = tab_name.split(" ", 1)[-1] if " " in tab_name else tab_name

    urls = [
        # Try with full emoji tab name (percent-encoded)
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(tab_name)}",
        # Try with just the word part (no emoji) — Google sometimes accepts this
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(clean_name)}",
        # Try export endpoint with full name
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={quote(tab_name)}",
        # Try export endpoint with clean name
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={quote(clean_name)}",
    ]

    last_error = ""
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and len(r.text) > 10:
                # Check it's not an HTML error page
                if r.text.strip().startswith("<"):
                    last_error = f"Got HTML response (not CSV) from: {url}"
                    continue
                df = pd.read_csv(StringIO(r.text))
                df.dropna(how="all", inplace=True)
                df.dropna(axis=1, how="all", inplace=True)
                df.columns = [str(c).strip() for c in df.columns]
                if df.empty or (len(df.columns) == 1 and "Unnamed" in df.columns[0]):
                    last_error = "Empty or malformed data returned"
                    continue
                return df, ""
            else:
                last_error = f"HTTP {r.status_code} from {url}"
        except Exception as e:
            last_error = str(e)

    return pd.DataFrame(), last_error


def enrich_display(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Status" in df.columns:
        df["Status"] = df["Status"].apply(
            lambda v: ("🔴 " + str(v)) if "Detained" in str(v)
            else ("🟢 " + str(v)) if "Regular" in str(v) else str(v)
        )
    if "Result" in df.columns:
        df["Result"] = df["Result"].apply(
            lambda v: "✅ PASS" if str(v).strip() == "PASS"
            else "❌ FAIL" if str(v).strip() == "FAIL" else str(v)
        )
    return df


# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**🎓 IMS Navigation**")
    st.markdown("---")
    selected_sheet = st.radio("nav", SHEETS, index=0, label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**⚙ Settings**")
    auto_refresh = st.toggle("Live Auto-Refresh", value=True)
    refresh_interval = st.slider("Interval (sec)", 10, 120, AUTO_REFRESH_SECS, step=5, disabled=not auto_refresh)
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown(
        f"<small style='color:#94A3B8'>📡 <a href='https://docs.google.com/spreadsheets/d/{SHEET_ID}'"
        f" target='_blank' style='color:#60A5FA;text-decoration:none'>Open Google Sheet ↗</a></small>",
        unsafe_allow_html=True,
    )


# ── Load data ──────────────────────────────────────────────────────
with st.spinner("Fetching latest data …"):
    df, load_error = load_sheet(selected_sheet)

now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")

# ── Show load errors prominently ──────────────────────────────────
if load_error:
    st.error(
        f"⚠️ **Could not load sheet: {selected_sheet}**\n\n"
        f"Error: `{load_error}`\n\n"
        "**Possible fixes:**\n"
        "1. Make sure the Google Sheet is set to **Anyone with the link can view**\n"
        "2. The sheet tab names in the app must exactly match the tab names in Google Sheets\n"
        "3. Try clicking **🔄 Refresh Now** in the sidebar"
    )
    st.stop()

# ── Top banner ─────────────────────────────────────────────────────
live_lbl = f"Live · every {refresh_interval}s" if auto_refresh else "Manual refresh"
st.markdown(
    f"<div class='card banner'>"
    f"<div><p class='btitle'>🎓 Institute Management System</p>"
    f"<p class='bsub'>SGGS Nanded · Academic Year 2024–25</p></div>"
    f"<div style='text-align:right'>"
    f"<div><span class='lpill'><span class='dot'></span>{live_lbl}</span></div>"
    f"<div class='tsm'>Last fetched: <b>{now_str}</b></div>"
    f"</div></div>",
    unsafe_allow_html=True,
)


# ── DASHBOARD ──────────────────────────────────────────────────────
if selected_sheet == "📋 Dashboard":
    kpis = [("10","Colleges","#3B82F6"),("100","Departments","#8B5CF6"),
            ("200","Faculty","#0EA5E9"),("1,300","Students","#10B981"),("3","Exams","#F59E0B")]
    html = "<div class='krow'>"
    for n, l, c in kpis:
        html += f"<div class='kcard' style='--kc:{c}'><div class='knum' style='color:{c}'>{n}</div><div class='klbl'>{l}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("<div class='card'><div class='sec-title'>📋 Sheet Directory</div>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=380)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(f"💡 Select any sheet from the left sidebar. Auto-refresh is {'**ON** · every ' + str(refresh_interval) + 's' if auto_refresh else '**OFF**'}.")


# ── ALL OTHER SHEETS ───────────────────────────────────────────────
else:
    st.markdown(
        f"<div class='sbar'><span class='stitle'>{selected_sheet}</span>"
        f"<div class='bgrp'><span class='bdg bdgb'>📊 {len(df):,} records</span>"
        f"<span class='bdg bdgs'>🕐 {now_str}</span></div></div>",
        unsafe_allow_html=True,
    )

    FILTERABLE = ["College ID","Dept ID","Semester","Result","Status","Category","Designation"]
    filter_cols = [c for c in FILTERABLE if c in df.columns]
    active_filters: dict = {}

    st.markdown("<div class='fbox'><div class='fttl'>🔍 Filter &amp; Search</div>", unsafe_allow_html=True)
    search_query = st.text_input("Search", placeholder="Name, email, reg no, ID …",
                                  key=f"s_{selected_sheet}", label_visibility="collapsed")
    if filter_cols:
        cols_ui = st.columns(min(len(filter_cols), 4))
        for i, col in enumerate(filter_cols[:4]):
            with cols_ui[i]:
                opts = sorted(df[col].dropna().astype(str).unique().tolist())
                chosen = st.multiselect(col, opts, default=[], key=f"f_{selected_sheet}_{col}")
                if chosen:
                    active_filters[col] = chosen
    st.markdown("</div>", unsafe_allow_html=True)

    fdf = df.copy()
    for col, vals in active_filters.items():
        fdf = fdf[fdf[col].astype(str).isin(vals)]
    if search_query.strip():
        mask = fdf.apply(lambda row: row.astype(str).str.contains(
            search_query.strip(), case=False, na=False).any(), axis=1)
        fdf = fdf[mask]

    tr, fr = len(df), len(fdf)
    if fr < tr:
        st.markdown(
            f"<div class='rbar'>Showing <span class='rnum'>&nbsp;{fr:,}&nbsp;</span> of "
            f"<span class='rnum'>&nbsp;{tr:,}&nbsp;</span> records "
            f"<span class='bdg bdgb'>{tr-fr:,} filtered out</span></div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='rbar'>Showing all <span class='rnum'>&nbsp;{tr:,}&nbsp;</span> records</div>",
            unsafe_allow_html=True)

    if fdf.empty:
        st.warning("No records match your filters.")
    else:
        st.dataframe(enrich_display(fdf), use_container_width=True,
                     hide_index=True, height=min(44 + fr * 35, 620))

    st.download_button(
        "⬇ Download CSV",
        fdf.to_csv(index=False).encode("utf-8"),
        f"{selected_sheet.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv",
    )


# ── Auto-refresh ───────────────────────────────────────────────────
if auto_refresh:
    time.sleep(refresh_interval)
    st.cache_data.clear()
    st.rerun()
