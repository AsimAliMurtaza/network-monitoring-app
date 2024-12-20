import scapy.all as scapy
import psutil
from collections import Counter
import threading
import queue


class PacketWorker:
    def __init__(self):
        self.packets = [] 
        self.selected_interfaces = []
        self.capture_threads = []
        self.stop_capture_event = threading.Event()
        self.packet_queue = queue.Queue()
        self.protocol_stats = Counter()

    def load_interfaces(self):
        """Load available network interfaces."""
        return list(psutil.net_if_addrs().keys())

    def load_pcap(self, file_path):
        """Load packets from a PCAP file."""
        try:
            self.packets.clear()
            self.protocol_stats.clear()

            packets = scapy.rdpcap(file_path)

            self.packets = [
                (None, packet) for packet in packets if isinstance(packet, scapy.packet.Packet)
            ]

            if not self.packets:
                raise Exception("No valid packets found in the PCAP file.")

            self.update_protocol_statistics()
        except Exception as e:
            raise Exception(f"Failed to load PCAP: {e}")



    def save_pcap(self, file_path, interface=None):
        """Save captured packets to a PCAP file."""
        try:
            if interface:
                valid_packets = [
                    packet for iface, packet in self.packets 
                    if iface == interface and isinstance(packet, scapy.packet.Packet)
                ]
            else:
                valid_packets = [
                    packet for _, packet in self.packets if isinstance(packet, scapy.packet.Packet)
                ]

            if not valid_packets:
                raise Exception("No valid packets to save.")
            scapy.wrpcap(file_path, valid_packets)
        except Exception as e:
            raise Exception(f"Failed to save PCAP: {e}")


    def start_capture(self, interfaces):
        """Start capturing packets on selected interfaces."""
        if not interfaces:
            raise ValueError("No interfaces selected.")

        self.selected_interfaces = interfaces
        self.stop_capture_event.clear()
        self.capture_threads = []

        for interface in interfaces:
            thread = threading.Thread(target=self.capture_packets, args=(interface,))
            thread.daemon = True
            thread.start()
            self.capture_threads.append(thread)

    def capture_packets(self, interface):
        """Capture packets on a specific interface."""
        try:
            def process_packet(packet):
                """Process a captured packet."""
                self.packet_queue.put((interface, packet)) 
                self.packets.append((interface, packet)) 
                if hasattr(packet, "getlayer"):
                    layer = packet.getlayer(0) 
                    if layer and hasattr(layer, "name"):
                        self.protocol_stats[layer.name] += 1

            scapy.sniff(
                iface=interface,
                prn=process_packet,
                store=False,
                stop_filter=lambda _: self.stop_capture_event.is_set(),
                timeout=60,
            )
        except Exception as e:
            self.packet_queue.put((interface, f"Error: {e}"))

    def stop_packet_capture(self):
        """Stop packet capture."""
        self.stop_capture_event.set()
        for thread in self.capture_threads:
            thread.join(timeout=1)

    def apply_filters(self, protocol=None, source_ip=None, destination_ip=None):
        """Filter packets based on protocol, source IP, and destination IP."""
        filtered_packets = []
        for interface, packet in self.packets:
            if isinstance(packet, scapy.packet.Packet):  
                match = True
                if protocol and protocol.upper() not in packet.summary().upper():
                    match = False
                if source_ip and hasattr(packet, "src") and packet.src != source_ip:
                    match = False
                if destination_ip and hasattr(packet, "dst") and packet.dst != destination_ip:
                    match = False
                if match:
                    filtered_packets.append((interface, packet))
        return filtered_packets

    def update_protocol_statistics(self):
        """Update protocol statistics based on current packets."""
        self.protocol_stats.clear()
        for _, packet in self.packets:
            if hasattr(packet, "getlayer"):
                layer = packet.getlayer(0)  
                if layer and hasattr(layer, "name"):
                    self.protocol_stats[layer.name] += 1

    def get_protocol_statistics(self):
        """Return protocol statistics."""
        return self.protocol_stats
