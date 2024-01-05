from flask import Flask, Response, request
import subprocess
import io
import threading

app = Flask(__name__)


def transcode(input_stream, start_event):
    # Use subprocess to run ffmpeg command with input from stdin and output to stdout
    command = ['ffmpeg','-re',  '-i', 'https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/nonuk/pc_hd_abr_v2/aks/bbc_asian_network.mpd', '-f', 'mp3', 'pipe:1']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_stream = io.BytesIO()
    chunk_size = 1024

    # Set the event to signal that the subprocess has started
    start_event.set()

    while True:
        print(f"Processing..")
        chunk = input_stream.read(chunk_size)
        if not chunk:
            break
        output_stream.write(process.stdout.read(chunk_size))

    process.stdin.close()
    process.wait()

    if process.returncode != 0:
        return None, f"Error: {process.stderr.read().decode('utf-8')}"

    return output_stream.getvalue(), None

@app.route('/transcode', methods=['GET'])
def transcode_endpoint():
    try:
        input_stream = request.stream

        # Create an event for synchronization
        start_event = threading.Event()

        # Start the transcoding in a separate thread
        transcoding_thread = threading.Thread(target=transcode, args=(input_stream, start_event))
        transcoding_thread.start()

        # Wait for the event before continuing
        start_event.wait()

        # Transcode the input stream
        mp3_content = transcode(input_stream, start_event)

        if mp3_content is None:
            return "Error during transcoding", 500

        # Serve the MP3 content in chunks in the same connection
        def generate():
            chunk_size = 1024
            for i in range(0, len(mp3_content), chunk_size):
                yield mp3_content[i:i+chunk_size]

        return Response(generate(), mimetype='audio/mp3')

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', debug=True)