import socket
import time

DNS_SERVERS = {
    "Cloudflare": ("1.1.1.1", "1.0.0.1"),
    "Google": ("8.8.8.8", "8.8.4.4"),
    "Quad9": ("9.9.9.9", "149.112.112.112"),
    "OpenDNS": ("208.67.222.222", "208.67.220.220"),
}

def ping(host, timeout=1):
    try:
        start = time.time()
        socket.create_connection((host, 53), timeout=timeout)
        return (time.time() - start) * 1000
    except Exception:
        return float('inf')

def find_best_dns():
    best_server = None
    best_ping = float('inf')
    for name, (primary, secondary) in DNS_SERVERS.items():
        latency = ping(primary)
        if latency < best_ping:
            best_ping = latency
            best_server = (name, primary, secondary)
    return best_server, best_ping
