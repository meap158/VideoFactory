import os
import sys
import time
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

try:
    from tts import TextToSpeech
except ImportError:
    # Handle the case where the module cannot be imported
    TextToSpeech = None
    # Log an error or raise an exception, as appropriate


class FptTTS(TextToSpeech):

    def __init__(self, key: str = None) -> None:
        super().__init__('fpt')
        self.key: str = key or os.environ.get('FPT_API_KEY', None)

    def generate_audio(
        self,
        text: str,
        voice: str = None,
        speed: float = None,
        output_path: str = 'fpt_tts.mp3'
    ) -> None:
        # Check if the arguments are provided, if not, fetch from environment variables or use defaults
        if voice is None:
            voice = os.environ.get('FPT_VOICE', 'leminh'),  # Default: 'leminh' (male northern)
        if speed is None:
            speed = float(os.environ.get('FPT_SPEED', '0'))

        url: str = 'https://api.fpt.ai/hmi/tts/v5'
        headers: dict = {
            'api-key': self.key,
            'voice': voice,
            'speed': str(speed),
            'format': 'wav'
        }
        payload = text
        # Make the API request
        response = requests.request('POST', url, data=payload.encode('utf-8'), headers=headers)

        # Get the response data
        data = response.json()
        async_url = data['async']
        error = data['error']
        r = requests.get(async_url, stream=True)

        max_attempts = 3
        counter = 0
        # Check if the request is successful
        while True:
            r = requests.get(async_url, stream=True)
            if r.status_code == 200 and error == 0:
                # Write the content of the response to the file
                with open(output_path, 'wb') as f:
                    f.write(r.content)
                break
            else:
                # Increment the counter
                counter += 1
                if counter > max_attempts:
                    # Maximum attempts reached, exit the loop
                    break
                # Wait 5 seconds before making another request
                time.sleep(5)


# # Usage:
# # To use the FptTTS class, create an instance with your API key:
# tts = FptTTS(key=os.environ.get('FPT_API_KEY'))
# # Then, call the generate_audio method to generate audio from text:
# tts.generate_audio(text='Xin chào mọi người', speed=0)

# # Using speed is rather unreliable; tested working speeds: -3.0, -2.0, -1.5, 0, 0.5, 1.0, 3.0
# speed = -3.0
# while speed <= 3.0:
#     print(speed)
#     tts.generate_audio(text='Xin chào mọi người', speed=speed, output_path=f'fpt_tts_{speed}.mp3')
#     time.sleep(15)  # Wait for 15 second before generating the next audio
#     speed += 0.5
