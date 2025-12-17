import os
import uuid
import logging
import glob
from flask import Flask, request, send_file, after_this_request, jsonify
import yt_dlp

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

@app.route('/audio', methods=['GET'])
def get_audio():
    video_id = request.args.get('videoId')
    
    if not video_id:
        return jsonify({'error': 'Missing videoId parameter'}), 400

    youtube_url = f'https://www.youtube.com/watch?v={video_id}'
    temp_id = str(uuid.uuid4())
    output_template = f'/tmp/{temp_id}.%(ext)s'
    
    # Ensure /tmp exists (mostly for local windows testing compatibility, though docker uses linux)
    if not os.path.exists('/tmp'):
        try:
            os.makedirs('/tmp')
        except OSError:
            # Fallback for Windows local dev if /tmp is not accessible
            output_template = f'temp/{temp_id}.%(ext)s'
            if not os.path.exists('temp'):
                os.makedirs('temp')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading audio for video ID: {video_id}")
            ydl.download([youtube_url])
            
        # Find the generated file (yt-dlp might append .mp3)
        # We look for the file derived from our temp_id
        # The output template was configured, but post-processor changes extension
        
        # Check specific locations based on template logic above
        base_path = '/tmp' if os.path.exists('/tmp') else 'temp'
        pattern = f"{base_path}/{temp_id}.mp3"
        
        files = glob.glob(pattern)
        if not files:
             # Fallback: sometimes it might be just the template name if conversion didn't happen as expected
             # But with FFmpegExtractAudio, it generally ensures reliable extension
             logger.error("Downloaded file not found.")
             return jsonify({'error': 'File processing failed'}), 500
             
        file_path = files[0]
        
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed temp file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing file: {e}")
            return response

        return send_file(
            file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f'{video_id}.mp3'
        )

    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
