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
        padding-left: 0rem !important;
        padding-right: 0rem !important;
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

    /* Profile Button Icon */
    button[key="nav_Profile"] {{
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0px !important;
        background-image: url("app/static/profile.png") !important;
        background-size: cover !important;
        background-position: center !important;
        color: transparent !important; 
        border: 2px solid #3b82f6 !important;
    }}

    /* UI Elements */
    .testimonial-card {{
        background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 180px;
        max-width: 800px; margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    
    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 380px; }}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; }}
    
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

# Container for standard page content
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

# --- PAGE ROUTING ---

# 1. HOME SECTION (REFACTORED)
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

    # Interactive Tab Columns
    t1, t2, t3 = st.columns(3)
    if t1.button("Why Napkin", use_container_width=True, type="primary" if st.session_state.home_tab == "Why Napkin" else "secondary"):
        st.session_state.home_tab = "Why Napkin"; st.rerun()
    if t2.button("How to use", use_container_width=True, type="primary" if st.session_state.home_tab == "How to use" else "secondary"):
        st.session_state.home_tab = "How to use"; st.rerun()
    if t3.button("Try now", use_container_width=True, type="primary" if st.session_state.home_tab == "Try now" else "secondary"):
        st.session_state.home_tab = "Try now"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab Content Area
    if st.session_state.home_tab == "Why Napkin":
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("### Engineering Speed")
            st.write("""
                Traditional CAD workflows are a bottleneck for emergency repairs and rapid prototyping. 
                Napkin leverages AI trained on ISO standards and machinist logic to generate 
                production-ready geometry in seconds. 
                
                Reduce your downtime from days to minutes by turning physical ideas into digital assets 
                without the need for complex modeling software.
            """)
        with right:
            st.image("https://via.placeholder.com/600x350/161b22/58a6ff?text=Industrial+AI+Engine+Preview", use_container_width=True)

    elif st.session_state.home_tab == "How to use":
        st.markdown("<div style='text-align:center;'><h3>Process Overview</h3></div>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI")

    elif st.session_state.home_tab == "Try now":
        st.markdown("<div style='text-align:center; padding: 40px 0;'>", unsafe_allow_html=True)
        st.markdown("### Ready to start printing?")
        st.write("Join leading engineering teams and streamline your production floor.")
        if st.button("Explore Pricing & Plans", type="primary"):
            set_page("Pricing")
        st.markdown("</div>", unsafe_allow_html=True)

    # Testimonials
    st.markdown("---")
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "Fundamental change for emergency production part replacements.", "author": "Maintenance Lead, TechBuild", "img": "https://i.pravatar.cc/150?u=2"}
    ]
    curr = testimonials[st.session_state.testimonial_index]
    tc1, tc2, tc3 = st.columns([1, 6, 1])
    if tc1.button("←", key="prev_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials); st.rerun()
    tc2.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><i>"{curr["quote"]}"</i><br><b>— {curr["author"]}</b></div></div>', unsafe_allow_html=True)
    if tc3.button("→", key="next_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials); st.rerun()

# 2. MAKE A PART
elif st.session_state.page == "Make a Part":
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        upload_choice = st.radio("Input Mode:", ["Sketch + Description", "Text Description Only"], horizontal=True)
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png'], label_visibility="collapsed")
        if uploaded_file: st.image(PIL.Image.open(uploaded_file), use_container_width=True)
        user_context = st.text_area("Specifications", placeholder="e.g. A 50x50mm cube with M5 holes...", height=150)
        if st.button("Generate 3D Model", type="primary", use_container_width=True):
            with st.spinner("Analyzing and Coding..."):
                st.info("Generation logic active. Ensure API keys are set in secrets.")
    with col2:
        st.write("3D Preview will appear here.")

# 3. PRICING (ALL CONTENT KEPT)
elif st.session_state.page == "Pricing":
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="price-card"><h3>Starter</h3><div class="price-amt">£0</div><p>1 week free trial</p><p>1 connected device</p><p>1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Join Free", key="p1", use_container_width=True)
    with p2:
        st.markdown('<div class="price-card" style="border-color:#58a6ff"><h3>Professional</h3><div class="price-amt">£65</div><p>Unlimited exports</p><p>1 connected device</p><p>1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Get Professional", type="primary", key="p2", use_container_width=True)
    with p3:
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom</div><p>Unlimited exports</p><p>Unlimited devices</p><p>Unlimited printers</p></div>', unsafe_allow_html=True)
        st.button("Contact Sales", key="p3", use_container_width=True)

# 4. HELP (ALL CONTENT KEPT)
elif st.session_state.page == "Help":
    st.markdown("### How to use Napkin")
    st.markdown("1. **Upload or Describe:** Use a photo of your sketch or type specs.\n2. **Be Specific:** Mention exact dimensions or hole types.\n3. **Generate:** The AI translates input into geometry.\n4. **Download:** Export .stl directly.")
    st.markdown("---")
    st.markdown("### Setting up your 3D Printer")
    st.markdown("1. **Network Discovery:** Ensure same Wi-Fi.\n2. **API Access:** Get your key from printer settings.\n3. **Direct Printing:** Send generated parts straight to the bed.")
    st.markdown("---")
    st.markdown("### Frequently Asked Questions")
    with st.expander("How is this software developed?"):
        st.write("Engineered for industrial environments using parametric modeling and machinist logic to guarantee structural integrity.")
    with st.expander("Does it work with resin printers?"):
        st.write("Yes, STL files are compatible with both FDM and SLA slicers.")

# 5. GALLERY (ALL CONTENT KEPT)
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/gallery3.jpg", use_container_width=True)
    g2.image("static/gallery4.jpg", use_container_width=True)
    g3, g4 = st.columns(2)
    g3.image("static/gallery5.jpg", use_container_width=True)
    g4.image("static/gallery6.jpg", use_container_width=True)

# 6. CONTACT
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name"); st.text_input("Company"); st.text_input("Email"); st.text_area("Message")
        st.form_submit_button("Send Message")

# 7. PROFILE (WITH COMPANY & NEW METRICS)
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
        s1.metric("Parts Generated", "42")
        s2.metric("Printers Connected", "1")
        s3.metric("Current Plan", "Professional")
        if st.button("Save Changes", type="primary"): st.success("Profile Updated!")

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""<div class="footer-minimal"><p>© 2025 Napkin Manufacturing Tool. All rights reserved.</p></div>""", unsafe_allow_html=True)
