import streamlit as st
import pandas as pd
import requests

def load_env_string(name: str) -> str:
    """Load string environment variable"""
    import os
    loaded = os.getenv(name)
    if loaded is None:
        raise ValueError(f"Environment variable {name} not set")
    return loaded

API_ROOT = load_env_string("MODEL_API_BASE_URL")

def fetch_data():
    return requests.get(API_ROOT).json()["value"]

st.write("Here's our first attempt at using data to create a table with an API response:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, fetch_data()]
}))