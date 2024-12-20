import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
import datetime

def load_history(csv_file="speed_test_history.csv"):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        st.warning("No history file found.")
        return pd.DataFrame()

def plot_graphs(df):
    df['Date'] = pd.to_datetime(df['Date'])

    fig = px.line(
        df,
        x='Date',
        y=['Download Speed (Mbps)', 'Upload Speed (Mbps)'],
        labels={'value': 'Speed (Mbps)', 'Date': 'Date'},
        title='Download vs Upload Speed Over Time',
        color='variable',
    )

    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        title=dict(font=dict(size=20, color='darkblue'), x=0.5),
        legend_title=dict(text='Speed Type'),
        xaxis_title="Date",
        yaxis_title="Speed (Mbps)",
        template='plotly_white',
    )

    st.plotly_chart(fig, use_container_width=True)

def create_pdf_report(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 18
    title_style.textColor = colors.darkblue

    normal_style = styles['Normal']
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 12

    title = Paragraph("Speed Test Analysis Report", title_style)
    elements.append(title)

    intro = Paragraph(f"<b>Date of report:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style)
    elements.append(intro)

    analysis = f"""
    <b>Average Download Speed:</b> {df['Download Speed (Mbps)'].mean():.2f} Mbps<br/>
    <b>Average Upload Speed:</b> {df['Upload Speed (Mbps)'].mean():.2f} Mbps<br/>
    <b>Average Ping:</b> {df['Ping (ms)'].mean():.2f} ms<br/>
    <b>Average Jitter:</b> {df['Jitter (ms)'].mean():.2f} ms<br/>
    <b>Max Download Speed:</b> {df['Download Speed (Mbps)'].max():.2f} Mbps<br/>
    <b>Max Upload Speed:</b> {df['Upload Speed (Mbps)'].max():.2f} Mbps<br/>
    <b>Min Download Speed:</b> {df['Download Speed (Mbps)'].min():.2f} Mbps<br/>
    <b>Min Upload Speed:</b> {df['Upload Speed (Mbps)'].min():.2f} Mbps<br/>
    """
    elements.append(Paragraph(analysis, normal_style))
    elements.append(Spacer(1, 12))

    graph_file = "graph.png"
    fig = px.line(
        df,
        x='Date',
        y=['Download Speed (Mbps)', 'Upload Speed (Mbps)'],
        labels={'value': 'Speed (Mbps)', 'Date': 'Date'},
        title='Download vs Upload Speed Over Time',
    )
    fig.write_image(graph_file)

    img = RLImage(graph_file, width=500, height=300)
    elements.append(img)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def history_tab():
    csv_file = "speed_test_history.csv"
    df = load_history(csv_file)

    if not df.empty:
        st.subheader("Speed Test History")
        st.dataframe(df)

        st.subheader("Speed Test Graph")
        plot_graphs(df)

        if st.button("Generate PDF Report"):
            pdf = create_pdf_report(df)
            st.download_button(label="Download PDF Report", data=pdf, file_name="Speed_Test_Report.pdf", mime="application/pdf")

        if st.button("Export CSV"):
            st.download_button(label="Download CSV", data=df.to_csv(index=False), file_name="Speed_Test_History.csv", mime="text/csv")
    else:
        st.warning("No speed test history available. Please run a speed test to populate the data.")
