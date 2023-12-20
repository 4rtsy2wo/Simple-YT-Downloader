# Simple YouTube Downloader

![Image 1](img/beforeFetch.png)
![Image 2](img/videoFetch.png)
YouTube Downloader is a simple Python script built with Tkinter and Pytube that allows you to download YouTube videos or audio streams with ease. It provides a user-friendly interface to fetch available streams, choose between video and audio options, and download the selected content.

## Features

- Fetch available streams for a given YouTube video link.
- Choose between video with audio, audio-only, or video-only streams.
- Download the selected stream to your specified folder.

## Prerequisites

The script is written in Python. Before using the YouTube Downloader, ensure you have Python installed on your machine.

[Python](https://www.python.org/) download link at https://www.python.org/

## Installation

### Clone the Repository:

```bash
git clone https://github.com/yourusername/YouTube-Downloader.git
cd YouTube-Downloader
pip install -r requirements.txt
python ytDL.py
```

OR

### Download the ZIP File:

1. Navigate to the GitHub repository of the YouTube Downloader script.
2. On the main page of the repository, look for a green button labeled "Code."
3. Click on the "Code" button, and a dropdown menu will appear.
4. Select "Download ZIP" from the menu.
5. Once the ZIP file is downloaded, locate it in your computer's Downloads folder or the location where your browser saves downloads.
6. Right-click on the ZIP file and choose "Extract All" (Windows) or "Open With" > "Archive Utility" (Mac).
7. This will create a new folder with the same name as the ZIP file.
8. Open a terminal or command prompt.

```bash
cd path/to/extracted/folder
pip install -r requirements.txt
python ytDL.py
```

## Usage

- **Enter YouTube URL:**
  Paste the YouTube video URL in the provided entry field.

- **Change Download Folder (Optional):**
  Click the "Change Folder" button to choose a different download folder.

- **Choose Media Type:**
  Select the desired media type (Video with Audio, Audio Only, or Video Only) using the radio buttons.

- **Fetch Streams:**
  Click the "Get Streams" button to fetch available streams for the provided YouTube URL.

- **Select Stream:**
  Click on a stream button to select the desired stream for download.

- **Wait for the download to complete.**
  A message box will confirm when the download is finished.

## Additional Information

- The default download folder is set to a subfolder within the user's Videos folder.
- You can customize the download folder by clicking the "Change Folder" button.
- Streams are displayed in a scrollable frame, and you can use the mouse wheel to scroll.

## Important Note

Downloading copyrighted content without permission may violate YouTube's terms of service. Make sure you have the right to download and use the content you are downloading.
