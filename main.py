import streamlit as st
from google import genai
import PIL.Image
import subprocess
from streamlit_stl import stl_from_file
import json
import re
import os
import shutil  # Required to find OpenSCAD on the server

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
    .stApp {{ background-color: #0e1117; color: #ffffff; }}
    
    /* Header/Footer Branding */
    .brand-blue {{
        background-color: #1e3a8a;
        border-bottom: 3px solid #3b82f6;
        padding: 40px 20px;
        margin: -6rem -5rem 2rem -5rem;
        text-align: center;
    }}
    .footer-minimal {{
        background-color: #1e3a8a;
        border-top: 3px solid #3b82f6;
        padding: 40px 20px;
        margin: 4rem -5rem -6rem -5rem;
        text-align: center;
        color: #e2e8f0;
    }}
    .nav-title {{ font-size: 3.5rem; font-weight: 800; color: white; letter-spacing: -1.5px; }}
    
    /* Contact Social Icons */
    .social-underlay {{
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }}
    .social-underlay img {{
        width: 70px !important;
        height: 70px !important;
        object-fit: contain;
    }}
    
    /* Footer specific icon size */
    .footer-icon-box {{
        background-color: white;
        padding: 6px;
        border-radius: 6px;
        display: inline-flex;
        margin: 0 8px;
    }}
    .footer-icon-box img {{
        width: 18px !important;
        height: 18px !important;
    }}

    /* Testimonial Carousel Card */
    .testimonial-card {{
        background: #161b22;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #30363d;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 180px;
        max-width: 750px;
        margin: 0 auto;
    }}
    .testimonial-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }}
    .testimonial-quote {{ font-style: italic; font-size: 1.05rem; color: #d1d5db; line-height: 1.4; }}

    /* Home Section Branding (Overlay Style) */
    .home-section {{
        position: relative; width: 100%; min-height: 450px;
        border-radius: 20px; overflow: hidden; margin-bottom: 40px;
        display: flex; align-items: center; justify-content: center;
    }}
    .section-bg {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.35; z-index: 1; }}
    .section-content {{ position: relative; z-index: 2; width: 80%; text-align: center; padding: 20px; }}
    .section-text {{ font-size: 2.5rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .highlight {{ color: #58a6ff; }}

    /* Pricing Card */
    .price-card {{ background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 350px; margin-bottom: 10px; }}
    .price-amt {{ font-size: 2.8rem; font-weight: 800; color: #58a6ff; display: inline-block; }}
    .per-month {{ font-size: 1rem; color: #8b949e; font-weight: 400; margin-left: 5px; }}
    
    .currency-sub {{ 
        color: #8b949e; 
        font-size: 0.85rem; 
        margin-bottom: 15px; 
    }}

    .stButton>button {{ border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; }}
    button[kind="primary"] {{ background-color: #3b82f6 !important; border: none !important; color: white !important; }}
    
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    
    <div class="brand-blue">
        <div class="nav-title">NAPKIN</div>
    </div>
    """, unsafe_allow_html=True)

# --- NAVBAR ---
nav_cols = st.columns(6)
pages = ["Home", "Make a Part", "Pricing", "Help", "Gallery", "Contact"]
for i, p in enumerate(pages):
    if nav_cols[i].button(p, use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page == p else "secondary"):
        set_page(p)

st.markdown("<br>", unsafe_allow_html=True)

# --- PAGE ROUTING ---

# 1. HOME
if st.session_state.page == "Home":
    st.markdown("""
        <div class="home-section"><img class="section-bg" src="app/static/home1.jpg"><div class="section-content"><div class="section-text">Combining <span class="highlight">AI</span> with <span class="highlight">3D printing</span> to turn napkin sketches into real parts within minutes.</div></div></div>
        <div class="home-section"><img class="section-bg" src="app/static/production1.jpg"><div class="section-content"><div class="section-text">Production downtime can cost companies up to <span class="highlight">millions of dollars</span> per hour.</div></div></div>
        <div class="home-section"><img class="section-bg" src="app/static/print1.jpg"><div class="section-content"><div class="section-text">Continuous advancements in AI are evolving Napkin to become the <span class="highlight">future of rapid manufacturing.</span></div></div></div>
    """, unsafe_allow_html=True)

    st.markdown("### Process Overview")
    st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI") 

    st.markdown("<br><h3 style='text-align:center;'>Testimonials</h3>", unsafe_allow_html=True)
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used in our R&D lab or manufacturing space.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "Napkin has fundamentally changed how we handle emergency production part replacements.", "author": "Maintenance Team Leader, TechBuild Solutions", "img": "https://i.pravatar.cc/150?u=2"},
        {"quote": "Intuitive, fast, and convenient. This software is revolutionary for staff who are untrained in CAD.", "author": "Operations Engineer, Global Auto", "img": "https://i.pravatar.cc/150?u=3"},
        {"quote": "On several ocasions, we've returned to production within a fraction of the time we previously could have.", "author": "CEO, Something Engineering", "img": "https://i.pravatar.cc/150?u=4"}
    ]
    
    curr = testimonials[st.session_state.testimonial_index]
    t_col1, t_carousel, t_col2 = st.columns([1, 6, 1])
    with t_col1:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("←", key="prev_t"):
            st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials)
            st.rerun()
    with t_carousel:
        st.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><div class="testimonial-quote">"{curr["quote"]}"</div><small><b>— {curr["author"]}</b></small></div></div>', unsafe_allow_html=True)
        dots = "".join(["● " if i == st.session_state.testimonial_index else "○ " for i in range(len(testimonials))])
        st.markdown(f"<p style='text-align:center; font-size:1.5rem; color:#3b82f6; margin-top:10px;'>{dots}</p>", unsafe_allow_html=True)
    with t_col2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if st.button("→", key="next_t"):
            st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials)
            st.rerun()

    if st.button("Get Started", type="primary", use_container_width=True):
        set_page("Make a Part")

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
                    # 1. Find the OpenSCAD executable on the server
                    openscad_executable = shutil.which("openscad")
                    
                    if not openscad_executable:
                        st.error("OpenSCAD is not installed. Please ensure packages.txt contains 'openscad' and is in your GitHub root.")
                    else:
                        client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                        prompt = f"Act as an OpenSCAD engineer. Create code based on: '{user_context}'. Use $fn=50;. Provide a JSON 'METADATA' object. Format: ```openscad [code] ``` and ```json [metadata] ```"
                        inputs = [prompt, PIL.Image.open(uploaded_file)] if uploaded_file else [prompt]
                        response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=inputs)
                        
                        scad_match = re.search(r"```openscad(.*?)```", response.text, re.DOTALL)
                        if scad_match:
                            scad_code = scad_match.group(1).strip()
                            with open("part.scad", "w") as f: f.write(scad_code)
                            
                            # 2. Run the subprocess using the found path
                            subprocess.run([openscad_executable, "-o", "part.stl", "part.scad"], check=True)
                            
                            stl_from_file("part.stl", color='#58a6ff')
                            st.download_button("Download STL", open("part.stl", "rb"), "part.stl", use_container_width=True)
                        else:
                            st.warning("AI could not generate valid OpenSCAD code. Try adjusting your description.")
                except Exception as e: 
                    st.error(f"Error during generation: {e}")

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

# 4. HELP
elif st.session_state.page == "Help":
    st.markdown("### How to use Napkin")
    st.markdown("""
    1. **Upload or Describe:** Use a photo of your hand-drawn sketch or just type out what you need in the specification box.
    2. **Be Specific:** For precision engineering, mention exact dimensions or hole types (e.g. 'M5 clearance hole').
    3. **Generate:** Click the 'Generate 3D Model' button. Our AI engine will translate your input into geometric code.
    4. **Download:** Export your .stl file directly for use in any slicing software.
    """)
    st.markdown("---")
    st.markdown("### Setting up your 3D Printer")
    st.markdown("""
    1. **Network Discovery:** Ensure your printer and computer are on the same Wi-Fi network.
    2. **API Access:** Locate your API Key or Access Code within your printer's network settings.
    3. **Direct Printing:** Once configured, you can send generated parts straight to the print bed without leaving Napkin.
    """)
    st.markdown("---")
    st.markdown("### Frequently Asked Questions")
    with st.expander("What file types does Napkin export?"): st.write("Napkin currently exports high-resolution .STL files.")
    with st.expander("Does it work with resin printers?"): st.write("Yes, the .STL files are compatible with both FDM and SLA slicers.")

# 5. GALLERY
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/print2.jpg")
    g2.image("static/production2.jpg")

# 6. CONTACT
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name")
        st.text_input("Company")
        st.text_input("Email")
        st.text_area("Message")
        st.form_submit_button("Send Message")
    
    st.markdown("<br>Connect with us", unsafe_allow_html=True)
    s1, s2, s3, _ = st.columns([1.5, 1.5, 1.5, 4.5])
    for col, img, lbl in zip([s1, s2, s3], ["insta.png", "linkedin.png", "youtube.png"], ["Instagram", "LinkedIn", "YouTube"]):
        with col:
            st.markdown(f'<div class="social-underlay"><img src="app/static/{img}"></div>', unsafe_allow_html=True)
            st.button(lbl, key=f"soc_{lbl}", use_container_width=True)

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