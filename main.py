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
    /* 1. Global Layout & Reset */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }}
    .stApp {{ background-color: #0e1117; color: #ffffff; }}

    /* 2. Navigation Bar */
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

    /* 3. Hero & Home Sections */
    .hero-container {{
        position: relative;
        width: 100%;
        height: 500px;
        background-image: linear-gradient(to bottom, rgba(14, 17, 17, 0) 60%, rgba(14, 17, 17, 1) 100%), url("app/static/home1.jpg");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        border-radius: 0 0 20px 20px;
    }}
    .section-content {{ position: relative; z-index: 2; width: 80%; text-align: center; padding: 20px; }}
    .section-text {{ font-size: 2.5rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .highlight {{ color: #58a6ff; }}

    /* 4. Profile Icon Styling */
    button[key="nav_Profile"] {{
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0px !important;
        min-width: 50px !important;
        background-image: url("app/static/profile.png") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        color: transparent !important; 
        border: 2px solid #3b82f6 !important;
    }}

    /* 5. UI Components */
    .testimonial-card {{
        background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 180px;
        max-width: 750px; margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    .testimonial-quote {{ font-style: italic; font-size: 1.05rem; color: #d1d5db; line-height: 1.4; }}
    
    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 350px; margin-bottom: 10px; }}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; display: inline-block; }}
    .per-month {{ font-size: 1rem; color: #8b949e; font-weight: 400; margin-left: 5px; }}
    .currency-sub {{ color: #8b949e; font-size: 0.85rem; margin-bottom: 15px; }}

    .stButton>button {{ border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #3b82f6 !important; border: none !important; color: white !important; }}
    button[key="sign_out_btn"] {{ border-color: #f85149 !important; color: #f85149 !important; }}

    .social-underlay {{ background-color: white; padding: 15px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px; }}
    .social-underlay img {{ width: 70px !important; height: 70px !important; object-fit: contain; }}
    .footer-icon-box {{ background-color: white; padding: 6px; border-radius: 6px; display: inline-flex; margin: 0 8px; }}
    .footer-icon-box img {{ width: 18px !important; height: 18px !important; }}

    .footer-minimal {{
        background-color: #1e3a8a; border-top: 3px solid #3b82f6;
        padding: 40px 20px; margin: 4rem 0rem -6rem 0rem; text-align: center; color: #e2e8f0;
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

# Main Content Padding
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

# --- PAGE ROUTING ---

# 1. HOME (UPDATED WITH TABS & GRADIENT)
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

    tab_cols = st.columns(3)
    if tab_cols[0].button("Why Napkin", use_container_width=True, type="primary" if st.session_state.home_tab == "Why Napkin" else "secondary"):
        st.session_state.home_tab = "Why Napkin"; st.rerun()
    if tab_cols[1].button("How to use", use_container_width=True, type="primary" if st.session_state.home_tab == "How to use" else "secondary"):
        st.session_state.home_tab = "How to use"; st.rerun()
    if tab_cols[2].button("Try now", use_container_width=True, type="primary" if st.session_state.home_tab == "Try now" else "secondary"):
        st.session_state.home_tab = "Try now"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.home_tab == "Why Napkin":
        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            st.markdown("### Why Napkin?")
            st.write("""
                Traditional CAD takes hours. Napkin takes seconds. 
                Our engine is built specifically for industrial maintenance and R&D teams who need functional parts now.
                
                By using mathematical modeling instead of just "drawing" pixels, we ensure that every part is physically accurate, ISO-compliant, and print-ready immediately.
            """)
        with c2:
            st.image("https://via.placeholder.com/600x400/161b22/58a6ff?text=Industrial+3D+Model+Preview", use_container_width=True)

    elif st.session_state.home_tab == "How to use":
        st.markdown("<div style='text-align:center;'><h3>Process Overview</h3></div>", unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI")

    elif st.session_state.home_tab == "Try now":
        st.markdown("<div style='text-align:center; padding: 50px 0;'><h3>Ready to turn your sketches into reality?</h3>", unsafe_allow_html=True)
        if st.button("View Pricing & Plans", type="primary"):
            set_page("Pricing")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>Testimonials</h3>", unsafe_allow_html=True)
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used in our R&D lab.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "Napkin has fundamentally changed how we handle emergency production replacements.", "author": "Maintenance Lead, TechBuild", "img": "https://i.pravatar.cc/150?u=2"},
        {"quote": "Intuitive and fast. Revolutionary for staff untrained in CAD.", "author": "Ops Engineer, Global Auto", "img": "https://i.pravatar.cc/150?u=3"},
        {"quote": "We've returned to production within a fraction of the time.", "author": "CEO, Something Engineering", "img": "https://i.pravatar.cc/150?u=4"}
    ]
    curr = testimonials[st.session_state.testimonial_index]
    t_col1, t_carousel, t_col2 = st.columns([1, 6, 1])
    with t_col1:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("←", key="prev_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials); st.rerun()
    with t_carousel:
        st.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><div class="testimonial-quote">"{curr["quote"]}"</div><small><b>— {curr["author"]}</b></small></div></div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-size:1.5rem; color:#3b82f6;'>{'● '* (st.session_state.testimonial_index+1)}{'○ '*(len(testimonials)-st.session_state.testimonial_index-1)}</p>", unsafe_allow_html=True)
    with t_col2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("→", key="next_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials); st.rerun()

# 2. MAKE A PART
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
                    if exe:
                        client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                        prompt = f"Act as an OpenSCAD engineer. Create code based on: '{user_context}'. Use $fn=50;. Provide a JSON 'METADATA' object. Format: ```openscad [code] ``` and ```json [metadata] ```"
                        inputs = [prompt, PIL.Image.open(uploaded_file)] if uploaded_file else [prompt]
                        response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=inputs)
                        scad_match = re.search(r"```openscad(.*?)```", response.text, re.DOTALL)
                        if scad_match:
                            scad_code = scad_match.group(1).strip()
                            with open("part.scad", "w") as f: f.write(scad_code)
                            subprocess.run([exe, "-o", "part.stl", "part.scad"], check=True)
                            stl_from_file("part.stl", color='#58a6ff')
                            st.download_button("Download STL", open("part.stl", "rb"), "part.stl", use_container_width=True)
                except Exception as e: st.error(f"Error: {e}")

# 3. PRICING
elif st.session_state.page == "Pricing":
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="price-card"><h3>Starter</h3><div class="price-amt">£0<span class="per-month">per month</span></div><div class="currency-sub">$0 USD | €0 EUR</div><p class="price-feat">1 week free trial</p><p class="price-feat">1 connected device</p><p class="price-feat">1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Join Free", key="p1", use_container_width=True)
    with p2:
        st.markdown('<div class="price-card" style="border-color:#58a6ff"><h3>Professional</h3><div class="price-amt">£65<span class="per-month">per month</span></div><div class="currency-sub">$82 USD | €78 EUR</div><p class="price-feat">Unlimited exports</p><p class="price-feat">1 connected device</p><p class="price-feat">1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Get Professional", type="primary", key="p2", use_container_width=True)
    with p3:
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom<span class="per-month">per month</span></div><div class="currency-sub">Tailored for large-scale operations</div><p class="price-feat">Unlimited exports</p><p class="price-feat">Unlimited connected devices</p><p class="price-feat">Unlimited connected printers</p></div>', unsafe_allow_html=True)
        st.button("Contact Sales", key="p3", use_container_width=True)

# 4. HELP (FULL CONTENT)
elif st.session_state.page == "Help":
    st.markdown("### How to use Napkin")
    st.markdown("1. **Upload or Describe:** Use a sketch or type your needs.\n2. **Be Specific:** Mention exact dimensions (e.g. M5 hole).\n3. **Generate:** AI creates the geometry code.\n4. **Download:** Export .stl directly.")
    st.markdown("---")
    st.markdown("### Setting up your 3D Printer")
    st.markdown("1. **Network Discovery:** Ensure same Wi-Fi.\n2. **API Access:** Get your key from printer settings.\n3. **Direct Printing:** Send parts straight to the bed.")
    st.markdown("---")
    st.markdown("### FAQs")
    with st.expander("How is this software developed?"):
        st.write("Uses parametric precision engines and machinist logic for structural integrity and ISO compliance.")
    with st.expander("Does it work with resin printers?"):
        st.write("Yes, STL files work with FDM and SLA slicers.")

# 5. GALLERY
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/gallery3.jpg", use_container_width=True)
    g2.image("static/gallery4.jpg", use_container_width=True)
    g3, g4 = st.columns(2)
    g3.image("static/gallery5.jpg", use_container_width=True)
    g4.image("static/gallery6.jpg", use_container_width=True)
    st.columns(2)[0].image("static/print1.jpg", use_container_width=True)
    st.columns(2)[1].image("static/production2.jpg", use_container_width=True)

# 6. CONTACT
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name"); st.text_input("Company"); st.text_input("Email"); st.text_area("Message")
        st.form_submit_button("Send Message")
    st.markdown("<br>Connect with us", unsafe_allow_html=True)
    s1, s2, s3, _ = st.columns([1.5, 1.5, 1.5, 4.5])
    s1.button("Instagram", key="soc_insta", use_container_width=True)
    s2.button("LinkedIn", key="soc_link", use_container_width=True)
    s3.button("YouTube", key="soc_yt", use_container_width=True)

# 7. PROFILE
elif st.session_state.page == "Profile":
    st.markdown("### User Profile")
    p1, p2 = st.columns([1, 2])
    with p1:
        st.markdown(f'<div style="text-align:center;"><img src="app/static/profile.png" style="border-radius:50%; border:4px solid #3b82f6; width:150px; height:150px; object-fit:cover;"><h4>John Doe</h4><p style="color:#8b949e;">Senior Engineer</p></div>', unsafe_allow_html=True)
        if st.button("Sign Out", key="sign_out_btn", use_container_width=True): set_page("Home")
    with p2:
        st.markdown("#### Account Information")
        st.text_input("Full Name", "John Doe"); st.text_input("Company", "TechBuild Solutions"); st.text_input("Email", "john.doe@techbuild.com")
        st.markdown("#### Statistics")
        st1, st2, st3 = st.columns(3)
        st1.metric("Parts Generated", "42"); st2.metric("Printers Connected", "1"); st3.metric("Current Plan", "Professional")
        if st.button("Save Changes", type="primary", use_container_width=True): st.success("Updated!")

st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""<div class="footer-minimal"><p style="font-weight:600; color:white;">FOLLOW US</p><p style="font-size:0.75rem; opacity:0.7;">© 2025 Napkin Manufacturing Tool. All rights reserved.</p></div>""", unsafe_allow_html=True)
