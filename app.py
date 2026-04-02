import streamlit as st
import pandas as pd
import sqlite3
import json
import re
from datetime import datetime

from schema import DATABASE_SCHEMA
from prompt import SYSTEM_PROMPT
from llama_index.llms.google_genai import GoogleGenAI

# ====================== CONFIG & TEMA ======================
st.set_page_config(
    page_title="SQL Genius - LKS AI 2026",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=90)
    st.title("🧠 SQL Genius")
    st.caption("Natural Language to SQL  \nLomba LKS AI Provinsi Jawa Tengah 2026")

    st.markdown("---")
    st.subheader("⚙️ Pengaturan")
    model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    selected_model = st.selectbox("Pilih Model Gemini", model_options, index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

    st.markdown("---")
    if st.button("🔄 Reset Chat", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ====================== INISIALISASI ======================
if "llm" not in st.session_state:
    try:
        db_path = "penjualan.db"

        llm = GoogleGenAI(
            model=selected_model,
            api_key=st.secrets["GEMINI_API_KEY"],
            temperature=temperature,
        )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        schema_text = DATABASE_SCHEMA
        # schema_text = "=== DATABASE SCHEMA ===\n\n"
        # for table in tables:
        #     table_name = table[0]
        #     columns = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
        #     schema_text += f"Table: {table_name}\nColumns:\n" + "\n".join([f"- {col[1]} ({col[2]})" for col in columns]) + "\n\n"
        # conn.close()

        st.session_state.llm = llm
        st.session_state.db_path = db_path
        st.session_state.schema = schema_text
        st.success(f"✅ Database '{db_path}' siap! ({len(tables)} tabel)")

    except Exception as e:
        st.error(f"❌ Gagal memuat database: {e}")
        st.stop()

# ====================== HEADER ======================
st.title("🧠 SQL Genius")
st.subheader("Tanya database dengan bahasa Indonesia")
st.caption(f"🕒 {datetime.now().strftime('%d %B %Y • %H:%M')}")

st.markdown("---")

# ====================== CHAT HISTORY ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("sql"):
            with st.expander("📜 SQL yang dihasilkan", expanded=False):
                st.code(msg["sql"], language="sql")
        if msg.get("df") is not None and not msg["df"].empty:
            st.subheader("📋 Hasil Data")
            num_rows = len(msg["df"])
            dynamic_height = min(max(num_rows * 45, 80), 500)
            styled_df = msg["df"].style.set_properties(**{'background-color': '#1e3a8a', 'color': 'white'}) \
                                      .highlight_max(axis=0, color='#22d3ee')
            st.dataframe(styled_df, use_container_width=True, height=dynamic_height)

# ====================== INPUT & PROSES ======================
if prompt := st.chat_input("Contoh: Apa saja produknya? Jumlahnya berapa?..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤖 SQL Genius sedang memproses..."):
            try:
#                 system_prompt = f"""
# """

                schema_text = st.session_state.get("schema belum dibuat.")

                system_prompt = SYSTEM_PROMPT.format(
                    schema = schema_text,
                    prompt = prompt
                )

                response = st.session_state.llm.complete(
                    system_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )

                text = response.text.strip()
                text = re.sub(r'```json|```', '', text).strip()

                result = json.loads(text)
                explanation = result.get("explanation", "Berikut hasilnya:")
                sql = result.get("sql", "").strip()

                st.markdown(explanation)

                if sql:
                    with st.expander("📜 SQL yang dihasilkan", expanded=True):
                        st.code(sql, language="sql")

                    conn = sqlite3.connect(st.session_state.db_path)
                    try:
                        df = pd.read_sql_query(sql, conn)
                    except Exception as e:
                        df = pd.DataFrame()
                        st.warning(f"Error menjalankan SQL: {e}")
                    finally:
                        conn.close()

                    if not df.empty:
                        st.subheader("📋 Hasil Data")
                        num_rows = len(df)
                        dynamic_height = min(max(num_rows * 45, 80), 500)
                        styled_df = df.style.set_properties(**{'background-color': '#1e3a8a', 'color': 'white'}) \
                                            .highlight_max(axis=0, color='#22d3ee')
                        st.dataframe(styled_df, use_container_width=True, height=dynamic_height)

                        # Jawaban Akhir
                        st.markdown("### ✅ Jawaban Akhir")
                        first_col = df.columns[0]

                        if len(df) > 1:
                            values = df[first_col].head(8).tolist()   # maksimal 8 item
                            hasil_utama = ", ".join([str(v) for v in values])
                            teks_hasil = f"{len(values)} item: {hasil_utama}"
                        else:
                            main_value = str(df.iloc[0][first_col])
                            teks_hasil = f"Hasil utama: {main_value}"

                        jawaban_teks = explanation.split(".")[0] if "." in explanation else explanation

                        st.markdown(
                            f"""
                            <div class="jawaban-akhir">
                                {jawaban_teks}<br><br>
                                {teks_hasil}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": explanation,
                    "sql": sql,
                    "df": df if 'df' in locals() else pd.DataFrame()
                })

            except Exception as e:
                st.error(f"⚠️ Terjadi kesalahan: {str(e)}")

