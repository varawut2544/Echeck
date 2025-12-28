import streamlit as st

def show(spreadsheet):
    st.header("🏗️ จัดการเครื่องจักรและอุปกรณ์")
    
    # เพิ่มเครื่องจักรใหม่
    with st.expander("➕ เพิ่มเครื่องจักรใหม่ (สร้างชีต)"):
        new_name = st.text_input("ชื่อเครื่องจักร")
        if st.button("สร้าง"):
            spreadsheet.add_worksheet(title=new_name, rows="100", cols="20")
            ws = spreadsheet.worksheet(new_name)
            ws.update_cell(1, 1, "Date")
            st.success("สร้างเครื่องจักรสำเร็จ")
            st.rerun()

    # จัดการอุปกรณ์ในเครื่องจักร
    st.divider()
    all_ws = [ws.title for ws in spreadsheet.worksheets()[1:]]
    target = st.selectbox("เลือกเครื่องจักรเพื่อจัดการอุปกรณ์", all_ws)
    sheet = spreadsheet.worksheet(target)
    
    headers = sheet.row_values(1)
    st.write(f"รายการปัจจุบัน: {', '.join(headers[1:])}")
    
    new_item = st.text_input("ชื่ออุปกรณ์ใหม่")
    if st.button("เพิ่มอุปกรณ์"):
        headers.append(new_item)
        sheet.update('A1', [headers])
        st.success("เพิ่มสำเร็จ")
        st.rerun()