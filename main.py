import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import extra_streamlit_components as cookie_manager
import streamlit.components.v1 as components
import time

# --- 1. การตั้งค่าการเชื่อมต่อ Google Sheets (รองรับ Cloud Secrets และ Local JSON) ---
@st.cache_resource
def get_spreadsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    # ตรวจสอบว่ารันบน Streamlit Cloud หรือไม่
    if "gcp_service_account" in st.secrets:
        creds_info = dict(st.secrets["gcp_service_account"])
        # แปลง \n ใน Private Key ให้ถูกต้อง
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    else:
        # กรณีรันในเครื่องตัวเอง ให้ใช้ไฟล์ credentials.json
        try:
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        except Exception as e:
            st.error("ไม่พบการตั้งค่า Secrets หรือไฟล์ credentials.json")
            st.stop()
            
    client = gspread.authorize(creds)
    sheet_id = "1tLONiZWLIkax5J7uC4PWTpyMEQES-rwXyUUzyy7rbL4"
    return client.open_by_key(sheet_id)

spreadsheet = get_spreadsheet()
controller = cookie_manager.CookieManager()

def main():
    # ดึงค่าจาก Cookie เพื่อเช็คสถานะการจำล็อกอิน
    saved_user = controller.get("user")
    saved_role = controller.get("role")

    # กรณีที่ 1: ไม่ได้ Login ใน Session แต่มีคุกกี้ค้างอยู่ (เช่น กด Refresh)
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        if saved_user and saved_role and saved_user != "None":
            st.session_state['logged_in'] = True
            st.session_state['username'] = saved_user
            st.session_state['user_role'] = saved_role
            st.rerun()
        else:
            show_login_page()
    
    # กรณีที่ 2: สถานะ Login ปกติ
    else:
        if st.session_state.get('user_role'):
            show_main_app()
        else:
            st.info("กำลังโหลดข้อมูลสิทธิ์...")
            time.sleep(0.5)
            st.rerun()

def show_login_page():
    st.title("🔒 ระบบตรวจเช็คเครื่องจักร")
    
    with st.container(border=True):
        # ป้องกันเบราว์เซอร์เติมข้อมูลเก่าอัตโนมัติ
        user = st.text_input("Username", key="login_user", autocomplete="new-password")
        pw = st.text_input("Password", type="password", key="login_pw", autocomplete="new-password")
        
        if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
            if user and pw:
                login_sheet = spreadsheet.worksheet("LogIn")
                data = login_sheet.get_all_records()
                
                # ตรวจสอบ Username และ Password
                user_found = next((row for row in data if str(row['User']) == user and str(row['Password']) == pw), None)
                
                if user_found:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['user_role'] = str(user_found['Role'])
                    
                    # บันทึกลงคุกกี้
                    controller.set("user", user, key="set_u")
                    controller.set("role", str(user_found['Role']), key="set_r")
                    
                    st.success("ล็อกอินสำเร็จ!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            else:
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

def show_main_app():
    role = st.session_state.get('user_role')
    user = st.session_state.get('username')
    
    st.sidebar.title(f"👤 {user}")
    st.sidebar.write(f"สิทธิ์: `{role}`")
    st.sidebar.divider()
    
    # --- ระบบ LOGOUT พร้อม Hard Refresh ผ่าน JavaScript ---
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
        # ล้าง Session ใน Python
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # สั่งลบคุกกี้และรีโหลดหน้าเว็บใหม่ทั้งหมดผ่าน JavaScript
        js_code = f"""
            <script>
                document.cookie = "user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                document.cookie = "role=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                setTimeout(function(){{
                    window.location.href = window.location.origin + window.location.pathname;
                }}, 300);
            </script>
        """
        components.html(js_code, height=0)
        st.stop()

    # --- เมนูการใช้งาน ---
    menu = ["📋 Check Machine"]
    if role in ["admin", "superadmin"]:
        menu.append("🏗️ Add Machine")
    if role == "superadmin":
        menu.append("👥 User Management")
        
    choice = st.sidebar.radio("เมนูหลัก", menu)

    # นำทางไปยังไฟล์โมดูลต่างๆ
    try:
        if choice == "📋 Check Machine":
            import check
            check.show(spreadsheet)
        elif choice == "🏗️ Add Machine":
            import addmachine
            addmachine.show(spreadsheet)
        elif choice == "👥 User Management":
            import admin
            admin.show(spreadsheet)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหน้า: {e}")

if __name__ == "__main__":
    main()