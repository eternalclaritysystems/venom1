# src/app.py
import streamlit as st
import pandas as pd

def run_app(df: pd.DataFrame):
    st.title("Crowd Density Estimator")
    st.write(df.head())
