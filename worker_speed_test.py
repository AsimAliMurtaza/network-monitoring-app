import time
import speedtest_cli
import socket
import numpy as np
import csv
import datetime
import os

class SpeedTestWorker:
    def __init__(self):
        super().__init__()
        self.progress_value = 0
        self.isp = None
        self.server = None
        self.download_speed = 0
        self.upload_speed = 0
        self.ping_value = 0
        self.jitter = 0
        self.download_speeds = []
        self.upload_speeds = []
        self.server_name = None
        self.server_country = None

    def get_progress(self):
        return self.progress_value

    def get_isp_server_info(self):
        return self.isp, self.server_name

    def get_speeds(self):
        return self.download_speed, self.upload_speed

    def get_ping(self):
        return self.ping_value

    def get_jitter(self):
        return self.jitter

    def start_test(self):
        st = speedtest_cli.Speedtest()

        self.isp = st.config['client']['isp']
        best_server = st.get_best_server()
        self.server_name = best_server['name']
        self.server_country = best_server['country']

        ping_times = self.ping_test()
        self.ping_value = np.mean(ping_times) if ping_times else None

        self.jitter = self.calculate_jitter(ping_times)

        self.test_speeds(st)

        self.save_test_results()

    def ping_test(self, host="8.8.8.8", port=53, timeout=1):
        ping_times = []
        for _ in range(2):  
            ping_time = self.perform_ping(host, port, timeout)
            if ping_time is not None:
                ping_times.append(ping_time)
            time.sleep(0.1) 
        return ping_times

    def perform_ping(self, host, port, timeout):
        try:
            start_time = time.time()
            socket.create_connection((host, port), timeout=timeout)
            end_time = time.time()
            return (end_time - start_time) * 1000 
        except Exception:
            return None

    def calculate_jitter(self, ping_times):
        if len(ping_times) < 2:
            return 0
        differences = [abs(ping_times[i] - ping_times[i-1]) for i in range(1, len(ping_times))]
        return np.mean(differences)

    def test_speeds(self, st):
        for i in range(2): 
            try:
                download_speed = st.download() / 1e6 
                self.download_speeds.append(download_speed)
            except Exception as e:
                print(f"Error during download speed test: {e}")
            time.sleep(0.1) 

        for i in range(2): 
            try:
                upload_speed = st.upload() / 1e6  
                self.upload_speeds.append(upload_speed)
            except Exception as e:
                print(f"Error during upload speed test: {e}")
            time.sleep(0.1)  

    def save_test_results(self):
        test_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        csv_file = "speed_test_history.csv"
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Date', 'Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping (ms)', 'Jitter (ms)', 'Server', 'ISP'])

            writer.writerow([test_date, np.mean(self.download_speeds), np.mean(self.upload_speeds), self.ping_value, self.jitter, self.server_name, self.isp])
