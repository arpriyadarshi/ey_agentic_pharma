import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt
import tempfile
from sarvamai import SarvamAI
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Pharma Agent", layout="wide")
st.title("🧬 Pharma Agentic AI (Powered by OpenAI)")

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

sarvam_client = None
if SARVAM_API_KEY:
    sarvam_client = SarvamAI(
        api_subscription_key=SARVAM_API_KEY
    )


# --- OPENAI KEY HANDLING ---
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
    os.environ["OPENAI_API_KEY"] = api_key
else:
    st.error("🚨 Missing OPENAI_API_KEY in Secrets.")
    st.stop()

# Import Backend
from backend.workflow import build_pharma_graph
from backend.rag_engine import rag_system

# Initialize RAG
try:
    rag_system.setup(api_key)
    if hasattr(rag_system, 'load_directory'): rag_system.load_directory("data")
except: pass

def transcribe_with_sarvam(audio_file):
    if not sarvam_client:
        raise ValueError("Sarvam client not initialized")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    response = sarvam_client.speech_to_text.transcribe(
        file=open(tmp_path, "rb"),
        language_code="unknown",
        model="saarika:v2.5"
    )

    # ✅ Sarvam returns a Pydantic object, not dict
    if hasattr(response, "transcript"):
        return response.transcript

    # fallback (debug)
    return str(response)



st.subheader("🎙️ Voice Input (Sarvam – Optional)")
audio_file = st.audio_input("Record your research query")

query = st.text_area(
    "Research Query",
    "Feasibility of Metformin for Anti-Aging."
)

# If audio is provided, override text query
if audio_file is not None:
    try:
        with st.spinner("🧠 Transcribing with Sarvam..."):
            voice_text = transcribe_with_sarvam(audio_file)
            st.success("🎧 Transcription complete")
            st.write("**Transcribed Query:**", voice_text)
            query = voice_text
    except Exception as e:
        st.error(f"Sarvam transcription failed: {e}")


if st.button("🚀 Run Analysis"):
    with st.status("🤖 Orchestrating Agents...", expanded=True):
        try:
            app = build_pharma_graph()
            # Run Graph
            result = app.invoke({"user_query": query, "api_key": api_key})

            agent_outputs = result["agent_outputs"]

            
            st.write("📋 **Strategic Plan:**")
            st.json(result["master_plan"])
            
            st.write("⚡ **Agent Insights:**")
            for agent, output in result["agent_outputs"].items():
                with st.expander(agent): st.markdown(output)
            
            st.subheader("📄 Final Strategy Report")
            st.markdown(result["final_report"])

            iqvia = agent_outputs.get("IQVIAInsightsAgent")

            if iqvia:
                st.subheader("📈 IQVIA Market Overview")

                df_iqvia = pd.DataFrame({
                    "Metric": ["Therapeutic Area", "Market Size (USD Bn)", "CAGR (%)"],
                    "Value": [
                        iqvia["therapeutic_area"],
                        iqvia["market_size_usd_billion"],
                        iqvia["cagr_percent"]
                    ]
                })
                df_iqvia["Value"] = df_iqvia["Value"].astype(str)
                st.table(df_iqvia)

                st.subheader("🏢 Key Competitors")
                st.dataframe(pd.DataFrame(iqvia["top_competitors"]))

            exim = agent_outputs.get("EXIMTrendsAgent")

            if exim:
                st.subheader("🌍 EXIM Exporter Volumes")

                df_exim = pd.DataFrame(exim["exporters"])
                st.dataframe(df_exim)

            st.subheader("📈 Market Growth Projection (5 Years)")

            base_size = iqvia["market_size_usd_billion"]
            cagr = iqvia["cagr_percent"] / 100

            years = [2024 + i for i in range(6)]
            market_projection = [
                round(base_size * ((1 + cagr) ** i), 2)
                for i in range(6)
            ]

            df_growth = pd.DataFrame({
                "Year": years,
                "Market Size (USD Bn)": market_projection
            })

            st.line_chart(df_growth.set_index("Year"))

            st.caption(
                f"Projected at {iqvia['cagr_percent']}% CAGR assuming stable macro conditions."
            )

            st.subheader("💰 Market Size Comparison (Peer Benchmarking)")

            peer_markets = {
                iqvia["therapeutic_area"]: iqvia["market_size_usd_billion"],
                "Cardiology": round(iqvia["market_size_usd_billion"] * 1.4, 1),
                "Oncology": round(iqvia["market_size_usd_billion"] * 2.1, 1),
                "Neurology": round(iqvia["market_size_usd_billion"] * 0.9, 1)
            }

            df_market = pd.DataFrame.from_dict(
                peer_markets,
                orient="index",
                columns=["Market Size (USD Bn)"]
            )

            st.bar_chart(df_market)

            st.caption("Peer therapeutic areas shown for relative scale comparison.")


            st.subheader("🚢 API Export Share")

            labels = [e["country"] for e in exim["exporters"]]
            sizes = [e["volume_mt"] for e in exim["exporters"]]

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct="%1.1f%%")
            ax.set_title("API Export Distribution")

            st.pyplot(fig)

            
            st.download_button("Download Report", result["final_report"], file_name="report.md")
            
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
