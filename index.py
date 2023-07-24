from flask import Flask, render_template
import psutil 
import GPUtil 
import shutil
from hurry.filesize import size
from datetime import datetime 
import time
import socket

app = Flask(__name__)

def get_ssid():
    addrs = psutil.net_if_addrs()
    return addrs.keys()


#disk_readage = size(psutil.disk_io_counters().read_bytes / psutil.disk_io_counters().read_time)
cache = {}
cache["prev_read_bytes_disk"] = -1
cache["prev_write_bytes_disk"] = -1
cache["prev_bytes_recv_network"] = -1
cache["prev_bytes_sent_network"] = -1

cache["init_time"] = -1

@app.route("/")
def index():
    if cache["init_time"] ==  -1:
        cache["init_time"] = psutil.disk_io_counters().read_time 
    ts = psutil.disk_io_counters().read_time - cache["init_time"]
    if cache["prev_read_bytes_disk"] == -1:
        cache["prev_read_bytes_disk"] = psutil.disk_io_counters().read_bytes
    bytes_read_disk = psutil.disk_io_counters().read_bytes-cache["prev_read_bytes_disk"]
    cache["prev_read_bytes_disk"] = psutil.disk_io_counters().read_bytes

    if cache["prev_write_bytes_disk"] == -1:
        cache["prev_write_bytes_disk"] = psutil.disk_io_counters().write_bytes
    bytes_write_disk = psutil.disk_io_counters().write_bytes-cache["prev_write_bytes_disk"]
    cache["prev_write_bytes_disk"] = psutil.disk_io_counters().write_bytes

    if cache["prev_bytes_recv_network"] == -1:
        cache["prev_bytes_recv_network"] = psutil.net_io_counters().bytes_recv
    bytes_recv_network = psutil.net_io_counters().bytes_recv-cache["prev_bytes_recv_network"]
    cache["prev_bytes_recv_network"] = psutil.net_io_counters().bytes_recv

    if cache["prev_bytes_sent_network"] == -1:
        cache["prev_bytes_sent_network"] = psutil.net_io_counters().bytes_sent
    bytes_sent_network = psutil.net_io_counters().bytes_sent-cache["prev_bytes_sent_network"]
    cache["prev_bytes_sent_network"] = psutil.net_io_counters().bytes_sent
    if ts == 0:
        ts = 1
    return f"""
    <html>
    <style>
        h1 {{
            font-family:monospace;
            color:white
        }}
        body {{
            background-color:black
        }}
      
    </style>

    <head>
      <meta http-equiv="refresh" content="3">
    </head>
        <h1>TIME: {datetime.now().strftime("%H:%M:%S")} {datetime.now().strftime("%m/%d/%Y")}</h1>
        <h1>CPU TEMP: {round(psutil.sensors_temperatures()["coretemp"][0].current,2)}° C</h1>
        <h1>CPU USSAGE: {round(psutil.cpu_percent(1),2)}% </h1>
    <hr>
        <h1>GPU TEMP: {round(GPUtil.getGPUs()[0].temperature,2)}° C</h1>
        <h1>GPU USSAGE: {round((GPUtil.getGPUs()[0].load) * 100,2)}% </h1>
        <h1>VRAM USSAGE: {round(GPUtil.getGPUs()[0].memoryUsed / GPUtil.getGPUs()[0].memoryTotal * 100,2)}% </h1>
    <hr> 
        <h1>RAM USSAGE: {round(psutil.virtual_memory()[3]/1000000000,2)}GB - {psutil.virtual_memory()[2]}% </h1>
    <hr> 
        <h1>💽 Disk Space: {size(shutil.disk_usage("/").used)}/{size(shutil.disk_usage("/").total)} - {round(((shutil.disk_usage("/").used/shutil.disk_usage("/").total) * 100),2)}% USED</h1>
        <div style="width:90%; border: 2px solid white;"> 
            <div id='a' style="width:{(shutil.disk_usage("/").used/shutil.disk_usage("/").total)*100}%;background:white;height:20px;position:relative"></div>
        </div>
        <h1>Read: {size((bytes_read_disk)/ts)}/s</h1>
        <h1>Write: {size((bytes_write_disk)/ts)}/s</h1>
    <hr>
        <h1>🌐 Network: {socket.gethostbyname(socket.gethostname())}
         <h1>Send: {size((bytes_sent_network)/ts)}/s</h1>
        <h1>Recieve: {size((bytes_recv_network)/ts)}/s</h1>
    </html>"""

if __name__ == "__main__":
    app.run(debug=True) 


