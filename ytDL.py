import os
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
from pytube.exceptions import PytubeError, VideoUnavailable, AgeRestrictedError, MembersOnly, VideoPrivate, VideoRegionBlocked, LiveStreamError, RecordingUnavailable, MaxRetriesExceeded, HTMLParseError, ExtractError, RegexMatchError

# version number
version = "0.2.2"
# Set the main_path to a subfolder within the user's home directory
main_path = os.path.join(os.path.expanduser('~'), 'YT_Downloader')
# Dictionary to map media choices to sub directories
sub_dirs = {'a': 'Audio_Only', 'v': 'Video_Only', 'c': 'Video_with_Audio'}

# Dictionary to map media choices to filter functions
filter_functions = {
    'a': lambda streams: streams.filter(only_audio=True).order_by('abr').desc(),
    'v': lambda streams: streams.filter(only_video=True).order_by('resolution').desc(),
    'c': lambda streams: streams.filter(progressive=True).order_by('resolution').desc()
}

# get streams from url
def fetch_streams():
    clear_stream_buttons()
    video_url = url_entry.get()
    media_choice = media_var.get().lower()
    try:
        yt = YouTube(video_url, on_progress_callback=download_progress, allow_oauth_cache=False, use_oauth=False)
        streams = yt.streams
        streams = filter_functions[media_choice](streams)
        for stream in streams:
            stream_info = get_stream_info(stream, media_choice)
            stream_button = create_stream_button(stream_info, stream)
            stream_button.pack(fill='x')
            stream_buttons.append(stream_button)
    except PytubeError as e:
        handle_error(e)

# error handling
def handle_error(e):
    if isinstance(e, AgeRestrictedError):
        messagebox.showerror("Age Restricted", f"Sorry, the Video {e.video_id} is age-restricted.")
    elif isinstance(e, MembersOnly):
        messagebox.showerror("MembersOnly", f"Members only video, skipping.")
    elif isinstance(e, VideoPrivate):
        messagebox.showerror("Video Private", f"Video {e.video_id} is private, skipping.")
    elif isinstance(e, VideoRegionBlocked):
        messagebox.showerror("Video Region Blocked", f"Video {e.video_id} is Region blocked, skipping.")
    elif isinstance(e, VideoUnavailable):
        messagebox.showerror("Video Unavailable", f"Video {e.video_id} is unavailable, skipping.")
    elif isinstance(e, LiveStreamError):
        messagebox.showerror("Live Stream", f"Video {e.video_id} is a Live Stream, skipping.")
    elif isinstance(e, RecordingUnavailable):
        messagebox.showerror("Recording Unavailable", f"Recording {e.video_id} is not avaiable, skipping.")
    elif isinstance(e, MaxRetriesExceeded):
        messagebox.showerror("Max Retries Exceeded", "An error occurred during download: Maximum number of retries exceeded.")
    elif isinstance(e, HTMLParseError):
        messagebox.showerror("HTML Parse Error", "An error occurred during download: HTML could not be parsed.")
    elif isinstance(e, ExtractError):
        messagebox.showerror("Extract Error", "An error occurred during download: Data extraction error.")
    elif isinstance(e, RegexMatchError):
        messagebox.showerror("Regex Match Error", f"An error occurred during download: {e.caller}: could not find match for {e.pattern}")
    else:
        messagebox.showerror("Unknown Error", f"An unknown error occurred during download: {str(e)}")
        
#get stream info
def get_stream_info(stream, media_choice):
    codec = stream.audio_codec if media_choice == 'a' else stream.video_codec
    return f"{stream.abr if media_choice == 'a' else stream.resolution} ({stream.mime_type} - {'Codec: ' + codec.split('.')[0] if media_choice == 'a' else str(stream.fps) + ' fps - Codec: ' + codec.split('.')[0]})"

# create stream buttons
def create_stream_button(stream_info, stream):
    return tk.Button(scrollable_frame, text=stream_info, fg='yellow', bg='black', command=lambda s=stream: download_media(s))

# sanitize filename and add params
def get_stream_filename(stream):
    name, ext = os.path.splitext(stream.default_filename)
    filename = ''.join(c if c.isalnum() or c in [' ', '_', '-'] else '' for c in name)
    filename = filename.replace(' ', '_').replace('-', '_')
    media_type = media_var.get().lower()
    codec_info = f"{stream.abr}_{stream.audio_codec.split('.')[0]}" if media_type == 'a' else f"{stream.resolution}_{stream.video_codec.split('.')[0]}"
    return f"{filename}_{codec_info}{ext}"

# download stream
def download_media(stream):
    output_path = os.path.join(main_path, sub_dirs[media_var.get().lower()])
    try:
        stream.download(output_path=output_path, filename=get_stream_filename(stream))
        messagebox.showinfo("Download Complete", "Download complete.")
    except PytubeError as e:
        messagebox.showerror("Error", f"An error occurred during download: {e}")

# change download folder
def select_download_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        global main_path
        main_path = os.path.join(folder_selected, 'YT_Downloader')
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, main_path)

# delete stream buttons before fetching new ones
def clear_stream_buttons():
    for button in stream_buttons:
        button.destroy()
    stream_buttons.clear()

# handle mouse scroll
def on_mousewheel(event):
    streams_canvas.yview_scroll(-event.delta//120, "units")

# progress bar
def reset_progress_bar():
    progress_bar['value'] = 0

def download_progress(stream, chunk, bytes_remaining):
    progress_bar['value'] = (1 - (bytes_remaining / stream.filesize)) * 100
    # update window for progress
    window.update()
    # keep the green for 2 secs then reset
    if bytes_remaining == 0:
        window.after(2000, reset_progress_bar)


## GUI ##
# create widgets
def create_pack(widget_type, master, pack_args={}, **kwargs):
    widget = widget_type(master, **kwargs)
    widget.pack(**pack_args)
    return widget

# main window
window = tk.Tk()
window.geometry("400x500")
window.resizable(False, True)
window.title(f"YouTube Downloader v{version}")

# URL input
url_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'pady': 5})
url_label = create_pack(tk.Label, window, text="⛓ YouTube Link:", font=('monospace'), pack_args={'side': 'top', 'fill': 'x'})
url_entry = create_pack(tk.Entry, window, font=('monospace', 10), pack_args={'side': 'top', 'fill': 'x', 'padx': 10, 'pady': 5})

# media choice
media_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'pady': 10})
media_label = create_pack(tk.Label, media_frame, text="🎥 Choose Media:", font=('monospace'), pack_args={'side': 'top'})
media_var = tk.StringVar(value="C")
media_choices = [("Video with Audio", "C"),("Audio Only", "A"), ("Video Only", "V")]
for text, choice in media_choices:
    create_pack(tk.Radiobutton, media_frame, text=text, variable=media_var, value=choice, font=('monospace',), pack_args={'side': 'left'})

# fetch button and instruction label
instruction_label = create_pack(tk.Label, window, text="|| Retrieve the streams and click to download ||", font=('monospace'))
fetch_button = create_pack(tk.Button, window, text="Get Streams 🎬", font=('monospace'), bg='red', fg='white', bd=5, relief='solid', command=fetch_streams, pack_args={'side': 'top', 'padx': 5, 'pady': 10})

# progress bar
progress_frame = create_pack(tk.Frame, window, pack_args={'side': 'bottom', 'fill': 'x', 'expand': True, 'pady': 5, 'padx': 14})
progress_label = create_pack(tk.Label, progress_frame, text="📥 Progress:", font=('monospace'), pack_args={'side': 'left'})
progress_bar = create_pack(tk.ttk.Progressbar, progress_frame, orient="horizontal", length=300, mode="determinate", pack_args={'side': 'left'})

# folder frame
folder_frame = create_pack(tk.Frame, window, pack_args={'side': 'bottom', 'fill': 'x', 'expand': True, 'padx': 10})
change_folder_button = create_pack(tk.Button, folder_frame, text="Change Folder", font=('monospace', 11), command=select_download_folder, pack_args={'side': 'left'})
folder_path_entry = create_pack(tk.Entry, folder_frame, font=('monospace', 10), pack_args={'side': 'left', 'padx': 5, 'fill': 'x', 'expand': True})
folder_path_entry.insert(0, main_path)

# window frame + canvas + scrollbar
streams_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'fill': 'both', 'expand': True, 'pady': 10})
streams_canvas = create_pack(tk.Canvas, streams_frame)
scrollbar = create_pack(tk.Scrollbar, streams_frame, orient="vertical", command=streams_canvas.yview, pack_args={'side': "right", 'fill': "y"})
streams_canvas.pack(side="left", fill="both", expand=True)
streams_canvas.configure(yscrollcommand=scrollbar.set)

# scrollable frame
scrollable_frame = create_pack(tk.Frame, streams_canvas)
streams_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=streams_canvas.winfo_reqwidth())
scrollable_frame.bind("<Configure>", lambda e: streams_canvas.configure(scrollregion=streams_canvas.bbox("all")))

# bind mousewheel to canvas
streams_canvas.bind_all("<MouseWheel>", on_mousewheel)

# stream buttons var
stream_buttons = []

# run loop
window.mainloop()