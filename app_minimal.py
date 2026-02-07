# 极简版 Streamlit 应用 - 最快加载速度

import streamlit as st
import json
import re
from datetime import datetime

# 页面配置 - 必须在最前面
st.set_page_config(page_title="NEXUS", layout="wide", page_icon="🧠")

# 最小化 CSS - 只保留必要样式
st.markdown("""
<style>
.stApp { background: #0a0b1e; color: #e0e6ff; }
body { background: #0a0b1e; }
</style>
""", unsafe_allow_html=True)

# Session State 初始化
st.session_state.setdefault('user', None)
st.session_state.setdefault('talents', [])
st.session_state.setdefault('last_result', None)

# 懒加载重量级库
def lazy_import():
    global pd, requests, fitz, Document
    if 'libs_loaded' not in st.session_state:
        import pandas as pd
        import requests
        import fitz
        from docx import Document
        st.session_state['libs_loaded'] = True

# 简化的工具函数
def parse_file(file):
    if not file:
        return ""
    lazy_import()
    suffix = file.name.lower().split(".")[-1]
    fb = file.read()
    try:
        if suffix == "pdf":
            return " ".join([page.get_text() for page in fitz.open(stream=fb, filetype="pdf")])
        elif suffix in ("docx", "doc"):
            return " ".join([p.text for p in Document(io.BytesIO(fb)).paragraphs])
        else:
            return fb.decode("utf-8", errors="ignore")
    except:
        return fb.decode("utf-8", errors="ignore")

def call_ai(api_key, prompt):
    lazy_import()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "[官逆]gemini-3-pro-preview",
        "messages": [
            {"role": "system", "content": "You are a headhunting assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    try:
        r = requests.post("https://api.gemai.cc/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            c = r.json()["choices"][0]["message"]["content"]
            start, end = c.find('{'), c.rfind('}')
            return json.loads(c[start:end+1]) if start != -1 else None
        return None
    except:
        return None

# 登录页面
if not st.session_state['user']:
    st.title("🧠 NEXUS")
    st.caption("AI-Driven Talent Intelligence")
    u = st.text_input("用户名")
    if st.button("进入", use_container_width=True):
        if u:
            st.session_state['user'] = u
            st.rerun()
    st.stop()

# 主界面
st.sidebar.title("功能")
menu = st.sidebar.radio("", ["打标", "看板"], label_visibility="collapsed")
api_key = st.sidebar.text_input("API Key", type="password")

if menu == "打标":
    st.title("人才打标")
    cv_f = st.file_uploader("上传简历")
    nt_f = st.text_area("沟通记录")
    
    if st.button("开始打标", use_container_width=True) and (cv_f or nt_f):
        with st.spinner("分析中..."):
            cv_txt = parse_file(cv_f) if cv_f else ""
            prompt = f"""
            分析候选人信息并返回 JSON：
            Notes: {nt_f}
            CV: {cv_txt[:2000]}
            
            返回格式：
            {{
              "name": "姓名",
              "company": "公司",
              "title": "职位",
              "summary": "摘要"
            }}
            """
            res = call_ai(api_key or "sk-5gdJnwOpb24drogckyzMQg4mId442uXTl0V8JNYcQdHm1FZH", prompt)
            if res:
                st.session_state['last_result'] = res
                st.rerun()
    
    if st.session_state['last_result']:
        res = st.session_state['last_result']
        st.subheader(res.get('name', '未知'))
        st.write(f"**公司**: {res.get('company', '—')}")
        st.write(f"**职位**: {res.get('title', '—')}")
        st.write(f"**摘要**: {res.get('summary', '—')}")
        if st.button("入库", use_container_width=True):
            st.session_state['talents'].append(res)
            st.session_state['last_result'] = None
            st.success("已入库")

elif menu == "看板":
    st.title("人才库")
    if st.session_state['talents']:
        lazy_import()
        df = pd.DataFrame(st.session_state['talents'])
        st.dataframe(df, use_container_width=True)
        st.download_button("导出", data=json.dumps(st.session_state['talents'], ensure_ascii=False), file_name="talents.json")
    else:
        st.info("暂无数据")
