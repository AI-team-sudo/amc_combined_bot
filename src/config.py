import streamlit as st

# Topic to namespace mapping
NAMESPACE_MAP = {
    "GPMC Act": "gpmcact",
    "Compilation of Circulars": "compcirculars",
    "Tax Laws": "taxlaw"
}

# OpenAI Configuration
GPT_MODEL = "gpt-4"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# UI Configuration
PAGE_TITLE = "AMC Chatbot"
PAGE_ICON = "🏛️"
AMC_LOGO_URL = "https://ahmedabadcity.gov.in/images/amc-logo.png"
