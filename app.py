import streamlit as st
import sqlite3
import os
import shutil
from streamlit_quill import st_quill

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="My Office Showcase", layout="wide")

# Custom CSS for the "Brilliant" feel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Inter:wght@400;700&display=swap');
    
    .main { background-color: #ffffff; }
    .stButton>button { border-radius: 20px; font-weight: bold; }
    
    /* Project Card Styling */
    .project-container {
        border: 1px solid #f0f0f0;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 50px;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Multicolor Header Styling */
    .header-box { text-align: center; padding: 40px 0; background: #fcfcfc; border-radius: 30px; margin-bottom: 30px; }
    .main-title { font-family: 'Bungee', cursive; font-size: 4.5rem; letter-spacing: 2px; margin: 0; line-height: 1; }
    .color-red { color: #FF3131; }
    .color-blue { color: #3A86FF; }
    .color-green { color: #38B000; }
    .color-white { color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    
    .tagline { font-family: 'Inter', sans-serif; color: #64748B; font-size: 1.2rem; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

SAVE_DIR = "showcase_media"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('office_vault_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  header TEXT, subtitle TEXT, description TEXT, 
                  link TEXT, folder_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. THE BEAUTIFUL MULTICOLOR HEADER ---
def render_header():
    st.markdown("""
        <div class="header-box">
            <h1 class="main-title">
                <span class="color-red">M</span><span class="color-blue">y</span> 
                <span class="color-green">O</span><span class="color-white">f</span><span class="color-red">f</span><span class="color-blue">i</span><span class="color-green">c</span><span class="color-red">e</span>
            </h1>
            <h1 class="main-title" style="font-size: 3.5rem;">
                <span class="color-blue">S</span><span class="color-green">h</span><span class="color-white">o</span><span class="color-red">w</span><span class="color-blue">c</span><span class="color-green">a</span><span class="color-red">s</span><span class="color-blue">e</span>
            </h1>
            <p class="tagline">Built with AI • My Personal Masterpiece • Designed to Shine</p>
        </div>
        """, unsafe_allow_html=True)

# --- 4. ADMIN SECURITY ---
st.sidebar.title("🔐 Admin Access")
# --- !!! CHANGE THE PASSWORD BELOW !!! ---
ADMIN_PASSWORD = "your_secret_password" 
user_input = st.sidebar.text_input("Owner Password", type="password")
is_admin = (user_input == ADMIN_PASSWORD)

if is_admin:
    st.sidebar.success("Welcome back, Boss!")
    menu = st.sidebar.radio("Navigation", ["📂 View Gallery", "✨ Add New Project"])
else:
    st.sidebar.info("Viewer Mode (Locked)")
    menu = "📂 View Gallery"

# --- 5. MAIN APP LOGIC ---
render_header()

# ADD NEW PROJECT (ADMIN ONLY)
if menu == "✨ Add New Project":
    st.markdown("### 📝 Create a New Project Entry")
    with st.form("project_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        title = col1.text_input("Project Name")
        sub = col2.text_input("Your Role / Category")
        link = st.text_input("Live Link (Optional)")
        
        st.write("---")
        desc = st_quill(html=True, placeholder="Write your project story here...")
        
        st.write("---")
        files = st.file_uploader("Upload up to 10 Images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("Publish to My Office"):
            if title and files:
                folder_name = title.replace(" ", "_").lower()
                path = os.path.join(SAVE_DIR, folder_name)
                if not os.path.exists(path): os.makedirs(path)
                
                for f in files:
                    with open(os.path.join(path, f.name), "wb") as file:
                        file.write(f.getbuffer())
                
                conn = sqlite3.connect('office_vault_final.db')
                c = conn.cursor()
                c.execute("INSERT INTO projects (header, subtitle, description, link, folder_name) VALUES (?,?,?,?,?)",
                          (title, sub, desc, link, folder_name))
                conn.commit()
                conn.close()
                st.success("Project published beautifully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Title and Images are required!")

# VIEW GALLERY (PUBLIC VIEW)
else:
    conn = sqlite3.connect('office_vault_final.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.warning("Your showcase is currently empty. Use the admin password to add projects!")

    for r in rows:
        # r[0]=id, r[1]=title, r[2]=sub, r[3]=desc, r[4]=link, r[5]=folder
        with st.container():
            st.markdown(f"## {r[1]}")
            st.markdown(f"<p style='color:#3a7bd5; font-size:1.2rem; font-weight:bold; margin-top:-15px;'>{r[2]}</p>", unsafe_allow_html=True)
            
            # --- BOLD MEDIA LAYOUT ---
            f_path = os.path.join(SAVE_DIR, r[5])
            if os.path.exists(f_path):
                imgs = os.listdir(f_path)
                if imgs:
                    # Top Bold Hero Image
                    st.image(os.path.join(f_path, imgs[0]), use_container_width=True)
                    
                    # Smaller Grid for rest of images
                    if len(imgs) > 1:
                        cols = st.columns(4)
                        for i, img_name in enumerate(imgs[1:5]): # Show next 4
                            cols[i].image(os.path.join(f_path, img_name), use_container_width=True)
            
            # --- DESCRIPTION ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(r[3], unsafe_allow_html=True)
            
            # --- FOOTER BUTTONS ---
            col_web, col_spacer, col_del = st.columns([2, 6, 1])
            if r[4]:
                col_web.link_button("🌐 Visit Project", r[4])
            
            if is_admin:
                if col_del.button("🗑️", key=f"del_{r[0]}"):
                    conn = sqlite3.connect('office_vault_final.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM projects WHERE id=?", (r[0],))
                    conn.commit()
                    conn.close()
                    if os.path.exists(f_path): shutil.rmtree(f_path)
                    st.rerun()
            
            st.markdown("<hr style='margin: 40px 0;'>", unsafe_allow_html=True)
