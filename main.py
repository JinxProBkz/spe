import os
import subprocess
import requests
import getpass

def print_ascii_art():
    art = r"""
   _____                 _       _  __          __       _    
  / ____|               (_)     | | \ \        / /      | |   
 | (___  _ __   ___  ___ _  __ _| |  \ \  /\  / /__  ___| | __
  \___ \| '_ \ / _ \/ __| |/ _` | |   \ \/  \/ / _ \/ _ \ |/ /
  ____) | |_) |  __/ (__| | (_| | |    \  /\  /  __/  __/   < 
 |_____/| .__/ \___|\___|_|\__,_|_|     \/  \/ \___|\___|_|\_\
        | |                                                   
        |_|                                                   
         Network Automation Toolkit
    """
    print(art)

GITHUB_REPO = "https://github.com/JinxProBkz/spe"  
BRANCH = "main"  

def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    raw_url = f"https://raw.githubusercontent.com/JinxProBkz/spe/{BRANCH}/version.txt"
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f" Gagal mengambil versi dari GitHub: {e}")
        return None

def update_from_github_zip():
    zip_url = f"{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
    
    try:
        print(" Mengunduh update...")
        response = requests.get(zip_url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            extract_folder = "__update_temp__"
            zip_ref.extractall(extract_folder)

        extracted_subfolder = os.path.join(extract_folder, os.listdir(extract_folder)[0])

        for item in os.listdir(extracted_subfolder):
            s = os.path.join(extracted_subfolder, item)
            d = os.path.join(".", item)

            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        shutil.rmtree(extract_folder)
        print(" Update selesai. Silakan restart aplikasi.")
        input("Tekan Enter untuk keluar...")
        sys.exit()

    except Exception as e:
        print(" Gagal update:", e)
        input("Tekan Enter untuk keluar...")

def check_and_update():
    print("\n Mengecek versi...")

    local_version = get_local_version()
    remote_version = get_remote_version()

    if remote_version is None:
        print(" Tidak bisa mengambil versi dari GitHub.")
        input("Tekan Enter untuk kembali ke menu...")
        return

    print(f" Versi saat ini: {local_version}")
    print(f" Versi tersedia: {remote_version}")

    if local_version == remote_version:
        print(" Sudah menggunakan versi terbaru.")
    else:
        print(" Versi baru tersedia!")
        pilihan = input("Ingin update sekarang? (y/n): ").strip().lower()
        if pilihan == 'y':
            update_from_github_zip()
        else:
            print(" Update dibatalkan.")

    input("Tekan Enter untuk kembali ke menu...")

def change_credentials():
    print("\n Ganti Username & Password Login SSH")
    new_user = input("Masukkan username baru: ")
    new_pass = getpass.getpass("Masukkan password baru: ")

    # Simpan kredensial baru ke file
    with open("ssh_credentials.txt", "w") as f:
        f.write(f"{new_user}\n{new_pass}")
    print(" Username dan password SSH disimpan.")

def load_credentials():
    try:
        with open("ssh_credentials.txt", "r") as f:
            lines = f.readlines()
            return lines[0].strip(), lines[1].strip()
    except FileNotFoundError:
        return None, None

def run_ssh_script():
    username, password = load_credentials()
    if not username or not password:
        print("  Username/password belum disetel. Silakan ubah kredensial terlebih dahulu.")
        return
    print(f"\n Menjalankan SSH dengan user: {username}")
    subprocess.run(["python", "core/ssh_multi.py", username, password])

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_ascii_art()
        print("Menu Utama:")
        print("1. SSH Multiple Device")
        print("2. Ubah username/password SSH")
        print("3. Check and Update All script from GitHub")
        print("4. Keluar")

        pilihan = input("\n Pilih menu : ").strip()

        if pilihan == '1':
            run_ssh_script()
        elif pilihan == '2':
            change_credentials()
        elif pilihan == '3':
            check_and_update()
        elif pilihan == '4':
            print(" Keluar dari program.")
            break
        else:
            print(" Pilihan tidak valid.")
        
        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()

