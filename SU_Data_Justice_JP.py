"""
Data Justice Assistent — Streamlit App
Exact ontwerp gebaseerd op Archive_4 design
Groq API (llama-3.3-70b-versatile) voor AI chat
"""
pip install streamlit groq
streamlit run SU_Data_Justice_JP.py

import streamlit as st
import json
import os
import time
import math
import re
from Groq import groq

# ─────────────────────────────────────────────
# PAGINA CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Data Justice Assistent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — pixel-perfect Archive_4 ontwerp
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ── Reset & Global ── */
html, body, .stApp {
    background-color: #0B1220 !important;
    color: #F1F5F9 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
* { box-sizing: border-box; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1C2A40 !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 14px 14px 14px 14px !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {
    color: #8B9CB8 !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 14px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background: #1a2438 !important;
    color: #8B9CB8 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 7px 12px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1f2d47 !important;
    color: #F1F5F9 !important;
    border-color: #3B7EF6 !important;
}
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: #3B7EF6 !important;
    color: white !important;
    border-color: #3B7EF6 !important;
    font-weight: 600 !important;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1a2438 !important;
    border: 1px solid #253047 !important;
    color: #F1F5F9 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}

/* ── Topbar ── */
.topbar {
    background: #111827;
    border-bottom: 1px solid #1C2A40;
    padding: 0 24px;
    height: 64px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.tb-logo-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}
.tb-logo-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: #1a4fa0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.tb-logo-text {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: #F1F5F9;
}
.tb-divider {
    width: 1px;
    height: 32px;
    background: #1C2A40;
    margin: 0 8px;
}
.tb-project-wrap { display: flex; flex-direction: column; }
.tb-project-name {
    font-family: 'Sora', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #4a8af4;
    line-height: 1.2;
}
.tb-project-sub {
    font-size: 11px;
    color: #5a7090;
    display: flex;
    align-items: center;
    gap: 5px;
}
.tb-actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 10px;
}
.tb-btn {
    background: #111827;
    border: 1px solid #253047;
    border-radius: 8px;
    color: #8B9CB8;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    padding: 7px 14px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
    white-space: nowrap;
}
.tb-btn:hover { border-color: #3B7EF6; color: #F1F5F9; }
.tb-btn-primary {
    background: #3B7EF6;
    border-color: #3B7EF6;
    color: white;
    font-weight: 600;
}
.tb-btn-primary:hover { background: #5B9BFF; }

/* ── Chat berichten ── */
.chat-ts {
    text-align: center;
    font-size: 11px;
    color: #3a5070;
    margin: 8px 0 12px 0;
}
.msg-bot-wrap { display: flex; flex-direction: column; margin-bottom: 16px; }
.msg-user-wrap { display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 16px; }
.msg-sender {
    font-size: 11px;
    color: #5B9BFF;
    font-weight: 600;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.msg-sender-sub { font-size: 10px; color: #5a7090; font-weight: 400; margin-top: 1px; }
.bubble-bot {
    background: #151f33;
    border: 1px solid #1C2A40;
    border-radius: 10px 10px 10px 3px;
    padding: 12px 16px;
    max-width: 84%;
    font-size: 13px;
    line-height: 1.65;
    color: #F1F5F9;
}
.bubble-user {
    background: #3B7EF6;
    border-radius: 10px 10px 3px 10px;
    padding: 11px 15px;
    max-width: 72%;
    font-size: 13px;
    line-height: 1.6;
    color: white;
}
.user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #3B7EF6;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: white;
    margin-left: 8px;
    flex-shrink: 0;
    vertical-align: middle;
}

/* ── Persona kaart (in chat) ── */
.pc-card {
    background: #151f33;
    border: 1px solid #1C2A40;
    border-radius: 12px;
    padding: 16px;
    max-width: 860px;
    margin-top: 8px;
    position: relative;
}
.pc-header {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    margin-bottom: 14px;
}
.pc-photo {
    width: 100px;
    height: 100px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
    background: #253047;
}
.pc-main { flex: 1; min-width: 0; }
.pc-name {
    font-family: 'Sora', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #F1F5F9;
}
.pc-diag { font-size: 11px; color: #1DB87A; margin: 2px 0 6px; }
.pc-quote {
    font-size: 12px;
    color: #8B9CB8;
    font-style: italic;
    line-height: 1.55;
    margin-bottom: 9px;
}
.pc-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.pc-tag {
    background: #1a2438;
    border: 1px solid #253047;
    color: #8B9CB8;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
}
.pc-age {
    background: rgba(59,126,246,.18);
    color: #5B9BFF;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
}
.view-full-btn {
    background: transparent;
    border: 1px solid #253047;
    border-radius: 7px;
    color: #8B9CB8;
    font-size: 11px;
    padding: 4px 10px;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.15s;
    white-space: nowrap;
    margin-top: 6px;
    display: block;
}
.view-full-btn:hover { border-color: #3B7EF6; color: #5B9BFF; }
.pc-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid #1C2A40;
}
.pc-det-row { display: flex; align-items: flex-start; gap: 7px; }
.pc-det-icon { font-size: 13px; flex-shrink: 0; margin-top: 1px; }
.pc-det-label { color: #5a7090; font-size: 11px; min-width: 74px; flex-shrink: 0; }
.pc-det-val { color: #F1F5F9; font-size: 11px; line-height: 1.4; }

/* ── XAI Box ── */
.xai-box {
    background: #0f1929;
    border: 1px solid #1C2A40;
    border-radius: 10px;
    padding: 13px 16px;
    max-width: 860px;
    margin-top: 6px;
}
.xai-title {
    font-size: 12px;
    font-weight: 600;
    color: #F1F5F9;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 5px;
}
.xai-accent { color: #5B9BFF; }
.xai-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
}
.xai-col-label {
    font-size: 10px;
    color: #5a7090;
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: 6px;
}
.xai-source { font-size: 11px; color: #F1F5F9; padding: 2px 0; }
.xai-source::before { content: "• "; color: #3B7EF6; }
.xai-badge {
    display: inline-block;
    background: rgba(59,126,246,.15);
    color: #5B9BFF;
    border-radius: 12px;
    padding: 2px 9px;
    font-size: 10px;
    margin: 2px 2px 2px 0;
}
.xai-expl { font-size: 11px; color: #8B9CB8; line-height: 1.5; }
.xai-feedback {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    justify-content: flex-end;
}
.xai-fb-label { font-size: 11px; color: #5a7090; }
.feedback-btn {
    background: transparent;
    border: 1px solid #253047;
    border-radius: 6px;
    color: #5a7090;
    padding: 3px 9px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
}
.feedback-btn:hover { border-color: #3B7EF6; color: #3B7EF6; }

/* ── Reliability bar ── */
.rel-bar {
    background: #111827;
    border-top: 1px solid #1C2A40;
    padding: 9px 24px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.rel-label { font-size: 11px; color: #5a7090; }
.rel-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
}
.rel-amber { background: rgba(245,158,11,.13); color: #F59E0B; border: 1px solid rgba(245,158,11,.3); }
.rel-green { background: rgba(29,184,122,.1); color: #1DB87A; border: 1px solid rgba(29,184,122,.3); }
.rel-blue { background: rgba(59,126,246,.1); color: #5B9BFF; border: 1px solid rgba(59,126,246,.25); }
.rel-red { background: rgba(239,68,68,.12); color: #EF4444; border: 1px solid rgba(239,68,68,.3); }
.rel-view {
    margin-left: auto;
    font-size: 11px;
    color: #3B7EF6;
    cursor: pointer;
    font-weight: 500;
}
.rel-view:hover { text-decoration: underline; }

/* ── Input ── */
.input-wrap {
    background: #0B1220;
    border-top: 1px solid #1C2A40;
    padding: 12px 22px 16px;
}
.input-label { font-size: 11px; color: #5a7090; margin-bottom: 6px; }
.input-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #111827;
    border: 1px solid #253047;
    border-radius: 10px;
    padding: 8px 14px;
    transition: border-color 0.2s;
}
.input-row:focus-within { border-color: #3B7EF6; }
.spark-icon { font-size: 20px; color: #3B7EF6; flex-shrink: 0; line-height: 1; }

/* Main chat input */
.stTextInput input {
    background: #111827 !important;
    border: 1px solid #253047 !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 16px !important;
    height: 44px !important;
}
.stTextInput input:focus { border-color: #3B7EF6 !important; box-shadow: none !important; }
.stTextInput input::placeholder { color: #3a5070 !important; }
.stTextInput label { color: #5a7090 !important; font-size: 11px !important; }

/* Send button */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="column"] div[data-testid="stButton"] > button {
    background: #3B7EF6 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 20px !important;
    height: 44px !important;
    transition: background 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #5B9BFF !important;
}

/* ── Sidebar persona items ── */
.sb-persona-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid transparent;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.15s;
}
.sb-persona-item:hover {
    background: rgba(59,126,246,.07);
    border-color: rgba(59,126,246,.2);
}
.sb-persona-item.active {
    background: rgba(59,126,246,.13);
    border-color: rgba(59,126,246,.4);
}
.sb-persona-avatar {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: #1f2d47;
    border: 1px solid #253047;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    overflow: hidden;
}
.sb-persona-avatar-active { background: rgba(59,126,246,.15); }
.sb-persona-name {
    font-size: 12px;
    font-weight: 600;
    color: #F1F5F9;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sb-persona-meta { font-size: 10px; color: #5a7090; }
.sb-persona-age {
    font-size: 11px;
    font-weight: 600;
    color: #8B9CB8;
    white-space: nowrap;
    flex-shrink: 0;
}
.sb-persona-age-active { color: #5B9BFF; }

/* ── Dataset & project items ── */
.sb-dataset-item {
    background: #1a2438;
    border: 1px solid #253047;
    border-radius: 7px;
    padding: 8px 11px;
    font-size: 12px;
    color: #8B9CB8;
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 6px;
}
.sb-project-item {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 6px 9px;
    border-radius: 7px;
    font-size: 12px;
    color: #5a7090;
    cursor: pointer;
    transition: all 0.15s;
    margin-bottom: 3px;
    border: 1px solid transparent;
}
.sb-project-item:hover { background: rgba(59,126,246,.07); color: #F1F5F9; }
.sb-project-item.active {
    background: rgba(59,126,246,.1);
    border-color: rgba(59,126,246,.35);
    color: #F1F5F9;
}
.sb-view-all { font-size: 11px; color: #3B7EF6; cursor: pointer; padding: 4px 9px; }
.sb-view-all:hover { text-decoration: underline; }

/* ── Sidebar footer ── */
.sb-footer {
    display: flex;
    align-items: center;
    gap: 9px;
    padding-top: 12px;
    border-top: 1px solid #1C2A40;
    margin-top: auto;
}
.sb-designer-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #3B7EF6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}
.sb-designer-name { font-size: 12px; color: #F1F5F9; font-weight: 500; }
.sb-designer-role { font-size: 10px; color: #5a7090; }

/* ── Section labels ── */
.sb-section-title {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #F1F5F9 !important;
    margin-bottom: 2px !important;
}
.sb-section-sub {
    font-size: 10px;
    color: #3B7EF6;
    margin-bottom: 8px;
    display: block;
}
.sb-divider { border: none; border-top: 1px solid #1C2A40; margin: 10px 0; }

/* ── Validation Panel (rechts) ── */
.val-panel {
    background: #111827;
    border: 1px solid #1C2A40;
    border-radius: 12px;
    padding: 16px;
    width: 100%;
}
.val-panel-title {
    font-family: 'Sora', sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: #4a8af4;
    margin-bottom: 14px;
}
.val-check-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #1C2A40;
    font-size: 12px;
}
.val-check-label { color: #8B9CB8; }
.val-check-ok { color: #1DB87A; font-size: 11px; cursor: pointer; }
.val-check-warn { color: #F59E0B; font-size: 11px; cursor: pointer; }
.val-check-med { color: #EF4444; font-size: 11px; cursor: pointer; }

/* Score ring */
.score-ring-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 14px 0;
    padding: 12px;
    background: #151f33;
    border-radius: 10px;
    border: 1px solid #1C2A40;
}
.score-legend { display: flex; flex-direction: column; gap: 4px; }
.score-legend-good { font-size: 12px; font-weight: 600; color: #1DB87A; }
.score-legend-improve { font-size: 11px; color: #8B9CB8; }
.score-legend-link { font-size: 11px; color: #3B7EF6; cursor: pointer; }
.score-legend-link:hover { text-decoration: underline; }

/* Improve AI input section */
.improve-title {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #4a8af4;
    margin: 14px 0 10px;
}
.improve-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #1C2A40;
    font-size: 12px;
}
.improve-icon { font-size: 13px; margin-right: 5px; }
.improve-label { color: #F1F5F9; }
.improve-action { color: #5a7090; font-size: 11px; }

/* Full report panel */
.fr-section { margin-bottom: 14px; }
.fr-cat-title {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.fr-pct { font-size: 12px; color: #8B9CB8; }
.fr-bar-bg {
    background: #1C2A40;
    border-radius: 4px;
    height: 6px;
    margin-bottom: 8px;
    overflow: hidden;
}
.fr-bar-fill { height: 6px; border-radius: 4px; }
.fr-item {
    display: flex;
    align-items: center;
    gap: 7px;
    background: #151f33;
    border: 1px solid #1C2A40;
    border-radius: 7px;
    padding: 8px 10px;
    font-size: 11px;
    color: #F1F5F9;
    margin-bottom: 5px;
}
.fr-details-link { font-size: 11px; color: #3B7EF6; text-align: right; margin-top: 4px; cursor: pointer; }
.fr-details-link:hover { text-decoration: underline; }

/* Visualisatie sectie */
.vis-section { margin-top: 14px; }
.vis-title {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 10px;
}
.vis-ring-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}
.suggestions-title {
    font-size: 12px;
    font-weight: 600;
    color: #F1F5F9;
    margin: 10px 0 7px;
}
.suggestion-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #151f33;
    border: 1px solid #1C2A40;
    border-radius: 7px;
    padding: 8px 10px;
    font-size: 11px;
    color: #F1F5F9;
    margin-bottom: 5px;
}
.suggestion-star { color: #3B7EF6; font-size: 13px; }

/* Panel action buttons */
.panel-btn {
    background: #1a2438;
    border: 1px solid #253047;
    border-radius: 8px;
    color: #8B9CB8;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    padding: 8px 16px;
    cursor: pointer;
    transition: all 0.15s;
}
.panel-btn:hover { border-color: #3B7EF6; color: #F1F5F9; }
.panel-btn-primary {
    background: #3B7EF6;
    border-color: #3B7EF6;
    color: white;
    font-weight: 600;
}
.panel-btn-primary:hover { background: #5B9BFF; }
.panel-close {
    background: transparent;
    border: none;
    color: #5a7090;
    font-size: 16px;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
    float: right;
}
.panel-close:hover { color: #F1F5F9; }

/* ── Persona expanded in sidebar (screen 5) ── */
.sb-persona-expanded {
    background: #1a2438;
    border: 1px solid #253047;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 6px;
}
.sb-persona-exp-header { display: flex; align-items: center; gap: 9px; margin-bottom: 8px; }
.sb-persona-exp-photo {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    object-fit: cover;
    background: #253047;
    flex-shrink: 0;
}
.sb-persona-exp-name { font-size: 12px; font-weight: 600; color: #F1F5F9; }
.sb-persona-exp-diag { font-size: 10px; color: #EF4444; }
.sb-persona-exp-goals { font-size: 11px; color: #8B9CB8; margin-bottom: 6px; }
.sb-persona-exp-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 7px; }
.sb-persona-exp-tag {
    background: rgba(59,126,246,.15);
    color: #5B9BFF;
    border-radius: 20px;
    padding: 2px 8px;
    font-size: 10px;
}
.sb-persona-exp-quote {
    font-size: 11px;
    color: #8B9CB8;
    font-style: italic;
    line-height: 1.5;
    border-top: 1px solid #253047;
    padding-top: 7px;
}

/* ── Mood checker / Assign project dropdown overlays ── */
.dropdown-overlay {
    background: #1a2438;
    border: 1px solid #253047;
    border-radius: 10px;
    padding: 8px 0;
    min-width: 180px;
    box-shadow: 0 8px 32px rgba(0,0,0,.6);
}
.dropdown-item {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 7px 14px;
    font-size: 12px;
    color: #F1F5F9;
    cursor: pointer;
    transition: background 0.1s;
}
.dropdown-item:hover { background: rgba(59,126,246,.1); }
.dropdown-check {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #253047;
    background: transparent;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.dropdown-check.checked { background: #3B7EF6; border-color: #3B7EF6; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #1a2438 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
    font-size: 13px !important;
}
.streamlit-expanderContent {
    background: #111827 !important;
    border: 1px solid #253047 !important;
    border-top: none !important;
}

/* ── Progress bars ── */
.stProgress > div > div > div > div {
    background-color: #3B7EF6 !important;
}

/* ── Metrics ── */
.metric-card {
    background: #151f33;
    border: 1px solid #1C2A40;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}
.metric-val { font-size: 22px; font-weight: 700; margin-bottom: 2px; }
.metric-lbl { font-size: 10px; color: #8B9CB8; text-transform: uppercase; letter-spacing: .5px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #253047; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3B7EF6; }

/* ── Topbar Streamlit button rij — trekt omhoog in de topbar ── */
div[data-testid="stHorizontalBlock"]:has(button[key="tb_mood"]) {
    background: #111827;
    border-bottom: 1px solid #1C2A40;
    margin-top: -62px !important;
    padding: 0 24px 0 0 !important;
    gap: 8px !important;
    justify-content: flex-end;
    height: 64px;
    align-items: center;
    position: relative;
    z-index: 99;
}
div[data-testid="stHorizontalBlock"]:has(button[key="tb_mood"]) div[data-testid="stButton"] button {
    background: #111827 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    color: #8B9CB8 !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 6px 13px !important;
    height: 36px !important;
    white-space: nowrap !important;
    transition: all 0.15s !important;
}
div[data-testid="stHorizontalBlock"]:has(button[key="tb_mood"]) div[data-testid="stButton"] button:hover {
    border-color: #3B7EF6 !important;
    color: #F1F5F9 !important;
}
div[data-testid="stHorizontalBlock"]:has(button[key="tb_mood"]) div[data-testid="stButton"] button[kind="primary"] {
    background: #3B7EF6 !important;
    border-color: #3B7EF6 !important;
    color: white !important;
    font-weight: 600 !important;
}

/* "View Full Report" knop stijl */
div[data-testid="stButton"]:has(button[key="btn_view_full_report"]) button {
    background: transparent !important;
    border: none !important;
    color: #3B7EF6 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    padding: 4px 0 !important;
    height: auto !important;
    text-align: right !important;
    box-shadow: none !important;
}
div[data-testid="stButton"]:has(button[key="btn_view_full_report"]) button:hover {
    text-decoration: underline !important;
    color: #5B9BFF !important;
}

/* ── General divider ── */
hr { border-color: #1C2A40 !important; margin: 8px 0 !important; }</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────
def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)
    return None


client = get_groq_client()


# ─────────────────────────────────────────────
# PERSONA DATA
# ─────────────────────────────────────────────
PERSONAS = [
    {
        "id": 1,
        "initials": "AJ",
        "naam": "Alex Johnson",
        "leeftijd": 52,
        "leeftijd_label": "52jr",
        "geslacht": "Vrouw",
        "diagnose": "Reumatoïde artritis",
        "quote": "I want to keep living my life, but the fatigue makes it hard to plan or be consistent.",
        "tags": ["Fatigue", "Pain Management", "Independence", "Work-life balance"],
        "context": "Works part-time and lives with a partner",
        "goals": "Stay active, maintain independence",
        "frustrations": "Unpredictable fatigue, limited energy",
        "tech_support": "Medium",
        "data_bronnen": ["ReumaNederland Interviews n=65", "Patiëntforum data", "Wetenschappelijke literatuur"],
        "sleutelfactoren": ["Diagnose", "Leefstijl", "Emotionele impact"],
        "xai_uitleg": "Gegenereerd op basis van patronen in de dataset. Fatigue wordt vaak als uitdaging genoemd",
        "kwaliteit": "goed",
    },
    {
        "id": 2,
        "initials": "AJ",
        "naam": "Alex Johnson",
        "leeftijd": 18,
        "leeftijd_label": "18jr",
        "geslacht": "Vrouw",
        "diagnose": "Juveniele artritis",
        "quote": "School en sport zijn mijn leven. De pijn maakt dat moeilijk, maar ik geef niet op.",
        "tags": ["Jong", "School", "Sport", "Vriendschappen"],
        "context": "Scholier, woont bij ouders",
        "goals": "Normaal leven leiden, studie afmaken",
        "frustrations": "Niet begrepen worden, missen van activiteiten",
        "tech_support": "Hoog",
        "data_bronnen": ["ReumaNederland Interviews n=65", "Jongerenonderzoek"],
        "sleutelfactoren": ["Leeftijd", "Sociale context"],
        "xai_uitleg": "Jong persona met focus op sociale inclusie en schoolprestaties.",
        "kwaliteit": "goed",
    },
    {
        "id": 3,
        "initials": "AJ",
        "naam": "Alex Johnson",
        "leeftijd": 23,
        "leeftijd_label": "23jr",
        "geslacht": "Man",
        "diagnose": "Artritis psoriatica",
        "quote": "Ik wil werken en carrière maken, maar de ziekte gooit roet in het eten.",
        "tags": ["Werk", "Carrière", "Jonge professional", "Zelfstandig"],
        "context": "Starter op de arbeidsmarkt, eigen appartement",
        "goals": "Carrière opbouwen, onafhankelijk zijn",
        "frustrations": "Werkgever begrijpt het niet, energiegebrek",
        "tech_support": "Hoog",
        "data_bronnen": ["ReumaNederland survey 2024", "Arbeidsmarktonderzoek"],
        "sleutelfactoren": ["Werkdruk", "Leefstijl"],
        "xai_uitleg": "Jonge werkende met focus op professionele ontwikkeling.",
        "kwaliteit": "goed",
    },
    {
        "id": 4,
        "initials": "AJ",
        "naam": "Alex Johnson",
        "leeftijd": 34,
        "leeftijd_label": "34jr",
        "geslacht": "Vrouw",
        "diagnose": "Reumatoïde artritis",
        "quote": "Met twee kinderen en een baan is er weinig ruimte voor ziekte. Ik moet vooruit.",
        "tags": ["Moeder", "Werk", "Gezin", "Multitasking"],
        "context": "Parttime werkend, twee jonge kinderen",
        "goals": "Goede moeder zijn, gezin draaiende houden",
        "frustrations": "Vermoeidheid bij gezinstaken, schuldgevoel",
        "tech_support": "Gemiddeld",
        "data_bronnen": ["ReumaNederland Interviews n=65", "Gezinsonderzoek"],
        "sleutelfactoren": ["Gezinscontext", "Werkdruk", "Vermoeidheid"],
        "xai_uitleg": "Persona gericht op het combineren van zorg en werk.",
        "kwaliteit": "goed",
    },
]

PROJECTS = [
    {"id": 1, "naam": "Project 1", "personas": 2, "rating": 71, "exports": 3},
    {"id": 2, "naam": "ReumaNederland", "personas": 4, "rating": 82, "exports": 10},
    {"id": 3, "naam": "Project 3", "personas": 1, "rating": 65, "exports": 1},
]

DATASETS = [
    {
        "id": 1,
        "naam": "Dataset_ReumaNederland",
        "bronnen": ["ReumaNederland Interviews n=65", "ReumaNederland Enquêtes n=482", "Reuma Patiëntforum data"],
    },
    {"id": 2, "naam": "Dataset_ReumaNederland", "bronnen": []},
    {"id": 3, "naam": "Dataset_ReumaNederland", "bronnen": []},
    {"id": 4, "naam": "Dataset_ReumaNederland", "bronnen": []},
]


# ─────────────────────────────────────────────
# SCORE & BADGE HELPERS
# ─────────────────────────────────────────────
def score_kleur(score: int) -> str:
    if score >= 75:
        return "#1DB87A"
    elif score >= 50:
        return "#F59E0B"
    return "#EF4444"

def score_label(score: int) -> str:
    if score >= 75:
        return "Low"
    elif score >= 50:
        return "Medium"
    return "High"

def badge_class(score: int) -> str:
    if score >= 75:
        return "rel-green"
    elif score >= 50:
        return "rel-amber"
    return "rel-red"

def badge_icon(score: int) -> str:
    if score >= 75:
        return "✓"
    elif score >= 50:
        return "⚠"
    return "✗"

def score_ring_svg(score: int, size: int = 100) -> str:
    r = size * 0.42
    cx = cy = size / 2
    circ = 2 * math.pi * r
    offset = circ * (1 - score / 100)
    kleur = score_kleur(score)
    fs = size * 0.18
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1C2A40" stroke-width="{size*0.09}"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{kleur}" stroke-width="{size*0.09}"
              stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
              stroke-linecap="round" transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy + fs*0.38}" text-anchor="middle" font-size="{fs}"
            font-weight="700" fill="#F1F5F9" font-family="DM Sans,sans-serif">{score}%</text>
    </svg>"""


# ─────────────────────────────────────────────
# PERSONA KAART HTML (in chat)
# ─────────────────────────────────────────────
def render_persona_card(p: dict) -> str:
    tags = "".join([f'<span class="pc-tag">{t}</span>' for t in p["tags"]])
    return f"""
    <div class="pc-card">
      <div class="pc-header">
        <img class="pc-photo" src="https://i.pravatar.cc/100?u={p['id']}" alt="{p['naam']}"
             onerror="this.style.background='#253047';this.src=''">
        <div class="pc-main">
          <div class="pc-name">{p['naam']}</div>
          <div class="pc-diag">{p['geslacht']} · {p['diagnose']}</div>
          <div class="pc-quote">"{p['quote']}"</div>
          <div class="pc-tags">{tags}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;flex-shrink:0">
          <div class="pc-age">{p['leeftijd']} yrs</div>
          <button class="view-full-btn">View full Persona &gt;</button>
        </div>
      </div>
      <div class="pc-details">
        <div class="pc-det-row">
          <span class="pc-det-icon">📋</span>
          <span class="pc-det-label">Context</span>
          <span class="pc-det-val">{p['context']}</span>
        </div>
        <div class="pc-det-row">
          <span class="pc-det-icon">🎯</span>
          <span class="pc-det-label">Goals</span>
          <span class="pc-det-val">{p['goals']}</span>
        </div>
        <div class="pc-det-row">
          <span class="pc-det-icon">⚡</span>
          <span class="pc-det-label">Frustrations</span>
          <span class="pc-det-val">{p['frustrations']}</span>
        </div>
        <div class="pc-det-row">
          <span class="pc-det-icon">💻</span>
          <span class="pc-det-label">Tech Support</span>
          <span class="pc-det-val">{p['tech_support']}</span>
        </div>
      </div>
    </div>"""


def render_xai_box(p: dict) -> str:
    bronnen = "".join([f'<div class="xai-source">{b}</div>' for b in p["data_bronnen"]])
    factoren = "".join([f'<span class="xai-badge">{f}</span>' for f in p["sleutelfactoren"]])
    return f"""
    <div class="xai-box">
      <div class="xai-title">
        ▼ Why was this created this way?
        <span class="xai-accent">(Explainable AI)</span>
        <span style="font-size:13px;color:#5a7090;margin-left:2px">ⓘ</span>
      </div>
      <div class="xai-grid">
        <div>
          <div class="xai-col-label">Top data sources</div>
          {bronnen}
        </div>
        <div>
          <div class="xai-col-label">Key factors used</div>
          {factoren}
        </div>
        <div>
          <div class="xai-col-label">Explanation</div>
          <div class="xai-expl">{p['xai_uitleg']}</div>
          <div class="xai-feedback">
            <span class="xai-fb-label">Was this useful?</span>
            <button class="feedback-btn">👎</button>
            <button class="feedback-btn">👍</button>
          </div>
        </div>
      </div>
    </div>"""


# ─────────────────────────────────────────────
# GROQ API CALL
# ─────────────────────────────────────────────
def bouw_systeem_prompt(p: dict) -> str:
    return f"""Je bent een cognitieve synthetic user agent genaamd "{p['naam']}".

PERSONA PROFIEL:
- Naam: {p['naam']}
- Leeftijd: {p['leeftijd']} jaar
- Geslacht: {p['geslacht']}
- Diagnose: {p['diagnose']}
- Kernquote: "{p['quote']}"
- Dagelijkse context: {p['context']}
- Doelen: {p['goals']}
- Frustraties: {p['frustrations']}
- Tech-comfort: {p['tech_support']}
- Kernthema's: {", ".join(p['tags'])}

GEDRAGSREGELS:
1. Spreek ALTIJD in de eerste persoon als {p['naam']}
2. Reageer authentiek vanuit dit persona — niet als AI
3. Noem specifieke ervaringen passend bij de aandoening
4. Wees eerlijk over frustraties
5. Houd antwoorden beknopt (2-4 zinnen) tenzij anders gevraagd
6. Gebruik het taalregister passend bij dit persona

VERPLICHT NA ELK ANTWOORD — voeg op een aparte laatste regel exact toe:
SCORES:{{"bias": <0-100>, "hallucinaties": <0-100>, "inclusie": <0-100>}}
(100 = geen probleem; bias = vrijheid van stereotypen; hallucinaties = feitelijke gronding; inclusie = representativiteit)
Voorbeeld: SCORES:{{"bias": 88, "hallucinaties": 75, "inclusie": 82}}
"""


def vraag_groq(client, persona: dict, vraag: str, geschiedenis: list) -> dict:
    systeem = bouw_systeem_prompt(persona)
    berichten = [{"role": "system", "content": systeem}]
    for msg in geschiedenis[-16:]:
        berichten.append(msg)
    berichten.append({"role": "user", "content": vraag})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=berichten,
            temperature=0.75,
            max_tokens=600,
        )
        volledig = response.choices[0].message.content.strip()

        scores = {"bias": 75, "hallucinaties": 60, "inclusie": 70}
        match = re.search(r'SCORES:\s*(\{[^}]+\})', volledig)
        if match:
            try:
                parsed = json.loads(match.group(1))
                for k in ["bias", "hallucinaties", "inclusie"]:
                    if k in parsed and isinstance(parsed[k], (int, float)):
                        scores[k] = int(parsed[k])
            except Exception:
                pass

        schoon = re.sub(r'\nSCORES:\s*\{[^}]+\}', '', volledig).strip()
        schoon = re.sub(r'SCORES:\s*\{[^}]+\}', '', schoon).strip()
        # Verwijder eventuele resterende accolades die HTML kunnen breken
        schoon = schoon.replace("{", "&#123;").replace("}", "&#125;")
        totaal = round((scores["bias"] + scores["hallucinaties"] + scores["inclusie"]) / 3)

        return {"tekst": schoon, "scores": {**scores, "totaal": totaal}, "succes": True}

    except Exception as e:
        return {
            "tekst": f"❌ Groq API fout: {str(e)}",
            "scores": {"bias": 0, "hallucinaties": 0, "inclusie": 0, "totaal": 0},
            "succes": False,
        }


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "actieve_persona_id": 1,
    "actief_project_id": 2,
    "actief_dataset_id": 1,
    "chatgeschiedenis": [],
    "api_berichten": [],
    "scores": {"bias": 83, "hallucinaties": 73, "inclusie": 77, "totaal": 76},
    "berichtentelling": 0,
    "sidebar_mode": "personas",  # personas | persona_detail | datasets | projects
    "panel_mode": None,           # None | validation | full_report | visualisatie
    "mood_opties": {"Curious": True, "Confused": False, "Distrust": True, "Frustrated": False, "Hopeful": False, "Overstimulated": False},
    "assign_opties": {"Designer 1": True, "Designer 2": False, "Designer 3": True, "Developer 1": False, "Developer 2": False, "Researcher 1": False},
    "mood_open": False,
    "assign_open": False,
    "persona_kaart_getoond": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def get_actieve_persona():
    return next(p for p in PERSONAS if p["id"] == st.session_state.actieve_persona_id)


def wissel_persona(pid: int):
    if pid != st.session_state.actieve_persona_id:
        st.session_state.actieve_persona_id = pid
        st.session_state.chatgeschiedenis = []
        st.session_state.api_berichten = []
        st.session_state.berichtentelling = 0
        st.session_state.persona_kaart_getoond = False
        st.session_state.scores = {"bias": 83, "hallucinaties": 73, "inclusie": 77, "totaal": 76}


def reset_chat():
    st.session_state.chatgeschiedenis = []
    st.session_state.api_berichten = []
    st.session_state.berichtentelling = 0
    st.session_state.persona_kaart_getoond = False
    st.session_state.scores = {"bias": 83, "hallucinaties": 73, "inclusie": 77, "totaal": 76}


# ─────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────
actieve_p = get_actieve_persona()
scores = st.session_state.scores

# CSS: trek de eerste horizontale Streamlit-kolomrij omhoog in de topbar
st.markdown("""
<style>
/* ── Topbar HTML ── */
.topbar {
    background: #111827;
    border-bottom: 1px solid #1C2A40;
    padding: 0 24px;
    height: 56px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: relative;
    z-index: 10;
    pointer-events: none;  /* knoppen erin zijn HTML, Streamlit knoppen zitten erover */
}
.topbar-left {
    display: flex;
    align-items: center;
    gap: 14px;
    pointer-events: auto;
}

/* Trek de Streamlit knoppenrij (eerste stHorizontalBlock na topbar)
   omhoog zodat ze visueel in de topbar vallen */
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type {
    background: #111827 !important;
    border-bottom: 1px solid #1C2A40 !important;
    margin-top: -56px !important;
    padding: 0 24px 0 0 !important;
    height: 56px !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 8px !important;
    position: relative !important;
    z-index: 20 !important;
}

/* Verberg de lege spacer kolom visueel */
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type
> div[data-testid="column"]:first-child {
    flex: 0 0 0 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
}

/* Topbar Streamlit knoppen styling */
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type button {
    background: #111827 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    color: #8B9CB8 !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 6px 13px !important;
    height: 34px !important;
    white-space: nowrap !important;
    font-weight: 400 !important;
    transition: all 0.15s !important;
}
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
    border-color: #3B7EF6 !important;
    color: #F1F5F9 !important;
}
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
    background: #3B7EF6 !important;
    border-color: #3B7EF6 !important;
    color: white !important;
    font-weight: 600 !important;
}
div[data-testid="stMainBlockContainer"] > div > div > div[data-testid="stVerticalBlock"]
> div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"]:hover {
    background: #5B9BFF !important;
    border-color: #5B9BFF !important;
}
</style>
""", unsafe_allow_html=True)

# HTML topbar — alleen logo + projectnaam (geen knoppen)
mood_arrow = "∧" if st.session_state.mood_open else "∨"
assign_arrow = "∧" if st.session_state.assign_open else "∨"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="tb-logo-icon">
      <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
        <rect width="28" height="28" rx="6" fill="#1a4fa0"/>
        <path d="M5 8h18M5 12h14M5 16h18M5 20h14" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
      </svg>
    </div>
    <span class="tb-logo-text">Data Justice Assistent</span>
    <div class="tb-divider"></div>
    <div class="tb-project-wrap">
      <div class="tb-project-name">ReumaNederland Project</div>
      <div class="tb-project-sub">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
          <ellipse cx="12" cy="5" rx="9" ry="3" stroke="#5a7090" stroke-width="1.5"/>
          <path d="M3 5v14c0 1.657 4.03 3 9 3s9-1.343 9-3V5" stroke="#5a7090" stroke-width="1.5"/>
          <path d="M3 12c0 1.657 4.03 3 9 3s9-1.343 9-3" stroke="#5a7090" stroke-width="1.5"/>
        </svg>
        ReumaNederland · Team 3
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Streamlit knoppen — worden via CSS omhoog getrokken in de topbar
_spacer, _col_mood, _col_assign, _col_export = st.columns([4.5, 1.3, 1.3, 0.7])
with _col_mood:
    if st.button(f"😊 Mood checker {mood_arrow}", key="tb_mood"):
        st.session_state.mood_open = not st.session_state.mood_open
        st.session_state.assign_open = False
        st.rerun()
with _col_assign:
    if st.button(f"📋 Assign project {assign_arrow}", key="tb_assign"):
        st.session_state.assign_open = not st.session_state.assign_open
        st.session_state.mood_open = False
        st.rerun()
with _col_export:
    if st.button("↑ Export", key="tb_export", type="primary"):
        export_data = {
            "project": "ReumaNederland",
            "persona": {"naam": actieve_p["naam"], "leeftijd": actieve_p["leeftijd"], "diagnose": actieve_p["diagnose"]},
            "scores": st.session_state.scores,
            "chatgeschiedenis": [{"rol": m["rol"], "inhoud": m["inhoud"]} for m in st.session_state.chatgeschiedenis],
        }
        st.download_button(
            "⬇ Download JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"data_justice_{actieve_p['naam'].replace(' ', '_')}.json",
            mime="application/json",
            key="tb_download",
        )

# Mood checker dropdown
if st.session_state.mood_open:
    with st.container():
        st.markdown("""<div style="background:#1a2438;border:1px solid #253047;border-radius:10px;
            padding:10px 16px 12px;margin-bottom:8px;">
          <div style="font-size:11px;font-weight:600;color:#8B9CB8;margin-bottom:8px;
                      text-transform:uppercase;letter-spacing:.5px">😊 Mood selectie</div></div>""",
            unsafe_allow_html=True)
        mood_cols = st.columns(6)
        for i, (mood, checked) in enumerate(st.session_state.mood_opties.items()):
            with mood_cols[i]:
                new_val = st.checkbox(mood, value=checked, key=f"mood_{mood}")
                st.session_state.mood_opties[mood] = new_val

# Assign project dropdown
if st.session_state.assign_open:
    with st.container():
        st.markdown("""<div style="background:#1a2438;border:1px solid #253047;border-radius:10px;
            padding:10px 16px 12px;margin-bottom:8px;">
          <div style="font-size:11px;font-weight:600;color:#8B9CB8;margin-bottom:8px;
                      text-transform:uppercase;letter-spacing:.5px">📋 Team toewijzing</div></div>""",
            unsafe_allow_html=True)
        assign_cols = st.columns(6)
        for i, (name, checked) in enumerate(st.session_state.assign_opties.items()):
            with assign_cols[i]:
                new_val = st.checkbox(name, value=checked, key=f"assign_{name}")
                st.session_state.assign_opties[name] = new_val


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    # Groq status
    # Groq verbindingsstatus tonen
    if client:
        st.markdown('<span style="color:#1DB87A;font-size:11px">✓ Groq verbonden (llama-3.3-70b)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#EF4444;font-size:11px">⚠ Voeg GROQ_API_KEY toe aan secrets.toml</span>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # New Chat button
    if st.button("+ New Chat", key="new_chat", use_container_width=True):
        reset_chat()
        st.session_state.sidebar_mode = "personas"
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Sidebar mode: PERSONAS (default) ──
    if st.session_state.sidebar_mode in ("personas", "persona_detail"):

        st.markdown('<div class="sb-section-title">Persona\'s</div><span class="sb-section-sub">Research</span>', unsafe_allow_html=True)

        for p in PERSONAS:
            is_actief = p["id"] == st.session_state.actieve_persona_id
            is_open = is_actief and st.session_state.sidebar_mode == "persona_detail"
            avatar_class = "sb-persona-avatar sb-persona-avatar-active" if is_actief else "sb-persona-avatar"
            item_class = "sb-persona-item active" if is_actief else "sb-persona-item"
            age_class = "sb-persona-age sb-persona-age-active" if is_actief else "sb-persona-age"

            col_main, col_arr = st.columns([10, 1])
            with col_main:
                st.markdown(f"""
                <div class="{item_class}">
                  <div class="{avatar_class}">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="7" r="4" stroke="{'#5B9BFF' if is_actief else '#5a7090'}" stroke-width="1.5"/>
                      <path d="M4 21c0-4.418 3.582-8 8-8s8 3.582 8 8"
                            stroke="{'#5B9BFF' if is_actief else '#5a7090'}" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                  </div>
                  <div style="flex:1;min-width:0">
                    <div class="sb-persona-name">{p['naam']}</div>
                    <div class="sb-persona-meta">{p['diagnose'][:24]}…</div>
                  </div>
                  <div class="{age_class}">{p['leeftijd_label']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_arr:
                pijl = "▼" if is_open else ("▷" if is_actief else "▷")
                if st.button(pijl, key=f"sel_persona_{p['id']}", help=f"Selecteer {p['naam']}"):
                    if not is_actief:
                        # Wissel naar andere persona, sluit detail
                        wissel_persona(p["id"])
                        st.session_state.sidebar_mode = "personas"
                    else:
                        # Toggle detail van actieve persona
                        st.session_state.sidebar_mode = "personas" if is_open else "persona_detail"
                    st.rerun()

            # Toon uitklapkaart DIRECT onder deze persona als die actief + open is
            if is_open:
                tags_html = "".join([f'<span class="sb-persona-exp-tag">{t}</span>' for t in p["tags"]])
                st.markdown(f"""
                <div class="sb-persona-expanded">
                  <div class="sb-persona-exp-header">
                    <img class="sb-persona-exp-photo" src="https://i.pravatar.cc/80?u={p['id']}"
                         alt="{p['naam']}" onerror="this.style.background='#253047';this.src=''">
                    <div>
                      <div class="sb-persona-exp-name">{p['naam']}
                        <span style="font-size:10px;color:#5a7090;margin-left:4px">✎</span>
                      </div>
                      <div class="sb-persona-exp-diag">🔴 {p['diagnose']}</div>
                    </div>
                  </div>
                  <div class="sb-persona-exp-goals">
                    <span style="color:#8B9CB8;font-size:10px">🎯 {p['goals'][:20]}</span>
                    <span style="color:#8B9CB8;font-size:10px;margin-left:8px">💻 {p['tech_support']}</span>
                  </div>
                  <div class="sb-persona-exp-tags">{tags_html}</div>
                  <div class="sb-persona-exp-quote">"{p['quote']}"</div>
                </div>
                """, unsafe_allow_html=True)
                col_save, col_regen = st.columns(2)
                with col_save:
                    st.button("Save Persona's", key=f"save_persona_{p['id']}", use_container_width=True)
                with col_regen:
                    if st.button("(Re)Generate", key=f"regen_persona_{p['id']}", use_container_width=True):
                        st.session_state.sidebar_mode = "personas"
                        st.rerun()

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
        col_edit, col_gen = st.columns(2)
        with col_edit:
            if st.button("Edit Persona's", key="edit_personas", use_container_width=True):
                st.session_state.sidebar_mode = "persona_detail"
                st.rerun()
        with col_gen:
            st.button("Generate Persona's", key="gen_personas", use_container_width=True)

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-title">Dataset</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-dataset-item">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <ellipse cx="12" cy="5" rx="9" ry="3" stroke="#5a7090" stroke-width="1.5"/>
            <path d="M3 5v14c0 1.657 4.03 3 9 3s9-1.343 9-3V5" stroke="#5a7090" stroke-width="1.5"/>
            <path d="M3 12c0 1.657 4.03 3 9 3s9-1.343 9-3" stroke="#5a7090" stroke-width="1.5"/>
          </svg>
          Dataset_ReumaNederland
        </div>
        """, unsafe_allow_html=True)
        if st.button("Edit Dataset", key="edit_dataset", use_container_width=True):
            st.session_state.sidebar_mode = "datasets"
            st.rerun()

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # Projects sectie
        st.markdown('<div class="sb-section-title">Projects</div>', unsafe_allow_html=True)
        for proj in PROJECTS:
            is_active = proj["id"] == st.session_state.actief_project_id
            cls = "sb-project-item active" if is_active else "sb-project-item"
            st.markdown(f"""
            <div class="{cls}">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="{'#F1F5F9' if is_active else '#5a7090'}" stroke-width="1.5"/>
                <path d="M9 9h6M9 12h6M9 15h4" stroke="{'#F1F5F9' if is_active else '#5a7090'}" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              {proj['naam']}
            </div>
            """, unsafe_allow_html=True)
            if st.button(proj["naam"], key=f"proj_{proj['id']}", help=f"Selecteer {proj['naam']}"):
                st.session_state.actief_project_id = proj["id"]
                st.rerun()

        st.markdown('<div class="sb-view-all">View all projects &gt;&gt;</div>', unsafe_allow_html=True)

    # ── Sidebar mode: DATASETS (screen 6) ──
    elif st.session_state.sidebar_mode == "datasets":
        st.markdown('<div class="sb-section-title">Dataset</div>'
                    '<span class="sb-section-sub">Project ReumaNederland</span>', unsafe_allow_html=True)

        for ds in DATASETS:
            is_active = ds["id"] == st.session_state.actief_dataset_id
            st.markdown(f"""
            <div style="background:{'#1a2438' if is_active else 'transparent'};border:1px solid {'#253047' if is_active else '#1C2A40'};
                        border-radius:9px;padding:10px 12px;margin-bottom:6px;cursor:pointer">
              <div style="display:flex;align-items:center;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#F1F5F9">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                    <ellipse cx="12" cy="5" rx="9" ry="3" stroke="#5a7090" stroke-width="1.5"/>
                    <path d="M3 5v14c0 1.657 4.03 3 9 3s9-1.343 9-3V5" stroke="#5a7090" stroke-width="1.5"/>
                    <path d="M3 12c0 1.657 4.03 3 9 3s9-1.343 9-3" stroke="#5a7090" stroke-width="1.5"/>
                  </svg>
                  {ds['naam']}
                </div>
                <div style="width:18px;height:18px;border-radius:3px;background:{'#3B7EF6' if is_active else 'transparent'};
                            border:1px solid #253047;display:flex;align-items:center;justify-content:center">
                  {'<span style="color:white;font-size:11px">✓</span>' if is_active else ''}
                </div>
              </div>
              {''.join([f"<div style='font-size:10px;color:#8B9CB8;margin-top:4px;padding-left:21px'>• {b}</div>" for b in ds['bronnen']]) if is_active else ''}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select dataset {ds['id']}", key=f"ds_{ds['id']}", help=ds["naam"]):
                st.session_state.actief_dataset_id = ds["id"]
                st.rerun()

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
        col_sv, col_ch = st.columns(2)
        with col_sv:
            if st.button("Save Dataset", key="save_ds", use_container_width=True):
                st.session_state.sidebar_mode = "personas"
                st.rerun()
        with col_ch:
            st.button("Check Dataset", key="check_ds", use_container_width=True)

    # ── Sidebar mode: PROJECTS (screen 7) ──
    elif st.session_state.sidebar_mode == "projects":
        st.markdown('<div class="sb-section-title">Projects</div>'
                    '<span class="sb-section-sub">Project ReumaNederland</span>', unsafe_allow_html=True)

        for proj in PROJECTS:
            is_active = proj["id"] == st.session_state.actief_project_id
            st.markdown(f"""
            <div style="background:{'#1a2438' if is_active else 'transparent'};border:1px solid {'#253047' if is_active else '#1C2A40'};
                        border-radius:9px;padding:10px 12px;margin-bottom:6px">
              <div style="display:flex;align-items:center;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#F1F5F9">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="{'#F1F5F9' if is_active else '#5a7090'}" stroke-width="1.5"/>
                    <path d="M9 9h6M9 12h6M9 15h4" stroke="{'#F1F5F9' if is_active else '#5a7090'}" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  {proj['naam']}
                </div>
                <div style="width:18px;height:18px;border-radius:50%;background:{'#3B7EF6' if is_active else '#1C2A40'};
                            border:1px solid {'#3B7EF6' if is_active else '#253047'};display:flex;align-items:center;justify-content:center">
                  {'<span style="color:white;font-size:10px">✓</span>' if is_active else ''}
                </div>
              </div>
              {f"""<div style='font-size:10px;color:#8B9CB8;margin-top:5px;padding-left:21px'>
                • {proj['personas']} Persona's<br>• Average rating {proj['rating']}%<br>• Exported {proj['exports']} times by team 2
              </div>""" if is_active else ''}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {proj['naam']}", key=f"proj_sel_{proj['id']}", help=proj["naam"]):
                st.session_state.actief_project_id = proj["id"]
                st.rerun()

        # Nieuw project button
        st.markdown("""
        <div style="border:1px dashed #253047;border-radius:9px;padding:10px;
                    text-align:center;font-size:20px;color:#253047;cursor:pointer;margin-top:4px">+</div>
        """, unsafe_allow_html=True)
        if st.button("+ Nieuw project", key="new_proj", use_container_width=True):
            pass

    # Sidebar footer (altijd)
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-footer">
      <div class="sb-designer-avatar">DS</div>
      <div>
        <div class="sb-designer-name">Designer</div>
        <div class="sb-designer-role">Greenberry</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────
# Bepaal of rechter validatie-panel open is
panel_open = st.session_state.panel_mode is not None

if panel_open:
    chat_col, panel_col = st.columns([2, 1])
else:
    chat_col = st.container()
    panel_col = None


# ── CHAT COLUMN ──
with (chat_col if panel_open else st.container()):

    # Chat achtergrond wrapper open
    st.markdown("""
    <div id="chat-scroll" style="min-height:400px;padding:20px 24px 8px;
        background:
          radial-gradient(ellipse at 75% 30%, rgba(26,79,160,0.18) 0%, transparent 55%),
          radial-gradient(ellipse at 90% 80%, rgba(59,126,246,0.08) 0%, transparent 40%),
          #0B1220;">
    """, unsafe_allow_html=True)

    # Welkomstbericht
    if not st.session_state.chatgeschiedenis:
        st.markdown(f"""
        <div class="chat-ts">Nu</div>
        <div class="msg-bot-wrap">
          <div class="msg-sender">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="18" height="14" rx="3" stroke="#5B9BFF" stroke-width="1.5"/>
              <path d="M8 17v4M16 17v4M6 21h12" stroke="#5B9BFF" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            Data Justice Assistent
          </div>
          <div class="bubble-bot">
            Hallo! Ik ben de <strong>Data Justice Assistent</strong>.<br><br>
            Actieve synthetic user: <strong>{actieve_p['naam']}</strong>
            ({actieve_p['leeftijd']}jr, {actieve_p['diagnose']}).<br><br>
            Stel een vraag om de conversatie te starten. Elk antwoord wordt geëvalueerd op
            <strong>bias</strong>, <strong>hallucinaties</strong> en <strong>inclusie</strong>.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        vorig_ts = None
        for msg in st.session_state.chatgeschiedenis:
            ts = msg.get("tijd", "")
            if ts != vorig_ts:
                st.markdown(f'<div class="chat-ts">{ts}</div>', unsafe_allow_html=True)
                vorig_ts = ts

            if msg["rol"] == "gebruiker":
                # Inhoud veilig escapen voor HTML
                inhoud = str(msg["inhoud"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(f"""
                <div class="msg-user-wrap">
                  <div style="display:flex;align-items:flex-end;gap:8px;justify-content:flex-end">
                    <div class="bubble-user">{inhoud}</div>
                    <div class="user-avatar">DS</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            elif msg["rol"] == "assistent":
                inhoud = str(msg["inhoud"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                sub = '<div class="msg-sender-sub">Here is your Persona based on the dataset: Reuma_Nederland</div>' if msg.get("toon_persona_kaart") else ""
                st.markdown(f"""
                <div class="msg-bot-wrap">
                  <div class="msg-sender">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                      <rect x="3" y="3" width="18" height="14" rx="3" stroke="#5B9BFF" stroke-width="1.5"/>
                      <path d="M8 17v4M16 17v4M6 21h12" stroke="#5B9BFF" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                    Synthetic User · {actieve_p['naam']}
                  </div>
                  {sub}
                  <div class="bubble-bot">{inhoud}</div>
                </div>
                """, unsafe_allow_html=True)
                if msg.get("toon_persona_kaart"):
                    st.markdown(render_persona_card(actieve_p), unsafe_allow_html=True)
                    st.markdown(render_xai_box(actieve_p), unsafe_allow_html=True)

            elif msg["rol"] == "systeem":
                inhoud = str(msg["inhoud"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(f"""
                <div class="msg-bot-wrap">
                  <div class="msg-sender">⚖️ Data Justice Assistent</div>
                  <div class="bubble-bot">{inhoud}</div>
                </div>
                """, unsafe_allow_html=True)

    # Chat wrapper sluiten
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input (boven reliability bar) ──
    st.markdown("""
    <div style="padding:10px 0 0 0">
      <div style="font-size:11px;color:#5a7090;padding:0 0 4px 0">Ask the Synthetic User</div>
    </div>
    """, unsafe_allow_html=True)

    input_c1, input_c2, input_c3 = st.columns([0.04, 1, 0.12])
    with input_c1:
        st.markdown('<div style="font-size:22px;color:#3B7EF6;padding-top:8px;text-align:center">✦</div>', unsafe_allow_html=True)
    with input_c2:
        user_input = st.text_input(
            "vraag",
            placeholder="Ask the Synthetic User...",
            label_visibility="collapsed",
            key="chat_input_field",
        )
    with input_c3:
        send_clicked = st.button("➤ Send", key="send_btn", type="primary", use_container_width=True)

    # ── Reliability bar (onder input) ──
    b_score = scores["bias"]
    h_score = scores["hallucinaties"]
    i_score = scores["inclusie"]

    h_lbl = f"Hallucination — {'Low' if h_score >= 75 else 'Medium' if h_score >= 50 else 'High'}"
    b_lbl = f"Bias — {'Low' if b_score >= 75 else 'Medium' if b_score >= 50 else 'High'}"
    i_lbl = f"Data Justice — {'Needs Review' if i_score < 75 else 'Good'}"

    st.markdown(f"""
    <div class="rel-bar">
      <span class="rel-label">ⓘ Reliability :</span>
      <span class="rel-badge {badge_class(h_score)}">{badge_icon(h_score)} {h_lbl}</span>
      <span class="rel-badge {badge_class(b_score)}">{badge_icon(b_score)} {b_lbl}</span>
      <span class="rel-badge {badge_class(i_score)}">{badge_icon(i_score)} {i_lbl}</span>
    </div>
    """, unsafe_allow_html=True)

    # "View Full Report >>" als Streamlit knop rechts uitgelijnd → opent validation panel
    _rel_spacer, _rel_vfr = st.columns([4, 1])
    with _rel_vfr:
        if st.button("📊 View Full Report >>", key="btn_view_full_report"):
            st.session_state.panel_mode = "validation" if st.session_state.panel_mode != "validation" else None
            st.rerun()

    # Score detail expander
    if st.session_state.berichtentelling > 0:
        with st.expander("📈 Score detail — laatste evaluatie", expanded=False):
            sc1, sc2, sc3, sc4 = st.columns(4)
            for col, val, naam, beschr in [
                (sc1, scores["bias"], "Bias", "Stereotypering"),
                (sc2, scores["hallucinaties"], "Hallucinaties", "Feitelijkheid"),
                (sc3, scores["inclusie"], "Inclusie", "Representativiteit"),
                (sc4, scores["totaal"], "Totaal", "Gecombineerd"),
            ]:
                with col:
                    kleur = score_kleur(val)
                    st.markdown(f"""
                    <div class="metric-card">
                      <div class="metric-val" style="color:{kleur}">{val}%</div>
                      <div class="metric-lbl">{naam}</div>
                      <div style="font-size:9px;color:#8B9CB8;margin-top:2px">{beschr}</div>
                    </div>
                    """, unsafe_allow_html=True)

        if st.button("📥 Download gesprek (JSON)", key="dl_chat"):
            export = {
                "project": "ReumaNederland",
                "persona": {"naam": actieve_p["naam"], "leeftijd": actieve_p["leeftijd"], "diagnose": actieve_p["diagnose"]},
                "scores": st.session_state.scores,
                "chatgeschiedenis": [{"rol": m["rol"], "inhoud": m["inhoud"]} for m in st.session_state.chatgeschiedenis],
            }
            st.download_button(
                label="⬇ Download",
                data=json.dumps(export, indent=2, ensure_ascii=False),
                file_name=f"data_justice_{actieve_p['naam'].replace(' ', '_')}.json",
                mime="application/json",
                key="dl_chat_btn",
            )


# ── VALIDATION / REPORT PANEL (screen 9, 10, 11) ──
if panel_open and panel_col is not None:
    with panel_col:

        if st.session_state.panel_mode == "validation":
            # Screen 9: Validation & Risk overview
            totaal = scores["totaal"]
            st.markdown(f"""
            <div class="val-panel">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                <span class="val-panel-title">Validation &amp; Risk overview</span>
                <button class="panel-close" onclick="">✕</button>
              </div>
              <div class="val-check-row">
                <span class="val-check-label">Bias check</span>
                <span class="val-check-ok">Details &gt;&gt;</span>
              </div>
              <div class="val-check-row">
                <span class="val-check-label">Hallucination check</span>
                <span class="val-check-warn">Needs review &gt;&gt;</span>
              </div>
              <div class="val-check-row">
                <span class="val-check-label">Data Justice check</span>
                <span class="val-check-med">Medium Risk &gt;&gt;</span>
              </div>
              <div class="score-ring-wrap">
                {score_ring_svg(totaal, 90)}
                <div class="score-legend">
                  <div class="score-legend-good">Good</div>
                  <div class="score-legend-improve">Room for improvement</div>
                  <div class="score-legend-link">Details &gt;&gt;</div>
                </div>
              </div>
              <div class="improve-title">Improve AI input</div>
              <div class="improve-row">
                <span><span class="improve-icon">📋</span><span class="improve-label">Add more context</span></span>
                <span class="improve-action">Improve relevance</span>
              </div>
              <div class="improve-row">
                <span><span class="improve-icon">🔑</span><span class="improve-label">Refine Prompt</span></span>
                <span class="improve-action">Get better results</span>
              </div>
              <div class="improve-row">
                <span><span class="improve-icon">📋</span><span class="improve-label">Review data quality</span></span>
                <span class="improve-action">Check dataset</span>
              </div>
              <div class="improve-row" style="border-bottom:none">
                <span><span class="improve-icon">⚠</span><span class="improve-label">Report an issue</span></span>
                <span class="improve-action">Help us improve</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            close_c, export_c = st.columns(2)
            with close_c:
                if st.button("Fix issues %", key="fix_issues", use_container_width=True):
                    pass
            with export_c:
                if st.button("Export report", key="exp_report_val", use_container_width=True, type="primary"):
                    st.session_state.panel_mode = "full_report"
                    st.rerun()
            if st.button("✕ Sluit panel", key="close_val", use_container_width=True):
                st.session_state.panel_mode = None
                st.rerun()

        elif st.session_state.panel_mode == "full_report":
            # Screen 10: Full report met progress bars
            h = scores["hallucinaties"]
            b = scores["bias"]
            i = scores["inclusie"]

            def fr_bar(pct, kleur):
                return f'<div class="fr-bar-bg"><div class="fr-bar-fill" style="width:{pct}%;background:{kleur}"></div></div>'

            st.markdown(f"""
            <div class="val-panel">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                <span class="val-panel-title">Full report</span>
                <button class="panel-close">✕</button>
              </div>

              <div class="fr-section">
                <div class="fr-cat-title">
                  Hallucination <span class="fr-pct">{100 - h} %</span>
                </div>
                {fr_bar(100 - h, '#F59E0B')}
                <div class="fr-item">⚠ Lorem Ipsum</div>
                <div class="fr-item">✓ Lorem Ipsum</div>
                <div class="fr-item">ⓘ Lorem Ipsum</div>
                <div class="fr-details-link">Details &gt;&gt;</div>
              </div>

              <div class="fr-section">
                <div class="fr-cat-title">
                  Bias <span class="fr-pct">{100 - b} %</span>
                </div>
                {fr_bar(100 - b, '#1DB87A')}
                <div class="fr-item">⚠ Lorem Ipsum</div>
                <div class="fr-item">✓ Lorem Ipsum</div>
                <div class="fr-item">ⓘ Lorem Ipsum</div>
                <div class="fr-details-link">Details &gt;&gt;</div>
              </div>

              <div class="fr-section">
                <div class="fr-cat-title">
                  Data Justice <span class="fr-pct">{i} %</span>
                </div>
                {fr_bar(i, '#3B7EF6')}
                <div class="fr-item">⚠ Lorem Ipsum</div>
                <div class="fr-item">✓ Lorem Ipsum</div>
                <div class="fr-item">ⓘ Lorem Ipsum</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            fix_c, exp_c = st.columns(2)
            with fix_c:
                st.button("Fix issues %", key="fix_fr", use_container_width=True)
            with exp_c:
                if st.button("Export report", key="exp_fr", use_container_width=True, type="primary"):
                    rapport = {
                        "persona": actieve_p["naam"],
                        "scores": st.session_state.scores,
                        "chatgeschiedenis": [{"rol": m["rol"], "inhoud": m["inhoud"]} for m in st.session_state.chatgeschiedenis],
                    }
                    st.download_button(
                        "⬇ JSON",
                        data=json.dumps(rapport, indent=2, ensure_ascii=False),
                        file_name=f"rapport_{actieve_p['naam'].replace(' ', '_')}.json",
                        mime="application/json",
                        key="dl_rapport",
                    )
            if st.button("✕ Sluit panel", key="close_fr", use_container_width=True):
                st.session_state.panel_mode = None
                st.rerun()

        elif st.session_state.panel_mode == "visualisatie":
            # Screen 11: Visualisatie + Suggestions
            totaal = scores["totaal"]
            st.markdown(f"""
            <div class="val-panel">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                <span class="val-panel-title">Full report</span>
                <button class="panel-close">✕</button>
              </div>
              <div class="fr-section">
                <div class="fr-cat-title">Hallucination <span class="fr-pct">{100 - scores['hallucinaties']} %</span></div>
                <div class="fr-bar-bg"><div class="fr-bar-fill" style="width:{100-scores['hallucinaties']}%;background:#F59E0B"></div></div>
                <div class="fr-item">⚠ Lorem Ipsum</div>
                <div class="fr-item">✓ Lorem Ipsum</div>
                <div class="fr-item">ⓘ Lorem Ipsum</div>
                <div class="fr-details-link">Details &gt;&gt;</div>
              </div>
              <div class="vis-section">
                <div class="vis-title">Visualisatie</div>
                <div class="vis-ring-wrap">
                  {score_ring_svg(totaal, 80)}
                  <div class="score-legend">
                    <div class="score-legend-good">Good</div>
                    <div class="score-legend-improve">Room for improvement</div>
                    <div class="score-legend-link">Lorem Ipsum</div>
                  </div>
                </div>
                <div class="suggestions-title">Suggestions</div>
                <div class="suggestion-item"><span class="suggestion-star">✦</span> Lorem Ipsum</div>
                <div class="suggestion-item"><span class="suggestion-star">✦</span> Lorem Ipsum</div>
                <div class="suggestion-item"><span class="suggestion-star">✦</span> Lorem Ipsum</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            fix_c2, exp_c2 = st.columns(2)
            with fix_c2:
                st.button("Fix issues %", key="fix_vis", use_container_width=True)
            with exp_c2:
                st.button("Export report", key="exp_vis", use_container_width=True, type="primary")
            if st.button("✕ Sluit panel", key="close_vis", use_container_width=True):
                st.session_state.panel_mode = None
                st.rerun()


# ─────────────────────────────────────────────
# BERICHTVERWERKING
# ─────────────────────────────────────────────
if send_clicked and user_input.strip():
    if not client:
        st.warning("⚠️ Voeg een geldige GROQ_API_KEY toe aan .streamlit/secrets.toml of als omgevingsvariabele.")
    else:
        nu = time.strftime("%H:%M")
        eerste_bericht = st.session_state.berichtentelling == 0

        st.session_state.chatgeschiedenis.append({
            "rol": "gebruiker",
            "inhoud": user_input.strip(),
            "tijd": nu,
        })

        with st.spinner("Synthetic User denkt na..."):
            resultaat = vraag_groq(client, actieve_p, user_input.strip(), st.session_state.api_berichten)

        st.session_state.api_berichten.append({"role": "user", "content": user_input.strip()})
        st.session_state.api_berichten.append({"role": "assistant", "content": resultaat["tekst"]})

        st.session_state.chatgeschiedenis.append({
            "rol": "assistent",
            "inhoud": resultaat["tekst"],
            "tijd": nu,
            "toon_persona_kaart": eerste_bericht,
        })

        if resultaat["succes"]:
            st.session_state.scores = resultaat["scores"]

        st.session_state.berichtentelling += 1
        st.rerun()




