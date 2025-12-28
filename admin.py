import streamlit as st

def show(spreadsheet):
    st.header("👥 การจัดการผู้ใช้งาน")
    sheet = spreadsheet.worksheet("LogIn")
    data = sheet.get_all_records()

    st.subheader("รายชื่อผู้ใช้งาน")
    for i, row in enumerate(data):
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**User:** {row['User']}")
            c2.write(f"**Role:** {row['Role']}")
            if c3.button("ลบ", key=f"del_{i}", type="primary"):
                sheet.delete_rows(i + 2)
                st.rerun()

    with st.expander("➕ เพิ่มผู้ใช้ใหม่"):
        r = st.selectbox("ระดับสิทธิ์", ["user", "admin", "superadmin"])
        u = st.text_input("Username", key="new_u")
        p = st.text_input("Password", type="password", key="new_p")
        if st.button("บันทึกข้อมูลผู้ใช้"):
            sheet.append_row([r, u, p])
            st.success("เพิ่มสำเร็จ")
            st.rerun()