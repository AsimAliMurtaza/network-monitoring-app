import streamlit as st
import plotly.graph_objects as go
from worker_speed_test import SpeedTestWorker 
import numpy as np

def speedtest():
    st.write("Test the network's performance and visualize real-time speed data.")

    status_placeholder = st.empty()
    isp_placeholder = st.empty()

    col1, col2, col3 = st.columns(3)
    download_placeholder = col1.empty()
    upload_placeholder = col2.empty()
    ping_placeholder = col3.empty()

    jitter_placeholder = st.empty()

    progress_bar = st.progress(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode="lines+markers", name="Download Speed", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=[], y=[], mode="lines+markers", name="Upload Speed", line=dict(color="blue")))
    fig.update_layout(
        title="Real-Time Speed Plot",
        xaxis_title="Time (s)",
        yaxis_title="Speed (Mbps)",
        template="plotly_white",
        legend=dict(yanchor="top", y=1.15, xanchor="left", x=0.01),
        yaxis=dict(range=[0, 100])  
    )
    plot_placeholder = st.empty()

    start_button = st.button("Start Speed Test", key="start_test")

    if start_button:
        worker = SpeedTestWorker()

        status_placeholder.info("Testing... Please wait.")
        isp_placeholder.text("ISP: --, Server: --")
        progress_bar.progress(0)

        worker.start_test()  

        x_data = list(range(len(worker.download_speeds)))
        download_data = worker.download_speeds
        upload_data = worker.upload_speeds

        status_placeholder.success("Test Completed!")
        isp_placeholder.text(f"ISP: {worker.isp}, Server: {worker.server_name} ({worker.server_country})")
        download_placeholder.metric("Download Speed", f"{np.mean(download_data):.2f} Mbps")
        upload_placeholder.metric("Upload Speed", f"{np.mean(upload_data):.2f} Mbps")
        ping_placeholder.metric("Ping", f"{worker.ping_value:.2f} ms") 
        jitter_placeholder.metric("Jitter", f"{worker.jitter:.2f} ms")  

        for i, (download_speed, upload_speed) in enumerate(zip(download_data, upload_data)):
            progress_bar.progress(int((i + 1) / len(download_data) * 100))

            fig.data[0].x = x_data[: i + 1]
            fig.data[0].y = download_data[: i + 1]
            fig.data[1].x = x_data[: i + 1]
            fig.data[1].y = upload_data[: i + 1]

            max_y = max(max(download_data[: i + 1]), max(upload_data[: i + 1]), 5) + 5
            fig.update_yaxes(range=[0, max_y])

            plot_placeholder.plotly_chart(fig, use_container_width=True)

        progress_bar.progress(100)
