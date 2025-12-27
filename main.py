import streamlit as st
from google import genai
import PIL.Image
import subprocess
from streamlit_stl import stl_from_file
import json
import re
import os
import shutil

# --- PAGE CONFIG ---
st.set_page_config(page_title="Napkin", layout="wide", initial_sidebar_state="collapsed")

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'testimonial_index' not in st.session_state:
    st.session_state.testimonial_index = 0
if 'home_tab' not in st.session_state:
    st.session_state.home_tab = "Why Napkin"

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    /* Global Layout */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }}
    .stApp {{ background-color: #0e1117; color: #ffffff; }}

    /* Navigation Bar */
    [data-testid="stHorizontalBlock"]:has(button[key^="nav_"]) {{
        background-color: #1e3a8a !important;
        border-bottom: 3px solid #3b82f6 !important;
        padding: 40px 5rem 20px 5rem !important;
        margin-top: 0rem !important;
        width: 100vw !important;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        display: flex;
        align-items: center;
    }}

    /* Hero Section with Vertical Gradient Fade */
    .hero-container {{
        position: relative;
        width: 100%;
        height: 550px;
        background-image: linear-gradient(to bottom, rgba(14, 17, 23, 0) 50%, rgba(14, 17, 23, 1) 100%), url("app/static/home1.jpg");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0px;
    }}
    .section-content {{ position: relative; z-index: 2; width: 70%; text-align: center; }}
    .section-text {{ font-size: 2.8rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 15px rgba(0,0,0,0.9); }}
    .highlight {{ color: #58a6ff; }}

    /* UI Elements */
    .testimonial-card {{
        background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 180px;
        max-width: 800px; margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    
    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 380px; margin-bottom: 16px;}}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; }}
    
    .per-month {{ 
        font-size: 1rem; 
        color: #8b949e; 
        font-weight: 400; 
        margin-left: 5px;
    }}
    .currency-sub {{ 
        font-size: 0.85rem; 
        color: #8b949e; 
        margin-top: -10px; 
        margin-bottom: 15px;
    }}

    .stButton>button {{ border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #3b82f6 !important; border: none !important; }}
    button[key="sign_out_btn"] {{ border-color: #f85149 !important; color: #f85149 !important; }}

    .footer-minimal {{
        background-color: #1e3a8a; 
        border-top: 3px solid #3b82f6;
        padding: 20px 15px; 
        text-align: center; 
        color: #e2e8f0; 
        margin-top: 4rem;
        margin-left: -5.3% !important;
        margin-right: -5.3% !important;
        width: calc(100% + 10.6%) !important;
    }}

    .footer-icon-box img {{
        width: 30px !important;
        height: auto !important;
        margin: 0 10px;
    }}

    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR ---
pages = ["Home", "Make a Part", "Pricing", "Help", "Gallery", "Contact", "Profile"]
nav_cols = st.columns(len(pages))

for i, p in enumerate(pages):
    if nav_cols[i].button(p, use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary"):
        set_page(p)

# Container for standard page content
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

# --- PAGE ROUTING ---

if st.session_state.page == "Home":
    st.markdown("""
        <div class="hero-container">
            <div class="section-content">
                <div class="section-text">
                    Combining <span class="highlight">AI</span> with <span class="highlight">3D printing</span> 
                    to turn napkin sketches into real parts.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    if t1.button("Why Napkin", use_container_width=True, type="primary" if st.session_state.home_tab == "Why Napkin" else "secondary"):
        st.session_state.home_tab = "Why Napkin"; st.rerun()
    if t2.button("How to use", use_container_width=True, type="primary" if st.session_state.home_tab == "How
