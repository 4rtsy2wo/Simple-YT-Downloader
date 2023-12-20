import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pytube import YouTube


# Set the main_path to a subfolder within the user's Videos folder
main_path = os.path.join(os.path.expanduser('~'), 'Videos', 'YT_Downloads')

def fetch_streams():
    global streams
    clear_stream_buttons()
    video_url = url_entry.get()
    media_choice = media_var.get().lower()
    yt = YouTube(video_url)
    streams = yt.streams
    if media_choice == 'a':
        streams = streams.filter(only_audio=True).order_by('abr').desc()
    elif media_choice == 'v':
        streams = streams.filter(only_video=True).order_by('resolution').desc()
    else:
        streams = streams.filter(progressive=True).order_by('resolution').desc()

    for stream in streams:
        if media_choice == 'a':
            stream_info = f"{stream.abr} ({stream.mime_type} - Codec: {stream.audio_codec.split('.')[0]})"
        else:
            stream_info = f"{stream.resolution} ({stream.mime_type} - {stream.fps} fps - Codec: {stream.video_codec.split('.')[0]})"
        stream_button = tk.Button(scrollable_frame, text=stream_info, fg='yellow', bg='black', command=lambda s=stream: download_media(s))
        stream_button.pack(fill='x')
        stream_buttons.append(stream_button)

# download stream
def download_media(stream):
    sub_dir = {'a': 'audio', 'v': 'video'}.get(media_var.get().lower(), 'video_audio')
    output_path = os.path.join(main_path, sub_dir)
    try:
        stream.download(output_path=output_path)
        messagebox.showinfo("Download Complete", "Download complete.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during download: {e}")
        
# change download button  
def select_download_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        global main_path
        main_path = os.path.join(folder_selected, 'YT_Downloader')
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, main_path)

# clean stream buttons when new get fetched
def clear_stream_buttons():
    for button in stream_buttons:
        button.destroy()
    stream_buttons.clear()
    
# handle mouse scroll
def on_mousewheel(event):
    streams_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
# main window
window = tk.Tk()
window.title("YouTube Downloader")
window.resizable(width=False, height=True)

# URL label
url_label = tk.Label(window, text="⛓ YouTube Link:", font=('monospace'))
url_label.pack(side='top', fill='x')

# URL input
url_entry = tk.Entry(window, font=('monospace', 10))
url_entry.pack(side='top', fill='x', padx=10, pady=5)

# folder frame 
folder_frame = tk.Frame(window)
folder_frame.pack(side='top', fill='x', expand=True, pady=5, padx=10)
# download change button
change_folder_button = tk.Button(folder_frame, text="Change Folder", font=('monospace', 10), command=select_download_folder)
change_folder_button.pack(side='left')
# download path
folder_path_entry = tk.Entry(folder_frame, font=('monospace', 10))
folder_path_entry.pack(side='left', padx=5, fill='x', expand=True)
# set initial folder to users video folder
folder_path_entry.insert(0, main_path)

# media label
media_label = tk.Label(window, text="🎥 Choose Media:", font=('monospace'))
media_label.pack(side='top')
# media frame for buttons
media_frame = tk.Frame(window)
media_frame.pack(side='top')
# media radio buttons
media_var = tk.StringVar(value="C")  # Default choice is Audio and Video
media_choices = [("Video with Audio", "C"), ("Audio Only", "A"), ("Video Only", "V")]
for text, choice in media_choices:
    tk.Radiobutton(media_frame, text=text, variable=media_var, value=choice, font=('monospace')).pack(side='left')

# fetch button
fetch_button = tk.Button(window, text="Get Streams 🎬", font=('monospace'), bg='red', fg='white', bd=5, relief='solid', command=fetch_streams)
fetch_button.pack(side='top', padx=10, pady=10)

# instruction label
instruction_label = tk.Label(window, text="📌 Click on a stream when loaded, and wait for the download to finish.", fg='blue', font=('monospace', 10))
instruction_label.pack()

# stream frame + canvas + scrollbar
streams_frame = tk.Frame(window)
streams_frame.pack(side='top', fill='both', expand=True, pady='5')

streams_canvas = tk.Canvas(streams_frame)
scrollbar = tk.Scrollbar(streams_frame, orient="vertical", command=streams_canvas.yview)
scrollbar.pack(side="right", fill="y")

streams_canvas.pack(side="left", fill="both", expand=True)
streams_canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(streams_canvas)
streams_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=streams_canvas.winfo_reqwidth())

scrollable_frame.bind("<Configure>", lambda e: streams_canvas.configure(scrollregion=streams_canvas.bbox("all")))

# bind mousewheel 
streams_canvas.bind_all("<MouseWheel>", on_mousewheel)

# stream button array
stream_buttons = []  # List to keep track of stream buttons

# start GUI loop
window.mainloop()