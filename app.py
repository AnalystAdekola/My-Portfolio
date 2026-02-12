import streamlit as st
import sqlite3
import os
import shutil
from streamlit_quill import st_quill

# --- 1. CONFIGURATION & STUDIO THEME ---
st.set_page_config(page_title="My Office Showcase", layout="wide")

# Custom CSS for "The Studio" look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    
    .stApp {
        background-color: #050505;
        color: #E0E0E0;
    }
    
    /* Elegant Header */
    .header-box { text-align: center; padding: 60px 0 40px 0; }
    .main-title { 
        font-family: 'Playfair Display', serif; 
        font-size: 4.5rem; 
        color: #FFFFFF;
        letter-spacing: -1px;
        margin: 0;
    }
    .title-accent { color: #3A86FF; font-style: italic; }
    .tagline { 
        font-family: 'Inter', sans-serif; 
        color: #666666; 
        font-size: 1rem; 
        letter-spacing: 3px; 
        text-transform: uppercase;
        margin-top: 10px; 
    }

    /* Project Cards */
    .project-container {
        border-bottom: 1px solid #1A1A1A;
        padding-bottom: 60px;
        margin-bottom: 60px;
    }
    
    .project-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        color: #FFFFFF;
        margin-bottom: 5px;
    }
    
    .project-sub {
        font-family: 'Inter', sans-serif;
        color: #3A86FF;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        margin-bottom: 25px;
    }

    /* Input focus colors */
    .stTextInput>div>div>input { background-color: #111; color: white; border-color: #222; }
    </style>
    """, unsafe_allow_html=True)

SAVE_DIR = "showcase_media"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('office_studio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  header TEXT, subtitle TEXT, description TEXT, 
                  link TEXT, folder_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. MINIMALIST HEADER ---
def render_header():
    st.markdown("""
        <div class="header-box">
            <h1 class="main-title">My Office <span class="title-accent">Showcase</span></h1>
            <p class="tagline">Portfolio Collection • Vol. 01</p>
        </div>
        """, unsafe_allow_html=True)

# --- 4. ADMIN SECURITY ---
st.sidebar.title("🔐 Admin Access")
# --- SET YOUR PASSWORD HERE ---
ADMIN_PASSWORD = "Adedayo" 
user_input = st.sidebar.text_input("Owner Password", type="password")
is_admin = (user_input == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("Admin Session Active")
    menu = st.sidebar.radio("Navigation", ["📂 View Gallery", "✨ Add New Project"])
else:
    st.sidebar.info("Public Gallery View")
    menu = "📂 View Gallery"

# --- 5. MAIN APP LOGIC ---
render_header()

# ADD NEW PROJECT (ADMIN ONLY)
if menu == "✨ Add New Project":
    st.markdown("## ✨ New Entry")
    with st.form("project_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        title = col1.text_input("Project Name")
        sub = col2.text_input("Role / Category")
        link = st.text_input("Live Link")
        
        st.write("---")
        desc = st_quill(html=True, placeholder="Project narrative...")
        
        files = st.file_uploader("Project Media (Max 10)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("Publish Entry"):
            if title and files:
                folder_name = title.replace(" ", "_").lower()
                path = os.path.join(SAVE_DIR, folder_name)
                if not os.path.exists(path): os.makedirs(path)
                
                for f in files:
                    with open(os.path.join(path, f.name), "wb") as file:
                        file.write(f.getbuffer())
                
                conn = sqlite3.connect('office_studio.db')
                c = conn.cursor()
                c.execute("INSERT INTO projects (header, subtitle, description, link, folder_name) VALUES (?,?,?,?,?)",
                          (title, sub, desc, link, folder_name))
                conn.commit()
                conn.close()
                st.success("Entry added to vault.")
                st.rerun()

# VIEW GALLERY (PUBLIC VIEW)
else:
    conn = sqlite3.connect('office_studio.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.warning("Vault empty. Access admin to populate.")

    for r in rows:
        with st.container():
            st.markdown(f"<div class='project-title'>{r[1]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='project-sub'>{r[2]}</div>", unsafe_allow_html=True)
            
            # --- MEDIA ---
            f_path = os.path.join(SAVE_DIR, r[5])
            if os.path.exists(f_path):
                imgs = os.listdir(f_path)
                if imgs:
                    # Massive Hero Image
                    st.image(os.path.join(f_path, imgs[0]), use_container_width=True)
                    
                    # Thumbnails
                    if len(imgs) > 1:
                        cols = st.columns(5)
                        for i, img_name in enumerate(imgs[1:6]):
                            cols[i].image(os.path.join(f_path, img_name), use_container_width=True)
            
            # --- DESCRIPTION ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(r[3], unsafe_allow_html=True)
            
            # --- ACTIONS ---
            col_web, col_spacer, col_del = st.columns([2, 6, 1])
            if r[4]:
                col_web.link_button("View Case Study", r[4])
            
            if is_admin:
                if col_del.button("🗑️", key=f"del_{r[0]}"):
                    conn = sqlite3.connect('office_studio.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM projects WHERE id=?", (r[0],))
                    conn.commit()
                    conn.close()
                    if os.path.exists(f_path): shutil.rmtree(f_path)
                    st.rerun()
            
            st.markdown("<hr style='border-color: #1A1A1A; margin: 60px 0;'>", unsafe_allow_html=True)

