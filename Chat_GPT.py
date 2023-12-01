from pynput import keyboard
import wave
import sounddevice as sd
import time
from openai import OpenAI
import re

client = OpenAI()


def record_audio(duration=None):
    CHUNK = 1024
    FORMAT = 'int16'
    CHANNELS = 1
    RATE = 10000
    WAVE_OUTPUT_FILENAME = "user_response.wav"
    frames = []
    stream = None
    is_recording = False
    recording_stopped = False

    def record_audio():
        nonlocal frames, stream
        frames = []
        stream = sd.InputStream(
            samplerate=RATE,
            channels=CHANNELS,
            dtype=FORMAT,
            blocksize=CHUNK,
            callback=callback
        )
        stream.start()

    def callback(indata, frame_count, time, status):
        nonlocal stream
        if is_recording:
            frames.append(indata.copy())

    def stop_recording():
        nonlocal frames, stream, recording_stopped
        stream.stop()
        stream.close()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        recording_stopped = True

    def on_key(key):
        nonlocal is_recording
        if key == keyboard.Key.page_down:
            if not is_recording:
                record_audio()
                is_recording = True
            else:
                stop_recording()
                is_recording = False

    listener = keyboard.Listener(on_press=on_key)
    listener.start()
    start_time = time.time()
    while listener.running:
        if recording_stopped:
            listener.stop()
        elif duration and (time.time() - start_time) > duration:
            listener.stop()
        time.sleep(0.01)


def whisper():
    record_audio()
    audio_file = open("user_response.wav", "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcript.text


def voice_gpt():
    messages = [{"role": "system", "content": """
    You are a helpful assistant. 
    """}]
    with open('gpt_prompt.txt', 'r', errors="ignore") as filer:
        prompt = filer.read()
    while True:
        usermess = input("Type message or press Enter to record audio: ")
        if usermess == "":
            print("Press 'Page Down' to start/stop recording")
            message = whisper()
            print(f"{message}")
            message = f"{message}\n{prompt}"
        else:
            message = usermess + '\n' + prompt
        prompt = ''  # Clear the input materials
        messages.append({"role": "user", "content": f"{message}"})
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0.75,
            messages=messages,
            stream=True,
        )
        answer_accumulator = ''
        print('--------------------------------------------------------\nChatGPT:')
        for chunk in response:
            choice = chunk.choices[0]
            if choice.delta and choice.delta.content:
                answer = choice.delta.content
                answer_accumulator += answer
                print(answer, end='', flush=True)
        print('\n--------------------------------------------------------')
        messages.append({"role": "assistant", "content": f"{answer_accumulator}"})


if __name__ == "__main__":
    voice_gpt()
