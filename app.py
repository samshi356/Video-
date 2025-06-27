from flask import Flask, render_template, request, send_file
import os
import uuid
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'forcejson': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = sorted(
                    [f for f in info['formats'] if f.get('filesize') and f.get('ext') == 'mp4'],
                    key=lambda x: int(x['height']) if x.get('height') else 0,
                    reverse=True
                )
                video_info = {
                    'title': info.get('title'),
                    'formats': formats,
                    'url': url
                }
        except Exception as e:
            return render_template('index.html', error=str(e))
    return render_template('index.html', video_info=video_info)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    try:
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        ydl_opts = {
            'quiet': True,
            'outtmpl': filepath,
            'format': format_id
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"Download failed: {e}", 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
