import streamlit as st
from tab_realtime_monitoring import show_realtime_monitoring
from tab_speed_test import speedtest
from tab_packet_tracer import packet_tracer_tab
from tab_history_window import history_tab

st.set_page_config(page_title="Advanced Network Monitor", layout="wide")

st.title("Network Monitoring Tool")

tabs = st.tabs(["Real-Time Monitoring", "Speed Test", "History", "Packet Capture"])

with tabs[0]:
    try:
        show_realtime_monitoring()
    except Exception as e:
        st.error(f"An error occurred in Real-Time Monitoring: {str(e)}")

with tabs[1]:
    try:
        speedtest()
    except Exception as e:
        st.error(f"An error occurred in Speed Test: {str(e)}")

with tabs[2]:
    try:
        history_tab()
    except Exception as e:
        st.error(f"An error occurred in History: {str(e)}")

with tabs[3]:
    try:
        packet_tracer_tab()
    except Exception as e:
        st.error(f"An error occurred in Packet Capture: {str(e)}")