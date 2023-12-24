import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk, Image
from datetime import timedelta
import requests
from pytubefix import YouTube
from pytubefix.exceptions import PytubeFixError, VideoUnavailable, AgeRestrictedError, MembersOnly, VideoPrivate, VideoRegionBlocked, LiveStreamError, RecordingUnavailable, MaxRetriesExceeded, HTMLParseError, ExtractError, RegexMatchError
from pytubefix.helpers import safe_filename

# version number
version = "0.3.0"
# Set the main_path to a subfolder within the user's home directory
main_path = os.path.join(os.path.expanduser('~'), 'YT_Downloader')
# Dictionary to map media choices to sub directories
sub_dirs = {'a': 'Audio_Only', 'v': 'Video_Only', 'av': 'Video_with_Audio', 'c': 'Captions'}
# Dic media choices to filter streams
filter_functions = {
    'a': lambda streams: streams.filter(only_audio=True).order_by('abr').desc(),
    'v': lambda streams: streams.filter(only_video=True).order_by('resolution').desc(),
    'av': lambda streams: streams.filter(progressive=True).order_by('resolution').desc()
}
# Dic video info
video_info = {
    "title": "",
    "length": "",
    "thumbnail_url": ""
}
    
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

# get streams from url        
def fetch_streams():
    """
    Fetches and displays the available streams for a given YouTube video URL.
    
    This function clears the buttons, retrieves the video URL from the entry field,
    checks if the URL is empty, and displays an error message if it is. It then
    retrieves the media choice (audio or video) from the variable, creates a YouTube
    object with the given video URL, filters the available streams based on the media
    choice, and displays the filtered streams. Finally, it checks if there are any
    captions available and enables or disables the subtitle button accordingly.
    
    Raises:
        PytubeError: If there is an error while fetching the streams.
    """
    clear_buttons()
    video_url = url_entry.get()
    if not video_url.strip():
        messagebox.showerror("Error", "URL field is empty. Enter your YouTube Link")
        return
    media_choice = media_var.get().lower()
    try:
        yt = YouTube(video_url, on_progress_callback=download_progress, allow_oauth_cache=False, use_oauth=False)
        streams = yt.streams
        streams = filter_functions[media_choice](streams)
        display_streams(streams, media_choice)
        display_video_info(video_url)
        # check captions and switch button accordingly
        subtitle_button.config(state="normal" if len(yt.captions) > 0 else "disabled")
    except PytubeFixError as e:
        handle_error(e)  

# display thumbnail
def display_thumbnail(thumbnail_url, label):
    # Get the path to the 'img' folder in the bundled executable
    img_folder = os.path.join(sys._MEIPASS, 'img') if getattr(sys, 'frozen', False) else './img'

    # Use the included image file
    img_path = os.path.join(img_folder, 'placeholder.png')

    img = Image.open(requests.get(thumbnail_url, stream=True).raw) if thumbnail_url else Image.open(img_path)
    img.thumbnail((180, 180))
    thumbnail = ImageTk.PhotoImage(img)
    label.config(image=thumbnail)
    label.image = thumbnail

# Get all video info
def display_video_info(video_url):
    yt = YouTube(video_url)
    title = yt.title
    length = str(timedelta(seconds=yt.length))
    thumbnail_url = yt.thumbnail_url
    # Update dictionary
    video_info.update({
        "title": title,
        "length": length,
        "thumbnail_url": thumbnail_url,
    })
    # Update labels
    title_label.config(text=title)
    length_label.config(text="Length: " + length)
    display_thumbnail(thumbnail_url, placeholder_image)

# get stream info
def get_stream_info(stream, media_choice):
    codec = stream.audio_codec if media_choice == 'a' else stream.video_codec
    return f"{stream.abr if media_choice == 'a' else stream.resolution} ({stream.mime_type} - {'Codec: ' + codec.split('.')[0] if media_choice == 'a' else str(stream.fps) + ' fps - Codec: ' + codec.split('.')[0]})"

# create stream buttons and display
def display_streams(streams, media_choice):
    for stream in streams:
        stream_info = get_stream_info(stream, media_choice)
        stream_button = create_stream_button(stream_info, stream)
        stream_button.pack(fill='x')
        stream_buttons.append(stream_button)

# get captions and create buttons + display 
def get_and_display_captions():
    yt = YouTube(url_entry.get())
    yt.bypass_age_gate()
    captions = yt.caption_tracks
    
    subtitle_button.config(state="normal" if captions else "disabled")
    clear_buttons()
    for caption in captions:
            caption_button = create_caption_button(caption)
            caption_button.pack(fill='x')
            caption_buttons.append(caption_button)
               
# create stream buttons
def create_stream_button(stream_info, stream):
    button = tk.Button(scrollable_frame, text=stream_info, fg='yellow', bg='black', command=lambda s=stream: download_media(s))
    return button

# create caption buttons
def create_caption_button(caption):
    button = tk.Button(scrollable_frame, text=caption.name, fg='yellow', bg='black', command=lambda c=caption: download_caption(c.code))
    return button

# sanitize filename - streams
def get_stream_filename(stream):
    name, ext = os.path.splitext(stream.default_filename)
    # sanitize filename pytube
    filename = safe_filename(name).replace(' ', '_')
    media_type = media_var.get().lower()
    codec_info = f"{stream.abr}_{stream.audio_codec.split('.')[0]}" if media_type == 'a' else f"{stream.resolution}_{stream.video_codec.split('.')[0]}"
    return f"{filename}_{codec_info}{ext}"

# sanitize filename - captions
def get_caption_filename(vTitle):
    # sanitize filename pytube
    filename = safe_filename(vTitle).replace(' ', '_')
    return filename

# download stream
def download_media(stream):
    try:
        output_path = os.path.join(main_path, sub_dirs[media_var.get().lower()])
        stream.download(output_path=output_path, filename=get_stream_filename(stream))
        
        messagebox.showinfo("Download Complete", "Download complete.")
    except PytubeFixError as e:
        messagebox.showerror("Error", f"An error occurred during download: {e}")
        
# download caption               
def download_caption(code):
    try:
        yt = YouTube(url_entry.get())
        caption = yt.captions[code]  # Use the language code as the key
        
        output_path = os.path.join(main_path, sub_dirs['c'])
        os.makedirs(output_path, exist_ok=True)

        filename = get_caption_filename(yt.title)
        caption.download(title=filename, output_path=output_path, srt=True)
            
        messagebox.showinfo("Download Complete", "Caption downloaded.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during download: {e}")
        
# change download folder
def select_download_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        global main_path
        main_path = os.path.join(folder_selected, 'YT_Downloader')
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, main_path)
    
# clear buttons in the scrollframe
def clear_buttons():
    for button in stream_buttons + caption_buttons:
        button.destroy()
    stream_buttons.clear()
    caption_buttons.clear()
    streams_canvas.yview_moveto(0)

# handle mouse scroll
def on_mousewheel(event):
    streams_canvas.yview_scroll(-event.delta//120, "units")

# progress bar
def reset_progress_bar():
    progress_bar['value'] = 0

def download_progress(stream, chunk, bytes_remaining):
    """
    Updates the progress bar and window for the download progress.

    Parameters:
    stream (Stream): The stream object representing the download.
    chunk (bytes): Not used but expected by the callback function.
    bytes_remaining (int): The number of bytes remaining to be downloaded.

    """
    progress_bar['value'] = (1 - (bytes_remaining / stream.filesize)) * 100
    # update window for progress
    window.update()
    # keep the green for 2 secs then reset
    if bytes_remaining == 0:
        window.after(2000, reset_progress_bar)
        
        
## GUI ##
# create widgets
def create_pack(widget_type, master, pack_args={}, **kwargs):
    """
    Create a widget of the specified type, add it to the given master widget,
    and pack it using the provided pack arguments.

    Args:
        widget_type (class): The type of widget to create.
        master (class): The master widget to add the created widget to.
        pack_args (dict, optional): The arguments to pass to the pack method. Defaults to {}.
        **kwargs: Additional keyword arguments to pass to the widget constructor.

    Returns:
        class: The created widget.
    """
    widget = widget_type(master, **kwargs)
    widget.pack(**pack_args)
    return widget

# window diplay in the middle of the screen
window = tk.Tk()
window.geometry(f"400x600+{int((window.winfo_screenwidth() / 2) - (400 / 2))}+{int((window.winfo_screenheight() / 2) - (500 / 2))}")
window.resizable(False, True)
window.title(f"YouTube Downloader v{version}")

# URL input
url_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'pady': 5})
url_label = create_pack(tk.Label, window, text="⛓ YouTube Link:", font=('monospace'), pack_args={'side': 'top', 'fill': 'x'})
url_entry = create_pack(tk.Entry, window, font=('monospace', 10), pack_args={'side': 'top', 'fill': 'x', 'padx': 10, 'pady': 5})

# thumbnail frame
thumbnail_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'fill': 'x'})
# Create the thumbnail label without an image
placeholder_image = create_pack(tk.Label, thumbnail_frame, pack_args={'side': 'left', 'padx': 20, 'pady': 5})
# Now you can call display_thumbnail
display_thumbnail('', placeholder_image)

# media choice
media_frame = create_pack(tk.Frame, thumbnail_frame, pack_args={'side': 'left','pady': 10})
media_label = create_pack(tk.Label, media_frame, text="🎥 Choose Media:", font=('monospace'), pack_args={'side': 'top'})
media_var = tk.StringVar(value="AV")
media_choices = [("Video with Audio", "AV"),("Audio Only", "A"), ("Video Only", "V")]
for text, choice in media_choices:
    create_pack(tk.Radiobutton, media_frame, text=text, variable=media_var, value=choice, font=('monospace',), pack_args={'side': 'top'})
# length label
length_label = create_pack(tk.Label, media_frame, text="Length: " + str(video_info["length"]), font=('monospace'), pack_args={'side': 'top', 'fill': 'x'})

# instruction label
instruction_label = create_pack(tk.Label, window, text="|| Retrieve the streams and click to download ||", font=('monospace'))

# fetch stream and caption button
button_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'pady': 5})
fetch_button = create_pack(tk.Button, button_frame, text="Get Streams 🎬", font=('monospace'), bg='red', fg='white', bd=5, relief='solid', command=fetch_streams, pack_args={'side': 'left', 'padx': 5, 'pady': 5})
subtitle_button = create_pack(tk.Button, button_frame, text="Captions 📝", font=('monospace'), state="disabled", command=get_and_display_captions, pack_args={'side': 'left', 'padx': 5, 'pady': 5})

# title label
title_label = create_pack(tk.Label, window, text=video_info["title"], font=('monospace'), wraplength=380, anchor='center', justify='center', pack_args={'side': 'top', 'fill': 'x', 'padx': 5})

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
streams_frame = create_pack(tk.Frame, window, pack_args={'side': 'top', 'fill': 'both', 'expand': True, 'pady': 5})
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
caption_buttons = []

# run loop
window.mainloop()