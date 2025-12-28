import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import extra_streamlit_components as cookie_manager
import streamlit.components.v1 as components
import time

# --- 1. การตั้งค่า Google Sheets (เชื่อมต่อแบบ Cache) ---
@st.cache_resource
def get_spreadsheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = "1tLONiZWLIkax5J7uC4PWTpyMEQES-rwXyUUzyy7rbL4"
    return client.open_by_key(sheet_id)

spreadsheet = get_spreadsheet()
controller = cookie_manager.CookieManager()

def main():
    # ดึงค่าจาก Cookie
    saved_user = controller.get("user")
    saved_role = controller.get("role")

    # ตรวจสอบสถานะ: ถ้าไม่มี Session แต่มี Cookie (กรณี Refresh)
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        if saved_user and saved_role and saved_user != "None":
            st.session_state['logged_in'] = True
            st.session_state['username'] = saved_user
            st.session_state['user_role'] = saved_role
            st.rerun()
        else:
            show_login_page()
    else:
        # ล็อกอินอยู่แล้ว
        if st.session_state.get('user_role'):
            show_main_app()
        else:
            st.info("กำลังเรียกข้อมูลสิทธิ์...")
            time.sleep(0.5)
            st.rerun()

def show_login_page():
    st.title("🔒 ระบบตรวจเช็คเครื่องจักร")
    
    with st.container(border=True):
        # ใช้ autocomplete="new-password" เพื่อป้องกัน Browser จำค่าเก่ามาหยอดเอง
        user = st.text_input("Username", key="login_user", autocomplete="new-password")
        pw = st.text_input("Password", type="password", key="login_pw", autocomplete="new-password")
        
        if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
            if user and pw:
                login_sheet = spreadsheet.worksheet("LogIn")
                data = login_sheet.get_all_records()
                
                # ตรวจสอบ User/PW
                user_found = next((row for row in data if str(row['User']) == user and str(row['Password']) == pw), None)
                
                if user_found:
                    # บันทึกสถานะ
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['user_role'] = str(user_found['Role'])
                    
                    # เขียน Cookie ลงเบราว์เซอร์
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
    
    # --- ปุ่ม LOGOUT พร้อม Hard Refresh (JavaScript) ---
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
        # 1. ล้าง Session Python
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # 2. ฝัง JavaScript เพื่อลบคุกกี้ฝั่ง Client และทำ Hard Reload
        # วิธีนี้จะล้างทุกอย่างที่เบราว์เซอร์จำไว้ออกไปให้หมด
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
        
        st.rerun()

    # --- เมนูหลัก ---
    menu = ["📋 Check Machine"]
    if role in ["admin", "superadmin"]:
        menu.append("🏗️ Add Machine")
    if role == "superadmin":
        menu.append("👥 User Management")
        
    choice = st.sidebar.radio("เมนู", menu)

    # การนำทางหน้า
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
        st.error(f"ไม่สามารถโหลดหน้านี้ได้: {e}")

if __name__ == "__main__":
    main()