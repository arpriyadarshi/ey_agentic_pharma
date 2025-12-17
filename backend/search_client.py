import streamlit as st
from tavily import TavilyClient

TAVILY_AVAILABLE = False
tavily = None

try:
    api_key = st.secrets["TAVILY_API_KEY"]
    tavily = TavilyClient(api_key=api_key)
    TAVILY_AVAILABLE = True
except KeyError:
    TAVILY_AVAILABLE = False
