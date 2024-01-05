from wsgiref.simple_server import make_server
from io import BytesIO
import subprocess
from threading import Thread, Event

class AudioProcessingServer:
    def __init__(self):
        self.processed_request = False
        self.processing_event = Event()

    def process_audio_thread(self, input_audio_path, output_stream):
        try:
            # ffmpeg command to process the audio
            ffmpeg_command = [
                'ffmpeg', '-re',
                          '-i', input_audio_path,
                '-f', 'mp3',
                'pipe:1'
            ]

            ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Set the processing event to signal that the thread has started
            self.processing_event.set()

            # Read and write in chunks to keep the stream continuous
            while True:
                print(f"Processing..")
                chunk = ffmpeg_process.stdout.read(1024)
                if not chunk:
                    print(f"No chunk..")
                    break
                output_stream.write(chunk)

            ffmpeg_process.stdout.close()
            ffmpeg_process.stderr.close()

        except Exception as e:
            print(f"Error processing audio: {str(e)}")

    def application(self, environ, start_response):
        print(f"envi: {str(environ)}")
        try:
            if environ['REQUEST_METHOD'] == 'GET' and not self.processed_request:
                # Get the audio name from the request
                #audio_name = environ['wsgi.input'].read().decode('utf-8')

                # Start a thread for audio processing
                input_audio_path = f'https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/nonuk/pc_hd_abr_v2/aks/bbc_asian_network.mpd'
                output_stream = BytesIO()
                print(f'Start Thread')
                thread = Thread(target=self.process_audio_thread, args=(input_audio_path, output_stream))
                thread.start()

                # Wait for the processing thread to start
                self.processing_event.wait()

                # Set response headers
                status = '200 OK'
                response_headers = [('Content-type', 'audio/mp3')]

                start_response(status, response_headers)

                # Return a generator to stream the processed audio
                return (chunk for chunk in iter(lambda: output_stream.read(1024), b''))

            elif self.processed_request:
                start_response('403 Forbidden', [('Content-type', 'text/plain')])
                return [b'Forbidden - Only one connection allowed']

            else:
                start_response('405 Method Not Allowed', [('Content-type', 'text/plain')])
                return [b'Method Not Allowed']

        except Exception as e:
            start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
            return [str(e).encode('utf-8')]

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # Create the server instance
    audio_server = AudioProcessingServer()

    # Create a simple WSGI server
    with make_server('0.0.0.0', 5000, audio_server.application) as httpd:
        print("Waiting for one connection on port 5000...")
        httpd.handle_request()  # Serve only one request
        print("Request processed. Server shutting down.")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
