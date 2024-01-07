# Download Songs from YouTube

This Python script allows you to download songs (in mp3 audio or mp4 video format) from YouTube in various ways:

## Features

- Downloads songs from:
  - YouTube playlists
  - Spotify playlists (automatically searches on YouTube)
  - YouTube search
  - YouTube links
  - Spotify song links (automatically searches on YouTube)
  - Text file with YouTube links (canciones.txt)
- Downloads audio only in mp3 or video in mp4
- Filters special characters in file names
- Checks if the file already exists before downloading
- Fetches cover art and artist information from Spotify and adds it to the metadata (optional)
- Supports multiple downloads at once
- Has configuration options to customize the download

## Requirements

- Python 3.7 or higher
- The following Python libraries:
  - youtube_dl
  - spotipy
  - mutagen
  - requests
  - youtube-search-python
  - pytube
  - pydub

## Configuration

On first run, the `config.json` file will be generated with the configuration options. You need to provide the Spotify App Client ID and Client Secret to fetch song information.

The configuration options include:

- Download directory
- Video resolution (minimum, maximum or average)
- Download audio and/or video
- Enable downloading from different sources 
- Fetch metadata from Spotify

## Execution Instructions

1. Clone the repository or download the Python file.
2. Install the required libraries using `pip install -r requirements.txt`.
3. Configure the `config.json` file with the Spotify client IDs (you can get them [here](https://developer.spotify.com/dashboard)).
4. Run the script and follow the presented instructions.

By default it will attempt to download from the sources enabled in the configuration. 

## Credits

- Developed by Fvitu.

---
This script has been developed for educational and learning purposes.