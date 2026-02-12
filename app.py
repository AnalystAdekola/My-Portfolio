import streamlit as st
import sqlite3
import os
import shutil
from streamlit_quill import st_quill

# --- 1. CONFIGURATION & STUDIO THEME ---
st.set_page_config(page_title="My Office Showcase", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    .header-box { text-align: center; padding: 60px 0 40px 0; }
    .main-title { 
        font-family: 'Playfair Display', serif; 
        font-size: 4.5rem; color: #FFFFFF; letter-spacing: -1px; margin: 0;
    }
    .title-accent { color: #3A86FF; font-style: italic; }
    .tagline { 
        font-family: 'Inter', sans-serif; color: #666666; font-size: 1rem; 
        letter-spacing: 3px; text-transform: uppercase; margin-top: 10px; 
    }

    .project-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #FFFFFF; margin-bottom: 5px; }
    .project-sub { 
        font-family: 'Inter', sans-serif; color: #3A86FF; font-weight: 700; 
        text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem; margin-bottom: 25px; 
    }

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

# Initialize Edit State
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# --- EDIT SECTION (ADMIN ONLY) ---
if is_admin and st.session_state.edit_id:
    st.markdown(f"## ✏️ Edit Entry")
    eid = st.session_state.edit_id
    conn = sqlite3.connect('office_studio.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id=?", (eid,))
    curr = c.fetchone()
    conn.close()

    if curr:
        with st.form("edit_project_form"):
            col1, col2 = st.columns(2)
            new_title
