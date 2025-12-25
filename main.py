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

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }}
    .stApp {{ background-color: #0e1117; color: #ffffff; }}

    /* Navbar styling */
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

    /* Hero Sections */
    .home-section {{
        position: relative; width: 100%; min-height: 450px;
        border-radius: 20px; overflow: hidden; margin-bottom: 40px;
        display: flex; align-items: center; justify-content: center;
    }}
    .section-bg {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.35; z-index: 1; }}
    .section-content {{ position: relative; z-index: 2; width: 80%; text-align: center; padding: 20px; }}
    .section-text {{ font-size: 2.5rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .highlight {{ color: #58a6ff; }}

    /* Profile Button Icon */
    button[key="nav_Profile"] {{
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        background-image: url("app/static/profile.png") !important;
        background-size: cover !important;
        background-position: center !important;
        color: transparent !important; 
        border: 2px solid #3b82f6 !important;
    }}

    /* Global UI Components */
    .testimonial-card {{
        background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 180px;
        max-width: 750px; margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    
    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 350px; }}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; }}
    .currency-sub {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 15px; }}

    .stButton>button {{ border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #3b82f6 !important; border: none !important; }}
    button[key="sign_out_btn"] {{ border-color: #f85149 !important; color: #f85149 !important; }}

    .footer-minimal {{
        background-color: #1e3a8a; border-top: 3px solid #3b82f6;
        padding: 40px 20px; text-align: center; color: #e2e8f0; margin-top: 4rem;
    }}

    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- NAVBAR ---
nav_cols = st.columns([1,1,1,1,1,1,0.5])
pages = ["Home", "Make a Part", "Pricing", "Help", "Gallery", "Contact"]
for i, p in enumerate(pages):
    if nav_cols[i].button(p, use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary"):
        set_page(p)
if nav_cols[6].button(".", key="nav_Profile"):
    set_page("Profile")

st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

# --- ROUTING ---

# 1. HOME SECTION
if st.session_state.page == "Home":
    st.markdown("""
        <div class="home-section"><img class="section-bg" src="app/static/home1.jpg"><div class="section-content"><div class="section-text">Combining <span class="highlight">AI</span> with <span class="highlight">3D printing</span> to turn napkin sketches into real parts.</div></div></div>
        <div class="home-section"><img class="section-bg" src="app/static/production1.jpg"><div class="section-content"><div class="section-text">Production downtime can cost companies up to <span class="highlight">millions of dollars</span> per hour. </div></div></div>
        <div class="home-section"><img class="section-bg" src="app/static/print1.jpg"><div class="section-content"><div class="section-text">Merging modern technologies into a tool that <span class="highlight">continuously improves.</span></div></div></div>
    """, unsafe_allow_html=True)

    st.markdown("### Process Overview")
    st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI") 

    st.markdown("<br><h3 style='text-align:center;'>Testimonials</h3>", unsafe_allow_html=True)
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used in our R&D lab.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "Napkin has fundamentally changed how we handle emergency part replacements.", "author": "Maintenance Lead, TechBuild", "img": "https://i.pravatar.cc/150?u=2"},
        {"quote": "Intuitive, fast, and convenient. This software is revolutionary.", "author": "Operations Engineer, Global Auto", "img": "https://i.pravatar.cc/150?u=3"},
        {"quote": "On several occasions, we've returned to production within a fraction of the time.", "author": "CEO, Something Engineering", "img": "https://i.pravatar.cc/150?u=4"}
    ]
    curr = testimonials[st.session_state.testimonial_index]
    t_col1, t_carousel, t_col2 = st.columns([1, 6, 1])
    with t_col1:
        if st.button("←", key="prev_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials); st.rerun()
    with t_carousel:
        st.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><div class="testimonial-quote">"{curr["quote"]}"</div><small><b>— {curr["author"]}</b></small></div></div>', unsafe_allow_html=True)
    with t_col2:
        if st.button("→", key="next_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials); st.rerun()

# 2. MAKE A PART
elif st.session_state.page == "Make a Part":
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.radio("Mode:", ["Sketch + Description", "Text Only"], horizontal=True)
        st.file_uploader("Upload Image", type=['jpg', 'png'])
        st.text_area("Specifications", placeholder="e.g. A 50x50mm cube...", height=150)
        st.button("Generate 3D Model", type="primary", use_container_width=True)
    with c2: st.write("Preview Area")

# 3. PRICING
elif st.session_state.page == "Pricing":
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="price-card"><h3>Starter</h3><div class="price-amt">£0</div><div class="currency-sub">$0 USD | €0 EUR</div><p>1 week free trial</p><p>1 connected device</p><p>1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Join Free", key="p1", use_container_width=True)
    with p2:
        st.markdown('<div class="price-card" style="border:2px solid #3b82f6"><h3>Professional</h3><div class="price-amt">£65</div><div class="currency-sub">$82 USD | €78 EUR</div><p>Unlimited exports</p><p>1 connected device</p><p>1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Get Professional", type="primary", key="p2", use_container_width=True)
    with p3:
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom</div><div class="currency-sub">Tailored Scale</div><p>Unlimited exports</p><p>Unlimited devices</p><p>Unlimited printers</p></div>', unsafe_allow_html=True)
        st.button("Contact Sales", key="p3", use_container_width=True)

# 4. HELP
elif st.session_state.page == "Help":
    st.markdown("### How to use Napkin")
    st.write("1. **Upload or Describe:** Use a sketch or type out specs.\n2. **Be Specific:** Mention exact dimensions.\n3. **Generate:** AI creates geometry code.\n4. **Download:** Export .stl directly.")
    st.markdown("---")
    st.markdown("### Setting up your 3D Printer")
    st.write("1. **Network Discovery:** Ensure same Wi-Fi.\n2. **API Access:** Find your key in settings.\n3. **Direct Printing:** Send parts straight to the bed.")
    st.markdown("---")
    st.markdown("### Frequently Asked Questions")
    with st.expander("How is this software developed?"):
        st.write("Uses parametric precision engines and machinist logic for structural integrity and ISO compliance.")
    with st.expander("Does it work with resin printers?"):
        st.write("Yes, STL files are compatible with both FDM and SLA slicers.")

# 5. GALLERY
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/gallery3.jpg", use_container_width=True); g2.image("static/gallery4.jpg", use_container_width=True)
    g3, g4 = st.columns(2)
    g3.image("static/gallery5.jpg", use_container_width=True); g4.image("static/gallery6.jpg", use_container_width=True)
    g5, g6 = st.columns(2)
    g5.image("static/print1.jpg", use_container_width=True); g6.image("static/production2.jpg", use_container_width=True)

# 6. CONTACT
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name"); st.text_input("Company"); st.text_input("Email"); st.text_area("Message")
        st.form_submit_button("Send Message")

# 7. PROFILE
elif st.session_state.page == "Profile":
    st.markdown("### User Profile")
    pr1, pr2 = st.columns([1, 2])
    with pr1:
        st.markdown('<div style="text-align:center;"><img src="app/static/profile.png" style="border-radius:50%; border:4px solid #3b82f6; width:150px; height:150px; object-fit:cover;"><h4>John Doe</h4><p style="color:#8b949e;">Senior Engineer</p></div>', unsafe_allow_html=True)
        if st.button("Sign Out", key="sign_out_btn", use_container_width=True): set_page("Home")
    with pr2:
        st.markdown("#### Account Information")
        st.text_input("Full Name", "John Doe"); st.text_input("Company", "TechBuild Solutions"); st.text_input("Email", "john.doe@techbuild.com")
        st.markdown("#### Statistics")
        s1, s2, s3 = st.columns(3)
        s1.metric("Parts Generated", "42"); s2.metric("Printers Connected", "1"); s3.metric("Current Plan", "Professional")
        if st.button("Save Changes", type="primary", use_container_width=True): st.success("Updated!")

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""<div class="footer-minimal"><p>© 2025 Napkin Manufacturing Tool. All rights reserved.</p></div>""", unsafe_allow_html=True)
