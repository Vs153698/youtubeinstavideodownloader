import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, StringVar
from urllib.parse import urlparse
import yt_dlp
import instaloader
import threading


def download_youtube_video(url, resolution, output_path='.', pbar=None, speed_label=None, size_label=None):
    try:
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [lambda d: show_progress(d, pbar, speed_label, size_label)]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', None)
        show_download_details(f"Downloaded: {title}", output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")


def download_instagram_reel(url, output_path='.', pbar=None, speed_label=None, size_label=None):
    try:
        parsed_url = urlparse(url)
        shortcode = parsed_url.path.split('/')[2]

        L = instaloader.Instaloader(download_videos=True, download_comments=False, save_metadata=False)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=output_path)
        show_download_details(f"Downloaded: {post.title}", output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")


def on_platform_select(*args):
    platform = platform_var.get()
    if platform == 'YouTube':
        resolution_label.pack(pady=5)
        resolution_combobox.pack(pady=5)
    else:
        resolution_label.pack_forget()
        resolution_combobox.pack_forget()


def update_resolutions():
    url = url_entry.get()
    if platform_var.get() == 'YouTube' and url:
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                resolutions = list(set([f'{f["height"]}p' for f in formats if f.get('height')]))
                resolutions.sort(key=lambda x: int(x[:-1]))
                resolution_combobox['values'] = resolutions
                if resolutions:
                    resolution_combobox.set(resolutions[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")


def download_video():
    url = url_entry.get()
    platform = platform_var.get()

    if platform == 'YouTube':
        resolution = resolution_combobox.get()
        detail_window, pbar, speed_label, size_label = create_download_details_window()
        thread = threading.Thread(target=download_youtube_video, args=(url, resolution, '.', pbar, speed_label, size_label))
        thread.start()
    elif platform == 'Instagram':
        detail_window, pbar, speed_label, size_label = create_download_details_window()
        thread = threading.Thread(target=download_instagram_reel, args=(url, '.', pbar, speed_label, size_label))
        thread.start()
    else:
        messagebox.showerror("Error", "Please select a platform")


def show_progress(d, pbar, speed_label, size_label):
    if d['status'] == 'downloading':
        pbar['value'] = float(d['_percent_str'].strip('%'))
        speed_label.config(text=f"Speed: {d['_speed_str']}")
        size_label.config(text=f"Total size: {d['_total_bytes_str']}")
        pbar.update_idletasks()
    elif d['status'] == 'finished':
        pbar['value'] = 100
        speed_label.config(text=f"Speed: {d['_speed_str']}")
        size_label.config(text=f"Total size: {d['_total_bytes_str']}")
        pbar.update_idletasks()


def create_download_details_window():
    detail_window = Toplevel(root)
    detail_window.title("Download Details")

    title_label = ttk.Label(detail_window, text="Downloading...")
    title_label.pack(pady=5)

    path_label = ttk.Label(detail_window, text="Saved to: current directory")
    path_label.pack(pady=5)

    pbar = ttk.Progressbar(detail_window, orient='horizontal', mode='determinate', length=280)
    pbar.pack(pady=10)

    speed_label = ttk.Label(detail_window, text="Speed: ")
    speed_label.pack(pady=5)

    size_label = ttk.Label(detail_window, text="Total size: ")
    size_label.pack(pady=5)

    return detail_window, pbar, speed_label, size_label


# Create the main application window
root = tk.Tk()
root.title("Video Downloader")

# Set up styles
style = ttk.Style(root)
style.configure('TLabel', font=('Helvetica', 10))
style.configure('TButton', font=('Helvetica', 10))
style.configure('TEntry', font=('Helvetica', 10))
style.configure('TCombobox', font=('Helvetica', 10))

# URL Entry
url_label = ttk.Label(root, text="Enter Video URL:")
url_label.pack(pady=5)
url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

# Platform Selection
platform_var = tk.StringVar()
platform_label = ttk.Label(root, text="Select Platform:")
platform_label.pack(pady=5)
platform_youtube = ttk.Radiobutton(root, text="YouTube", variable=platform_var, value='YouTube',
                                   command=update_resolutions)
platform_youtube.pack(pady=5)
platform_instagram = ttk.Radiobutton(root, text="Instagram", variable=platform_var, value='Instagram')
platform_instagram.pack(pady=5)

# Resolution Selection for YouTube
resolution_label = ttk.Label(root, text="Select Resolution:")
resolution_combobox = ttk.Combobox(root, state='readonly')

# Update resolution options when URL is entered
url_entry.bind("<FocusOut>", lambda e: update_resolutions())

# Download Button
download_button = ttk.Button(root, text="Download", command=download_video)
download_button.pack(pady=20)

# Event binding for platform selection
platform_var.trace("w", on_platform_select)

# Run the application
root.mainloop()
