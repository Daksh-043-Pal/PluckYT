import customtkinter as ctk
import yt_dlp
import threading
import os
import sys

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PluckYT")
        self.geometry("550x400")

        # Default save location (User's Downloads folder)
        self.save_dir = os.path.expanduser("~/Downloads")

        # ---Folder Selection UI---
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        self.folder_label = ctk.CTkLabel(self.folder_frame, text=f"Saving to: {self.save_dir}", text_color="gray")
        self.folder_label.pack(side="left", padx=10)
        
        self.browse_btn = ctk.CTkButton(self.folder_frame, text="Browse", width=80, command=self.choose_directory)
        self.browse_btn.pack(side="right", padx=10)

        # URL Entry
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste YouTube URL here...", width=450)
        self.url_entry.pack(pady=10)

        # Download Button
        self.download_btn = ctk.CTkButton(self, text="Download", command=self.start_download)
        self.download_btn.pack(pady=10)
        
        # Progress UI
        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0)
        
        self.percentage_label = ctk.CTkLabel(self, text="")
        
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.pack(pady=10)

    def choose_directory(self):
        #folder picker
        folder = ctk.filedialog.askdirectory(initialdir=self.save_dir, title="Select Save Folder")
        if folder: # If user didn't click cancel
            self.save_dir = folder
            self.folder_label.configure(text=f"Saving to: {self.save_dir}")

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            return
        
        self.status_label.configure(text="Downloading...")
        self.download_btn.configure(state="disabled")
        
        self.progress_bar.pack(pady=10)
        self.percentage_label.pack()
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent_float = downloaded / total
                    percent_str = f"{int(percent_float * 100)}%"
                    self.after(0, self.update_progress_ui, percent_float, percent_str)
            except Exception:
                pass 
        elif d['status'] == 'finished':
            self.after(0, self.update_progress_ui, 1.0, "100%")
            self.after(0, lambda: self.status_label.configure(text="Processing and merging..."))

    def update_progress_ui(self, float_val, string_val):
        self.progress_bar.set(float_val)
        self.percentage_label.configure(text=string_val)

    def download_video(self, url):
        ffmpeg_path = get_resource_path("ffmpeg.exe")

        output_template = os.path.join(self.save_dir, '%(title)s.%(ext)s')

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            'extractor_args': {'youtube': ['player_client=android']},
            'ffmpeg_location': ffmpeg_path
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.status_label.configure(text="Download Complete!"))
        except Exception as e:
            print(f"Error: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error downloading video."))
        finally:
            self.after(0, lambda: self.download_btn.configure(state="normal"))
            self.after(0, lambda: self.progress_bar.pack_forget())
            self.after(0, lambda: self.percentage_label.pack_forget())

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()