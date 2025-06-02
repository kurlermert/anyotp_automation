from pywinauto import Application
import time
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import psutil
import os
import ctypes
import win32gui
import threading

stop_flag = False

def is_application_running(app_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == app_name:
            return True
    return False

def start_automation_thread():
    global stop_flag
    stop_flag = False
    threading.Thread(target=start_automation).start()

def stop_automation():
    global stop_flag
    stop_flag = True
    print("Otomasyon durduruldu.")

def start_automation():
    global stop_flag
    while not stop_flag:
        try:
            app_path = app_path_entry.get()
            otp_id = otp_id_entry.get()
            auth_code = auth_code_entry.get()

            if not app_path or not otp_id or not auth_code:
                messagebox.showerror("Hata", "Tüm alanları doldurun!")
                return

            if not os.path.exists(app_path):
                raise Exception(f"Uygulama yolu bulunamadı: {app_path}")

            if not is_application_running("AnyOTP.exe"):
                print("AnyOTP çalışmıyor, yeniden başlatılıyor...")
                app = Application(backend="uia").start(app_path)
            else:
                app = Application(backend="uia").connect(title="AnyOTP")

            main_window = app.window(title="AnyOTP")

            id_field = main_window.child_window(auto_id="7", control_type="Edit")
            id_field.set_text(otp_id)
            time.sleep(1)

            auth_field = main_window.child_window(auto_id="8", control_type="Edit")
            auth_field.set_text(auth_code)

            hwnd = win32gui.FindWindow(None, "AnyOTP")
            if hwnd == 0:
                raise Exception("AnyOTP penceresi bulunamadı!")
            else:
                print(f"Pencere Handle: {hwnd}")

                l_param = 14221538

                WM_LBUTTONDOWN = 0x0201
                WM_LBUTTONUP = 0x0202

                ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONDOWN, 0, l_param)
                ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, l_param)

                print("PostMessage ile Confirm butonuna tıklama gönderildi.")
                time.sleep(3)

            if not is_application_running("AnyOTP.exe"):
                print("Uygulama kapandı, otomasyon yeniden başlıyor...")
                continue

        except Exception as e:
            if stop_flag:
                break
            print(f"Hata: {e}")
            time.sleep(5)

def show_usage_info():
    info_window = Toplevel(root)
    info_window.title("Kullanım Bilgisi")
    info_window.geometry("400x200")
    info_text = (
        "OTP ID ve Auth code girin, Başlat tuşuna bastığınızda uygulama şifre ekranı "
        "görünene kadar AnyOTP'yi açıp denemeye devam edecektir.\n\n"
        "Şifre ekranı göründüğünde Durdur'a basıp şifrenizi girebilirsiniz."
    )
    Label(info_window, text=info_text, wraplength=380, justify="left", padx=10, pady=10).pack()

root = tk.Tk()
root.title("AnyOTP Otomasyonu")

tk.Label(root, text="Uygulama Yolu:").grid(row=0, column=0, padx=10, pady=5)
app_path_entry = tk.Entry(root, width=50)
app_path_entry.insert(0, "")
app_path_entry.grid(row=0, column=1, padx=10, pady=5)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("EXE Files", "*.exe")])
    if file_path:
        app_path_entry.delete(0, tk.END)
        app_path_entry.insert(0, file_path)

browse_button = tk.Button(root, text="Gözat", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="OTP ID:").grid(row=1, column=0, padx=10, pady=5)
otp_id_entry = tk.Entry(root, width=50)
otp_id_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="AuthCode:").grid(row=2, column=0, padx=10, pady=5)
auth_code_entry = tk.Entry(root, width=50)
auth_code_entry.grid(row=2, column=1, padx=10, pady=5)

usage_button = tk.Button(root, text="Kullanım Bilgisi", command=show_usage_info, bg="#FFC107", fg="black", font=("Arial", 10, "bold"))
usage_button.grid(row=3, column=1, pady=10)

start_button = tk.Button(root, text="Başlat", command=start_automation_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
start_button.grid(row=4, column=0, pady=20)

stop_button = tk.Button(root, text="Durdur", command=stop_automation, bg="#F44336", fg="white", font=("Arial", 12, "bold"))
stop_button.grid(row=4, column=1, pady=20)

root.mainloop()