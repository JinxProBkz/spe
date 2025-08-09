import csv
import paramiko
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor


def load_commands(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def read_until_prompt(shell, prompt_regex, timeout=10):
    buffer = ""
    shell.settimeout(timeout)
    while True:
        try:
            data = shell.recv(65535).decode('utf-8', errors='ignore')
            if not data:
                break
            buffer += data
            if re.search(prompt_regex, buffer):
                break
        except Exception:
            break
    return buffer


def ssh_device(hostname, ip, username, password, commands):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=8, look_for_keys=False)

        shell = ssh.invoke_shell()
        prompt_pattern = r"[>#]\s*$"  
        read_until_prompt(shell, prompt_pattern)  

        ssh_output = ""

        for cmd in commands:
            shell.send(cmd + "\n")
            output = read_until_prompt(shell, prompt_pattern)
            ssh_output += f"--- {cmd} ---\n" + output.replace('\r', '') + "\n"

        os.makedirs("ssh_output", exist_ok=True)
        with open(f"ssh_output/{hostname}.txt", "w", encoding='utf-8') as out_file:
            out_file.write(ssh_output.strip())

        print(f"[V] Sukses SSH ke {hostname} ({ip})")

        ssh.close()

    except Exception as e:
        print(f"[X] Gagal SSH ke {hostname} ({ip}) - {e}")


def load_devices(csv_filename):
    devices = []
    with open(csv_filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            devices.append((row['hostname'], row['ip']))
    return devices


def main():
    if len(sys.argv) < 3:
        print("X Penggunaan: python ssh_multi.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    devices = load_devices("ssh_devices.csv")
    commands = load_commands("ssh_commands.txt")

    max_threads = 30  
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for hostname, ip in devices:
            executor.submit(ssh_device, hostname, ip, username, password, commands)

if __name__ == "__main__":
    main()
