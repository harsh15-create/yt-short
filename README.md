# YT-DLP Audio Microservice

A lightweight microservice to extract audio from YouTube videos and stream it as MP3.

## Features
-   Extracts audio from YouTube video ID.
-   Converts to MP3 using ffmpeg.
-   Returns binary stream.
-   Automatic temporary file cleanup.

## API Usage

**Endpoint:** `GET /audio`

**Query Parameter:** `videoId` (The YouTube video ID)

**Example:**
```bash
curl "http://localhost:8080/audio?videoId=QLK9G5zyU-Q" --output audio.mp3
```

## Running Locally (Docker) - Recommended

1.  **Build the image:**
    ```bash
    docker build -t yt-audio .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 8080:8080 yt-audio
    ```

## Running Locally (Python)

*Prerequisite: `ffmpeg` must be installed and in your system PATH.*

1.  install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the server:
    ```bash
    python server.py
    ```

## Deployment

### Railway
1.  Connect your GitHub repository.
2.  Railway will automatically detect the `Dockerfile`.
3.  Add a variable `PORT=8080` (optional, Railway usually detects exposed port).
4.  Deploy.

### Fly.io
1.  Install `flyctl`.
2.  Run `fly launch`.
3.  Choose settings (Name, Region).
4.  Run `fly deploy`.
