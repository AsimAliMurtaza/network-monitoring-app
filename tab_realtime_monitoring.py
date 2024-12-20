import streamlit as st
import psutil
import time
import socket
import plotly.graph_objects as go

def show_realtime_monitoring():
    if "upload_data" not in st.session_state:
        st.session_state.upload_data = []
    if "download_data" not in st.session_state:
        st.session_state.download_data = []
    if "latency_data" not in st.session_state:
        st.session_state.latency_data = []
    if "time_data" not in st.session_state:
        st.session_state.time_data = []
        st.session_state.counter = 0
    if "monitoring" not in st.session_state:
        st.session_state.monitoring = False

    col1, col2, col3 = st.columns(3)
    with col1:
        upload_placeholder = st.metric("Upload Traffic Since Last Boot", "-- Mbps")
    with col2:
        download_placeholder = st.metric("Download Traffic Since Last Boot", "-- Mbps")
    with col3:
        latency_placeholder = st.metric("Latency", "-- ms")

    plot_placeholder = st.empty()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Start Monitoring"):
            st.session_state.monitoring = True
    with col2:
        if st.button("Stop Monitoring"):
            st.session_state.monitoring = False

    while st.session_state.monitoring:
        io_counters = psutil.net_io_counters(pernic=False)
        upload_speed = io_counters.bytes_sent / (1024 * 1024) 
        download_speed = io_counters.bytes_recv / (1024 * 1024) 

        try:
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            latency = (time.time() - start_time) * 1000  
        except Exception:
            latency = float('inf')

        st.session_state.upload_data.append(upload_speed)
        st.session_state.download_data.append(download_speed)
        st.session_state.latency_data.append(latency)
        st.session_state.time_data.append(st.session_state.counter)
        st.session_state.counter += 1

        if len(st.session_state.time_data) > 60:
            st.session_state.upload_data.pop(0)
            st.session_state.download_data.pop(0)
            st.session_state.latency_data.pop(0)
            st.session_state.time_data.pop(0)

        upload_placeholder.metric("Upload Traffic Since Last Boot", f"{upload_speed:.2f} Mbps")
        download_placeholder.metric("Download Traffic Since Last Boot", f"{download_speed:.2f} Mbps")
        latency_placeholder.metric("Latency", f"{latency:.2f} ms")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.time_data, y=st.session_state.upload_data,
                                 mode="lines+markers", name="Upload (Mbps)", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=st.session_state.time_data, y=st.session_state.download_data,
                                 mode="lines+markers", name="Download (Mbps)", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=st.session_state.time_data, y=st.session_state.latency_data,
                                 mode="lines+markers", name="Latency (ms)", line=dict(color="green")))

        fig.update_layout(
            title="Real-Time Monitoring",
            xaxis_title="Time (s)",
            yaxis_title="Values",
            legend_title="Metrics",
            template="plotly_white",
            yaxis=dict(
                title="Mbps / ms",
                tickformat=".2f"  
            )
        )

        plot_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(1)

        if not st.session_state.monitoring:
            break
