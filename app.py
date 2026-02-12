import streamlit as st
import requests
import qrcode
from PIL import Image
import time
import io

# --- Configuration ---
API_URL = "http://localhost:3000"

st.set_page_config(
    page_title="Ved Infotech WhatsApp",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Ved Infotech Theme) ---
st.markdown("""
<style>
    /* --- HIDING STREAMLIT DEFAULT ELEMENTS --- */
    .stDeployButton {display:none;} /* Hide Deploy Button */
    #MainMenu {visibility: hidden;} /* Hide Three-dot Menu */
    footer {visibility: hidden;}    /* Hide Footer */

    /* --- SIDEBAR TOGGLE BUTTON CUSTOMIZATION --- */
    /* Ensure the header is visible so the toggle button shows, but transparent */
    header {
        background: transparent !important;
    }
    
    /* Style the Open/Close (Chevron) Button */
    [data-testid="collapsedControl"] {
        color: #128C7E !important; /* WhatsApp Green */
        background-color: white;
        border-radius: 50%;
        border: 1px solid #128C7E;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 5px;
        transition: all 0.3s ease;
    }
    
    [data-testid="collapsedControl"]:hover {
        background-color: #128C7E;
        color: white !important;
        transform: scale(1.1);
    }

    /* --- GLOBAL STYLES --- */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f0f2f5 0%, #e1e8ed 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* --- MAIN HEADERS --- */
    .main-header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 30px;
        background: linear-gradient(90deg, #128C7E, #25D366);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Sidebar User Info Box */
    .sidebar-user-box {
        background: #f0f2f5;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #d1d7db;
    }

    /* --- CARDS & CONTAINERS --- */
    .css-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s;
    }
    .css-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    
    /* --- BADGES --- */
    .status-badge-success {
        background-color: #dcf8c6;
        color: #075e54;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9em;
        border: 1px solid #075e54;
        display: inline-block;
    }
    .status-badge-wait {
        background-color: #fff3cd;
        color: #856404;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9em;
        border: 1px solid #856404;
        display: inline-block;
    }
    .status-badge-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9em;
        border: 1px solid #f5c6cb;
        display: inline-block;
    }

    /* --- BUTTONS --- */
    .stButton>button {
        background: linear-gradient(90deg, #008069, #00a884);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #006b58, #008f70);
        box-shadow: 0 4px 12px rgba(0,128,105,0.3);
        transform: translateY(-1px);
    }
    
    /* --- INPUT FIELDS --- */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 10px;
        background-color: #fff;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #25D366;
        box-shadow: 0 0 0 1px #25D366;
    }
</style>
""", unsafe_allow_html=True)

# --- API Helper Functions ---

def get_status():
    """Fetch status from Node backend"""
    try:
        response = requests.get(f"{API_URL}/status", timeout=2)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        return None
    return None

def get_qr():
    """Fetch QR string from Node backend"""
    try:
        response = requests.get(f"{API_URL}/qr", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('qr')
    except:
        return None

def trigger_logout():
    """Call backend logout endpoint"""
    try:
        with st.spinner("Disconnecting device and cleaning session..."):
            requests.post(f"{API_URL}/logout")
            time.sleep(3) # Give backend time to delete files and restart
            st.success("Logged out successfully")
            st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")

# --- Sidebar Logic ---
with st.sidebar:
    st.markdown("<h2 style='color:#075e54; text-align:center;'>System Panel</h2>", unsafe_allow_html=True)
    
    status_data = get_status()
    
    if status_data:
        status = status_data.get("status")
        number = status_data.get("number")
        
        if status == "CONNECTED":
            st.markdown(f"""
            <div class="sidebar-user-box">
                <span class="status-badge-success" style="margin-bottom:10px;">● Online</span>
                <h3 style="margin:5px 0 0 0; color:#333;">+{number}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            if st.button("🚪 Logout & Reset"):
                trigger_logout()
                
        elif status == "SCAN_QR":
            st.markdown(f'<div class="sidebar-user-box"><span class="status-badge-wait">● Waiting for Scan</span></div>', unsafe_allow_html=True)
        elif status == "CONNECTING":
             st.markdown(f'<div class="sidebar-user-box"><span class="status-badge-wait">● Connecting...</span></div>', unsafe_allow_html=True)
        elif status == "INITIALIZING":
             st.markdown(f'<div class="sidebar-user-box"><span class="status-badge-wait">● Initializing...</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sidebar-user-box"><span class="status-badge-error">● Disconnected</span></div>', unsafe_allow_html=True)
            
    else:
        st.markdown(f'<div class="sidebar-user-box"><span class="status-badge-error">● Server Offline</span></div>', unsafe_allow_html=True)
        st.info("Start the backend server!")

# --- Main Page Content ---

# Custom Header for Ved Infotech
st.markdown('<h1 class="main-header">Ved Infotech</h1>', unsafe_allow_html=True)

if not status_data:
    st.warning("⚠️ Backend service is not running. Please run `node server.js` in the terminal.")
    st.stop()

current_status = status_data.get("status")

# --- SCENARIO 1: NOT CONNECTED (Show QR) ---
if current_status != "CONNECTED":
    st.markdown("### 🔐 Authentication Required")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="css-card">
            <h4 style="color:#075e54;">Instructions:</h4>
            <ol style="line-height: 1.8;">
                <li>Open <b>WhatsApp</b> on your phone.</li>
                <li>Tap <b>Menu</b> (Android) or <b>Settings</b> (iOS).</li>
                <li>Tap <b>Linked Devices</b> and then <b>Link a Device</b>.</li>
                <li>Point your phone at the screen to capture the code.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Check Status"):
            st.rerun()

    with col2:
        qr_string = get_qr()
        
        if current_status == "SCAN_QR" and qr_string:
            # Generate QR Image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_string)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            st.image(img_byte_arr.getvalue(), caption="Scan me with WhatsApp", width=300)
            
            # Auto-Refresh to check for login success
            time.sleep(3)
            st.rerun()
            
        elif current_status in ["CONNECTING", "INITIALIZING"]:
            st.info("🔄 Engine is starting up... please wait a moment.")
            time.sleep(2)
            st.rerun()
        else:
            st.warning("Waiting for backend to generate QR code...")
            time.sleep(2)
            st.rerun()

# --- SCENARIO 2: CONNECTED (Show Dashboard) ---
else:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <span class="status-badge-success">✅ System Connected & Ready</span>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📝 Send Text", "📎 Send Media"])
    
    # --- Text Tab ---
    with tabs[0]:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col_form, col_info = st.columns([2, 1])
        
        with col_form:
            st.subheader("Send Text Message")
            phone_input = st.text_input("Phone Number (with Country Code)", placeholder="e.g. 15551234567")
            msg_input = st.text_area("Message Content", height=150)
            
            if st.button("🚀 Send Message", key="btn_text"):
                if not phone_input or not msg_input:
                    st.error("Please fill in both fields.")
                else:
                    with st.spinner("Sending..."):
                        payload = {"number": phone_input, "message": msg_input}
                        try:
                            res = requests.post(f"{API_URL}/send-message", json=payload)
                            if res.status_code == 200:
                                st.balloons()
                                st.success(f"Message sent to {phone_input}!")
                            else:
                                st.error(f"Failed: {res.json().get('message')}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
        
        with col_info:
            st.info("""
            **Tips:**
            - Use international format (e.g. `91987...` for India, `1555...` for US).
            - Do not use `+` or spaces.
            - Ensure the number is on WhatsApp.
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Media Tab---
    with tabs[1]:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.subheader("Send Media File")
        
        m_phone_input = st.text_input("Phone Number", key="media_phone", placeholder="e.g. 15551234567")
        uploaded_file = st.file_uploader("Upload File", type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'xlsx'])
        caption_input = st.text_input("Caption (Optional)")
        
        if st.button("📤 Upload & Send", key="btn_media"):
            if not m_phone_input or not uploaded_file:
                st.error("Phone number and file are required.")
            else:
                with st.spinner("Uploading and sending..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {'number': m_phone_input, 'caption': caption_input}
                    
                    try:
                        res = requests.post(f"{API_URL}/send-media", data=data, files=files)
                        if res.status_code == 200:
                            st.balloons()
                            st.success("File sent successfully!")
                        else:
                            st.error(f"Failed: {res.json().get('message')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)