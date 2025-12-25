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

# --- CUSTOM CSS (FROM YOUR ORIGINAL CODE 1) ---
st.markdown(f"""
    <style>
    /* 1. Remove all default Streamlit padding */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }}

    /* 2. Navigation Bar Styling */
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

    .stApp {{ background-color: #0e1117; color: #ffffff; }}
    
    .footer-minimal {{
        background-color: #1e3a8a;
        border-top: 3px solid #3b82f6;
        padding: 40px 20px;
        margin: 4rem 0rem -6rem 0rem;
        text-align: center;
        color: #e2e8f0;
    }}
    
    button[key="nav_Profile"] {{
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0px !important;
        min-width: 50px !important;
        background-color: #30363d !important;
        font-size: 1.2rem !important;
    }}

    .social-underlay {{
        background-color: white; padding: 15px; border-radius: 12px;
        display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;
    }}
    .social-underlay img {{ width: 70px !important; height: 70px !important; object-fit: contain; }}
    
    .footer-icon-box {{
        background-color: white; padding: 6px; border-radius: 6px;
        display: inline-flex; margin: 0 8px;
    }}
    .footer-icon-box img {{ width: 18px !important; height: 18px !important; }}

    .testimonial-card {{
        background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 180px;
        max-width: 750px; margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    .testimonial-quote {{ font-style: italic; font-size: 1.05rem; color: #d1d5db; line-height: 1.4; }}

    /* HOME HERO SPECIFIC (ADAPTED) */
    .hero-container {{
        position: relative; width: 100%; height: 500px;
        background-image: linear-gradient(to bottom, rgba(14,17,23,0) 60%, rgba(14,17,23,1) 100%), url("app/static/home1.jpg");
        background-size: cover; background-position: center;
        display: flex; align-items: center; justify-content: center; margin-bottom: 40px; border-radius: 0 0 20px 20px;
    }}
    .section-content {{ position: relative; z-index: 2; width: 80%; text-align: center; padding: 20px; }}
    .section-text {{ font-size: 2.5rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .highlight {{ color: #58a6ff; }}

    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 350px; margin-bottom: 10px; }}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; display: inline-block; }}
    .per-month {{ font-size: 1rem; color: #8b949e; font-weight: 400; margin-left: 5px; }}
    .currency-sub {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 15px; }}

    .stButton>button {{ border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #3b82f6 !important; border: none !important; color: white !important; }}
    
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

if nav_cols[6].button("Profile", key="nav_Profile", type="primary" if st.session_state.page == "Profile" else "secondary"):
    set_page("Profile")

# Content padding for the rest of the page
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

# --- PAGE ROUTING ---

# 1. HOME (UPDATED WITH TABS)
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

    # Tabs
    t1, t2, t3 = st.columns(3)
    if t1.button("Why Napkin", use_container_width=True, type="primary" if st.session_state.home_tab == "Why Napkin" else "secondary"):
        st.session_state.home_tab = "Why Napkin"; st.rerun()
    if t2.button("How to use", use_container_width=True, type="primary" if st.session_state.home_tab == "How to use" else "secondary"):
        st.session_state.home_tab = "How to use"; st.rerun()
    if t3.button("Try now", use_container_width=True, type="primary" if st.session_state.home_tab == "Try now" else "secondary"):
        st.session_state.home_tab = "Try now"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.home_tab == "Why Napkin":
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("### Engineering Speed")
            st.write("Traditional CAD workflows are a bottleneck for emergency repairs. Napkin leverages AI trained on ISO standards to generate production-ready geometry in seconds.")
        with right:
            st.image("https://via.placeholder.com/600x350/161b22/58a6ff?text=Industrial+AI+Engine", use_container_width=True)

    elif st.session_state.home_tab == "How to use":
        st.markdown("<h3 style='text-align:center;'>Process Overview</h3>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI")

    elif st.session_state.home_tab == "Try now":
        st.markdown("<div style='text-align:center; padding: 40px 0;'><h3>Ready to start printing?</h3>", unsafe_allow_html=True)
        if st.button("Explore Pricing & Plans", type="primary"):
            set_page("Pricing")
        st.markdown("</div>", unsafe_allow_html=True)

    # Testimonials (Keep Original Style)
    st.markdown("<br><h3 style='text-align:center;'>Testimonials</h3>", unsafe_allow_html=True)
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "Napkin has fundamentally changed how we handle emergency production part replacements.", "author": "Maintenance Team Leader, TechBuild", "img": "https://i.pravatar.cc/150?u=2"}
    ]
    curr = testimonials[st.session_state.testimonial_index]
    t_col1, t_carousel, t_col2 = st.columns([1, 6, 1])
    with t_col1:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("←", key="prev_t"):
            st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials); st.rerun()
    with t_carousel:
        st.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><div class="testimonial-quote">"{curr["quote"]}"</div><small><b>— {curr["author"]}</b></small></div></div>', unsafe_allow_html=True)
    with t_col2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("→", key="next_t"):
            st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials); st.rerun()

# 2. MAKE A PART (ORIGINAL)
elif st.session_state.page == "Make a Part":
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        upload_choice = st.radio("Input Mode:", ["Sketch + Description", "Text Description Only"], horizontal=True)
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png'], label_visibility="collapsed") if upload_choice == "Sketch + Description" else None
        if uploaded_file: st.image(PIL.Image.open(uploaded_file), use_container_width=True)
        user_context = st.text_area("Specifications", placeholder="e.g. A 50x50mm cube...", height=150)
        generate_btn = st.button("Generate 3D Model", type="primary", use_container_width=True)
    with col2:
        if generate_btn:
            with st.spinner("Generating..."):
                try:
                    exe = shutil.which("openscad")
                    if not exe: st.error("Engine Error: OpenSCAD not found.")
                    else:
                        client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                        prompt = f"Act as an OpenSCAD engineer. Code for: '{user_context}'. Format: ```openscad [code] ```"
                        inputs = [prompt, PIL.Image.open(uploaded_file)] if uploaded_file else [prompt]
                        response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=inputs)
                        scad_match = re.search(r"```openscad(.*?)```", response.text, re.DOTALL)
                        if scad_match:
                            scad_code = scad_match.group(1).strip()
                            with open("part.scad", "w") as f: f.write(scad_code)
                            subprocess.run([exe, "-o", "part.stl", "part.scad"], check=True)
                            stl_from_file("part.stl", color='#58a6ff')
                except Exception as e: st.error(f"Error: {e}")

# 3. PRICING (ORIGINAL)
elif st.session_state.page == "Pricing":
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="price-card"><h3>Starter</h3><div class="price-amt">£0<span class="per-month">per month</span></div><p>1 week free trial</p></div>', unsafe_allow_html=True)
        st.button("Join Free", key="p1", use_container_width=True)
    with p2:
        st.markdown('<div class="price-card" style="border-color:#58a6ff"><h3>Professional</h3><div class="price-amt">£65<span class="per-month">per month</span></div><p>Unlimited exports</p></div>', unsafe_allow_html=True)
        st.button("Get Professional", type="primary", key="p2", use_container_width=True)
    with p3:
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom</div><p>Tailored for large-scale</p></div>', unsafe_allow_html=True)
        st.button("Contact Sales", key="p3", use_container_width=True)

# 4. HELP (ORIGINAL)
elif st.session_state.page == "Help":
    st.markdown("### How to use Napkin")
    st.markdown("1. Upload or Describe. 2. Be Specific. 3. Generate. 4. Print.")
    with st.expander("FAQ"):
        st.write("Answers to common industrial 3D printing questions.")

# 5. GALLERY (ORIGINAL)
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/print1.jpg", use_container_width=True)
    g2.image("static/production2.jpg", use_container_width=True)

# 6. CONTACT (ORIGINAL)
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name")
        st.text_input("Email")
        st.text_area("Message")
        st.form_submit_button("Send Message")

# 7. PROFILE (ORIGINAL)
elif st.session_state.page == "Profile":
    st.markdown("### User Profile")
    prof_col1, prof_col2 = st.columns([1, 2])
    with prof_col1:
        st.markdown('<img src="https://i.pravatar.cc/150?u=napkin" style="border-radius:50%; border:4px solid #3b82f6; width:150px;">', unsafe_allow_html=True)
    with prof_col2:
        st.text_input("Full Name", value="John Doe")
        st.metric("Parts Generated", "42")
        if st.button("Save Changes"): st.success("Profile Updated!")

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
    <div class="footer-minimal">
        <p style="font-size: 0.9rem; margin-bottom: 15px; font-weight: 600; color: white;">FOLLOW US</p>
        <div style="display: flex; justify-content: center; align-items: center;">
            <div class="footer-icon-box"><img src="app/static/insta.png"></div>
            <div class="footer-icon-box"><img src="app/static/linkedin.png"></div>
            <div class="footer-icon-box"><img src="app/static/youtube.png"></div>
        </div>
        <p style="font-size:0.75rem; margin-top: 25px; opacity: 0.7;">© 2025 Napkin Manufacturing Tool. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)
