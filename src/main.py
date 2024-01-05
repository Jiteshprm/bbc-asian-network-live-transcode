import subprocess
from flask import Flask, Response

app = Flask(__name__)


def get_ffmpeg_process():
    # FFmpeg command to transcode MP4 to MP3 and write to stdout
    ffmpeg_command = [
        'ffmpeg',
        '-re',
        '-i',
        'https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/nonuk/pc_hd_abr_v2/aks/bbc_asian_network.mpd',
        '-f', 'mp3',
        'pipe:1'  # Write to stdout
    ]
    return subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)


def audio_generator(ffmpeg_process):
    try:
        # Read and yield chunks of data from FFmpeg stdout
        while True:
            data = ffmpeg_process.stdout.read(1024)
            if not data:
                break
            yield data
    finally:
        # Close the FFmpeg process when streaming is finished
        ffmpeg_process.stdout.close()
        ffmpeg_process.wait()


@app.route('/stream')
def stream():
    ffmpeg_process = get_ffmpeg_process()

    def generate():
        return audio_generator(ffmpeg_process)

    # Create a Flask response with the generator function
    return Response(generate(), mimetype='audio/mpeg')


if __name__ == '__main__':
    # Run the Flask application with threaded mode to handle multiple clients
    app.run(host='0.0.0.0',port=5000, debug=False, threaded=True)
