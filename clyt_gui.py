import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
from pytube import YouTube
from moviepy.audio.io.AudioFileClip import AudioFileClip
import requests
from bs4 import BeautifulSoup
import re

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, directory)

def start_download():
    url = url_entry.get()
    format_selected = format_var.get()
    output_dir = output_entry.get()

    if not url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
        return

    if not output_dir or not os.path.exists(output_dir):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    download_button.config(state=tk.DISABLED)
    Thread(target=download_video, args=(url, format_selected, output_dir)).start()

def download_video(url, format_selected, output_dir):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        video_title = soup.find('title').get_text().strip()

        video_title = re.sub(r'[\\/*?:"<>|]', '', video_title)
        video_title = re.sub(r' - YouTube$', '', video_title)

        youtube = YouTube(url)
        if format_selected == "mp3":
            video = youtube.streams.get_audio_only()
            temp_video_filepath = os.path.join(output_dir, f"{video_title}_temp.mp4")
            output_file_path = os.path.join(output_dir, f"{video_title}.mp3")
        elif format_selected == "mp4":
            video = youtube.streams.get_highest_resolution()
            output_file_path = os.path.join(output_dir, f"{video_title}.mp4")

        if os.path.exists(output_file_path):
            messagebox.showerror("Error", f"File already exists at \"{output_file_path}\".")
            download_button.config(state=tk.NORMAL)
            return

        if format_selected == "mp3":
            out_video_filepath = video.download(output_dir, filename=f"{video_title}_temp.mp4")
            moviepy_audio_clip = AudioFileClip(out_video_filepath)
            moviepy_audio_clip.write_audiofile(output_file_path, verbose=False, logger=None)
            moviepy_audio_clip.close()
            os.remove(out_video_filepath)
        else:
            out_video_filepath = video.download(output_dir, filename=video_title)
            if not out_video_filepath.endswith('.mp4'):
                os.rename(out_video_filepath, out_video_filepath + '.mp4')

        # Uncomment to show success message
        # messagebox.showinfo("Success", f"Downloaded {format_selected} to \"{output_file_path}\"")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to download: {str(e)}")

    finally:
        download_button.config(state=tk.NORMAL)

# Set up the main application window
root = tk.Tk()
root.title("_clyt_ (an ez youtube to mp3/mp4 downloader)")
root.iconbitmap('icon.ico')

# YouTube URL input
tk.Label(root, text="youtube url:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Format selection
format_var = tk.StringVar(value="mp3")
tk.Label(root, text="select format:").grid(row=1, column=0, padx=10, pady=10)
mp3_radio = tk.Radiobutton(root, text="mp3", variable=format_var, value="mp3")
mp4_radio = tk.Radiobutton(root, text="mp4", variable=format_var, value="mp4")
mp3_radio.grid(row=1, column=1, padx=10, pady=10, sticky='w')
mp4_radio.grid(row=1, column=1, padx=70, pady=10, sticky='w')

# Output directory input
tk.Label(root, text="output directory:").grid(row=2, column=0, padx=10, pady=10)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="browse", command=browse_directory)
browse_button.grid(row=2, column=2, padx=10, pady=10)

# Download button
download_button = tk.Button(root, text="download", command=start_download)
download_button.grid(row=3, column=0, columnspan=3, pady=20)

root.mainloop()
