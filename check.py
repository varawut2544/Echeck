import streamlit as st
from datetime import datetime

def show(spreadsheet):
    st.header("📋 บันทึกการตรวจเช็ค")
    all_sheets = spreadsheet.worksheets()
    machine_list = [ws.title for ws in all_sheets[1:]]
    
    if not machine_list:
        st.info("ยังไม่มีข้อมูลเครื่องจักร")
        return

    selected_machine = st.selectbox("เลือกเครื่องจักร", machine_list)
    sheet = spreadsheet.worksheet(selected_machine)
    header = sheet.row_values(1)
    
    if len(header) < 2:
        st.warning("ยังไม่ได้กำหนดรายการอุปกรณ์")
        return

    items = header[1:]
    results = [datetime.now().strftime('%Y-%m-%d %H:%M')]

    with st.form("check_form"):
        st.write(f"ตรวจสอบอุปกรณ์สำหรับ: **{selected_machine}**")
        for i, item in enumerate(items):
            col_l, col_r = st.columns([3, 2])
            col_l.markdown(f"**{item}**")
            status = col_r.radio("สถานะ", [1, 0], format_func=lambda x: "ดี" if x==1 else "เสีย", key=f"ch_{i}", horizontal=True, label_visibility="collapsed")
            results.append(status)
        
        if st.form_submit_button("บันทึกข้อมูล", use_container_width=True):
            sheet.append_row(results)
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")