import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import threading
import os
import time
import zipfile

OS_DOWNLOAD_URLS = {
    "Ubuntu 22.04": "https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso",
    "Fedora 37": "https://download.fedoraproject.org/pub/fedora/linux/releases/37/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-37-1.7.iso",
    "Debian 11": "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.6.0-amd64-netinst.iso",
    "Kali Linux": "https://cdimage.kali.org/kali-2023.1/kali-linux-2023.1-installer-amd64.iso",
    "Arch Linux": "https://mirror.rackspace.com/archlinux/iso/latest/archlinux-2023.03.01-x86_64.iso",
    "Linux Mint 21.2": "https://mirrors.edge.kernel.org/linuxmint/stable/21.2/linuxmint-21.2-cinnamon-64bit.iso",
    "Zorin OS": "https://download.zorinos.com/15/Core/Zorin-OS-15.3-Core-64-bit.iso",
    "CentOS 8": "http://isoredirect.centos.org/centos/8/isos/x86_64/CentOS-8.2.2004-x86_64-dvd1.iso",
    "Windows 10 USB Tool": "https://go.microsoft.com/fwlink/?LinkId=691209",
    "Windows 11 USB Tool": "https://go.microsoft.com/fwlink/?linkid=2156295"
}

class FileDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

      
        self.title("OS Installer Downloader by TheZ")
        self.geometry("600x650")
        self.configure(bg='#2e2e2e')
        self.iconbitmap("icon.ico")  

       
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

       
        self.os_label = ctk.CTkLabel(self, text="Select Operating System:", text_color="#90ee90", font=("Arial", 14))
        self.os_label.pack(pady=(20, 5))

        self.os_var = tk.StringVar(value="Select OS")
        self.os_dropdown = ctk.CTkComboBox(self, values=list(OS_DOWNLOAD_URLS.keys()), variable=self.os_var, command=self.update_url_display)
        self.os_dropdown.pack(pady=5)

      
        self.url_label = ctk.CTkLabel(self, text="Download URL:", text_color="#90ee90", font=("Arial", 14))
        self.url_label.pack(pady=(10, 5))

        self.url_entry = ctk.CTkEntry(self, width=500, state="readonly")
        self.url_entry.pack(pady=5)

       
        self.dest_label = ctk.CTkLabel(self, text="Save Location:", text_color="#90ee90", font=("Arial", 14))
        self.dest_label.pack(pady=(20, 5))

        self.dest_entry = ctk.CTkEntry(self, width=400, border_color="#90ee90")
        self.dest_entry.pack(pady=5)

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_location, fg_color="#32CD32")
        self.browse_button.pack(pady=(10, 20))

       
        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download, fg_color="#32CD32")
        self.download_button.pack(pady=20)

        self.cancel_button = ctk.CTkButton(self, text="Cancel Download", command=self.cancel_download, fg_color="#DC143C")
        self.cancel_button.pack(pady=10)
        self.cancel_button.configure(state="disabled")

      
        self.progress = ctk.CTkProgressBar(self, width=500, progress_color="#32CD32")
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self, text="", text_color="white", font=("Arial", 12))
        self.status_label.pack(pady=10)

      
        self.cancel_event = threading.Event()

       
        self.downloaded_files = []

    def browse_location(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder_selected)

    def update_url_display(self, _=None):
        os_choice = self.os_var.get()
        url = OS_DOWNLOAD_URLS.get(os_choice, "")
        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.url_entry.configure(state="readonly")

    def start_download(self):
        os_choice = self.os_var.get()
        folder_path = self.dest_entry.get()

        if os_choice not in OS_DOWNLOAD_URLS:
            messagebox.showerror("Error", "Please select a valid OS.")
            return
        if not folder_path:
            messagebox.showerror("Error", "Please select a save location.")
            return

        download_url = OS_DOWNLOAD_URLS[os_choice]
        dest_path = os.path.join(folder_path, f"{os_choice.replace(' ', '_')}.exe" if "Windows" in os_choice else f"{os_choice.replace(' ', '_')}.iso")

       
        self.cancel_event.clear()
        self.cancel_button.configure(state="normal")

      
        download_thread = threading.Thread(target=self.download_file, args=(download_url, dest_path))
        download_thread.start()

    def cancel_download(self):
        self.cancel_event.set()  
        self.cancel_button.configure(state="disabled")  

    def download_file(self, url, dest_path):
       
        try:
            with requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                with open(dest_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if self.cancel_event.is_set():
                            self.status_label.configure(text="Download canceled.")
                            return
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress.set(downloaded / total_size if total_size else 0)
                        self.status_label.configure(text=f"Downloading... {downloaded / 1024 / 1024:.2f} MB")

           
            self.downloaded_files.append(dest_path)

          
            self.status_label.configure(text="Download completed.")
            self.progress.set(0)
            messagebox.showinfo("Download Complete", "File downloaded successfully!")

           
            self.zip_downloaded_files()

        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {e}")
            self.status_label.configure(text="Download failed.")
            self.progress.set(0)

    def zip_downloaded_files(self):
    
        if not self.downloaded_files:
            return

        folder_path = os.path.dirname(self.downloaded_files[0])
        zip_path = os.path.join(folder_path, "Downloaded_OS_Files.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in self.downloaded_files:
                arcname = os.path.basename(file_path)  
                zipf.write(file_path, arcname=arcname)

        messagebox.showinfo("Zipping Complete", f"All files have been zipped as {zip_path}")
        self.status_label.configure(text="All files zipped.")
        
        self.downloaded_files.clear()

    
        self.progress.set(0)
        self.cancel_button.configure(state="disabled")

if __name__ == "__main__":
    app = FileDownloaderApp()
    app.mainloop()
