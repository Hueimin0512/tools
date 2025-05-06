
import pandas as pd
import streamlit as st
import xlsxwriter
import io
import os

st.write(f"✅ pandas 版本：{pd.__version__}")
st.write(f"✅ streamlit 版本：{st.__version__}")
st.write(f"✅ xlsxwriter 版本：{xlsxwriter.__version__}")
st.title("📦 点货记录小工具")

# 保存数据的CSV文件
DATA_FILE = "data.csv"

st.markdown("请在下面输入您的点货数据：")

# 可选择的 DESCRIPTION 列表
description_options = [
    "5911","5912-2","5912-2TSK","5912-3","5912-3 TSK",
    "5912-4","5912-6","5913-3","5913-3TSK","5913-4",
    "5914-2","5914-3","5915-3","5915-4","5916","5917",
    "5922","5923","5938-6","5935-1","5935-2",
    "5935-3","5935-4","5935-5","5935-6","5942-1",
    "5942-2","5942-3","5942-4","5942-5 ","5942-6",
    "5942-8","5963-1","5963-2","5963-2A","5963-3",
    "5963-3S","5963-4","5963-5","5963-6","5963-7",
    "5963-8","5973-1","5973-2","5973-2A","5973X-2A",
    "5973-3","5973X-3","5973-4","5973-4P","5973-5",
    "5973-5P","5973-6","5973-6L","5973-7","5973-7C",
    "5973-8","5973-8C","5973-9","5973-9P","7981A",
    "7981AX","DOG1515-L","DOG2015-L","DOG1515-C","DOG2015-C",
    "DOG1515-M","DOG2015-M","PAWMASTER","TY1500","TY1500-L",
    "TY1800","TY2000","TYSPOTATO","DOG1515-CM","DOG1515-LM",
    "CAT2018-F","CAT1018-F","CAT2026-F","CAT2026-2F","CAT2026-3F",
    "CAT1026-F","CAT1026-2F","CAT1026-3F","CAT0926-F","CAT0926-2F",
    "CAT0926-3F","CAT0826-F","CAT0826-2F","CAT0826-3F","CAT2026-OM",
    "CAT1026-OM","CAT0826-OM","CAT2026-CS","CAT1026-CS","CAT0926-CS",
    "CAT2026-RG","CAT1026-RG","CAT2026-MM","CAT2026-MC","CAT1026-MC",
    "CAT1026-C","CAT2026-OC","CAT1026-OC","CAT2023-C","CAT1023-C",
    "CAT0723-C","CAT2023-OC","CAT2023-3OC","CAT1023-OC","CAT0723-OC","CAT06523-OC",
    "CAT2023-F","CAT1023-F","CAT0723-M","CAT1023-M","CAT2023-M","CAT2023-MC",
]

# 初始化空数据表
if "df" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.df = pd.read_csv(DATA_FILE)
    else:
        st.session_state.df = pd.DataFrame(columns=[
            "ITEM", "DESCRIPTION", "STANDARD WEIGHT PER BAG",
            "NO OF BAG PER PALLET", "QUANTITY NO OF PELLET",
            "QUANTITY NO OF BAG ITEM", "TOTAL", "TOTAL WEIGHT", "remark"
        ])

st.header("输入点货资料")

description = st.selectbox("DESCRIPTION (可选或手动输入)", options=[""] + description_options)
custom_description = st.text_input("若无，请手动输入DESCRIPTION")
final_description = custom_description if custom_description else description

standard_weight = st.number_input("STANDARD WEIGHT PER BAG", min_value=0.0, step=0.01)
bag_per_pallet_input = st.text_input("NO OF BAG PER PALLET (可输入加法如 5+6)")
pallet_qty_input = st.text_input("QUANTITY NO OF PELLET (可输入加法如 2+3)")
bag_item_qty_input = st.text_input("QUANTITY NO OF BAG ITEM (可输入加法如 1+2)")

remark = st.text_input("remark")

def eval_input(text):
    try:
        return eval(text)
    except:
        return 0

if st.button("添加记录"):
    bag_per_pallet = eval_input(bag_per_pallet_input)
    pallet_qty = eval_input(pallet_qty_input)
    bag_item_qty = eval_input(bag_item_qty_input)

    total = bag_per_pallet * pallet_qty + bag_item_qty
    total_weight = total * standard_weight

    new_row = {
        "ITEM": len(st.session_state.df) + 1,
        "DESCRIPTION": final_description,
        "STANDARD WEIGHT PER BAG": standard_weight,
        "NO OF BAG PER PALLET": bag_per_pallet,
        "QUANTITY NO OF PELLET": pallet_qty,
        "QUANTITY NO OF BAG ITEM": bag_item_qty,
        "TOTAL": total,
        "TOTAL WEIGHT": total_weight,
        "remark": remark
    }

    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.df.to_csv(DATA_FILE, index=False)
    st.success("已添加并保存！")

st.header("📋 当前记录")

# ➡️ 表格展示
if not st.session_state.df.empty:
    st.markdown(st.session_state.df.to_html(index=False), unsafe_allow_html=True)

    # ➡️ 删除功能
    delete_index = st.number_input("输入要删除的行号 (ITEM)", min_value=1, max_value=int(st.session_state.df["ITEM"].max()), step=1)
    if st.button("删除这行"):
        st.session_state.df = st.session_state.df[st.session_state.df["ITEM"] != delete_index].reset_index(drop=True)
        st.session_state.df["ITEM"] = st.session_state.df.index + 1
        st.session_state.df.to_csv(DATA_FILE, index=False)
        st.success(f"已删除第 {delete_index} 行！")
        # 删除后重新载入数据，确保刷新
        st.session_state.df = pd.read_csv(DATA_FILE)

# ➡️ 导出 Excel
def to_excel(df):
    if df.empty:
        df = pd.DataFrame({"提示": ["当前没有记录"]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    output.seek(0)
    return output.getvalue()

# 确保 df 是有效的
df = st.session_state.get('df', pd.DataFrame())

# 打印 DataFrame，确保数据正确
st.write("✅ 当前的 DataFrame：", df)

# 生成 Excel 数据
excel_data = to_excel(df)

# ✅ 下载按钮
st.download_button(
    label="下载为Excel",
    data=excel_data,
    file_name="点货记录.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
