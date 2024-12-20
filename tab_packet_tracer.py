import streamlit as st
from worker_packet_tracer import PacketWorker
from scapy.all import packet as scapy_packet

worker = PacketWorker()

def packet_tracer_tab():
    st.title("Packet Tracer")

    col1, col2 = st.columns([3, 1])

    with col1:
        interfaces = worker.load_interfaces()
        selected_interface = st.selectbox("Select an Interface:", interfaces)

    with col2:
        if st.button("Start Capture"):
            if selected_interface:
                try:
                    worker.start_capture([selected_interface])
                    st.success(f"Started capturing on {selected_interface}")
                except Exception as e:
                    st.error(f"Error starting capture: {e}")
            else:
                st.warning("Please select an interface to start capturing.")

        if st.button("Stop Capture"):
            try:
                worker.stop_packet_capture()
                st.success("Packet capture stopped.")
            except Exception as e:
                st.error(f"Error stopping capture: {e}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Packet List")
        captured_packets = worker.packets

        if captured_packets:
            packet_summaries = [
                f"[{iface}] {packet.summary()}" for iface, packet in captured_packets
            ]
            selected_packet_index = st.selectbox(
                "Select a Packet to View Details",
                range(len(packet_summaries)),
                format_func=lambda x: packet_summaries[x]
                if x < len(packet_summaries)
                else "No Packets",
            )
        else:
            st.info("No packets captured yet.")

        pcap_file = st.file_uploader("Upload a PCAP File:", type=["pcap"])
        if pcap_file:
            try:
                worker.load_pcap(pcap_file)
                st.success("PCAP file loaded successfully.")
            except Exception as e:
                st.error(f"Error loading PCAP: {e}")

        save_pcap_path = st.text_input("Save Captured Packets to PCAP (Enter Path):")
        if st.button("Save PCAP"):
            if save_pcap_path:
                try:
                    worker.save_pcap(save_pcap_path)
                    st.success(f"PCAP file saved at {save_pcap_path}")
                except Exception as e:
                    st.error(f"Error saving PCAP: {e}")
            else:
                st.warning("Please provide a valid file path.")

    with col2:
        st.markdown("### Packet Details")
        if captured_packets and selected_packet_index < len(captured_packets):
            _, packet = captured_packets[selected_packet_index]
            if isinstance(packet, scapy_packet.Packet):
                st.code(packet.show(dump=True), language="text")
            else:
                st.warning("Unable to display packet details.")
        else:
            st.write("Select a packet to view its details.")

