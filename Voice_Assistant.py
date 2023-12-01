import openai
import json
from pynput import keyboard
import wave
import sounddevice as sd
import time
import os
import subprocess
import datetime as dt


def voice_stream(input_text):
    # Call the API to get the audio stream
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )

    # Ensure the ffplay command is set up to read from stdin
    ffplay_cmd = ['ffplay', '-nodisp', '-autoexit', '-']
    ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE, stdout=open(os.devnull, 'wb'), stderr=subprocess.STDOUT)
    binary_content = response.content

    # Stream the audio to ffplay
    try:
        ffplay_proc.stdin.write(binary_content)
        ffplay_proc.stdin.flush()  # Ensure the audio is sent to ffplay
    except BrokenPipeError:
        # Handle the case where ffplay closes the pipe
        pass
    finally:
        ffplay_proc.stdin.close()
        ffplay_proc.wait()  # Wait for ffplay to finish playing the audio


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

client = openai.OpenAI()


def setup_assistant(client, assistant_name):
    # create a new agent
    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions= f"""
            You are a friend. Your name is {assistant_name} You are having a vocal conversation with a user. You will 
            never output any markdown or formatted text of any kind, and you will speak in a concise, highly 
            conversational manner. You will adopt any persona that the user may ask of you.
            """,
        model="gpt-4-1106-preview",
    )
    # Create a new thread
    thread = client.beta.threads.create()
    return assistant.id, thread.id


def send_message(client, thread_id, task):
    # Create a new thread message with the provided task
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=task,
    )
    return thread_message


def run_assistant(client, assistant_id, thread_id):
    # Create a new run for the given thread and assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Loop until the run status is either "completed" or "requires_action"
    while run.status == "in_progress" or run.status == "queued":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        # At this point, the status is either "completed" or "requires_action"
        if run.status == "completed":
            return client.beta.threads.messages.list(
                thread_id=thread_id
            )


def save_session(assistant_id, thread_id, user_name_input, file_path='chat_sessions.json'):
    # Check if file exists and load data, else initialize empty data
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {"sessions": {}}

    # Find the next session number
    next_session_number = str(len(data["sessions"]) + 1)

    # Add the new session
    data["sessions"][next_session_number] = {
        "Assistant ID": assistant_id,
        "Thread ID": thread_id,
        "User Name Input": user_name_input
    }

    # Save data back to file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def display_sessions(file_path='chat_sessions.json'):
    if not os.path.exists(file_path):
        print("No sessions available.")
        return

    with open(file_path, 'r') as file:
        data = json.load(file)

    print("Available Sessions:")
    for number, session in data["sessions"].items():
        print(f"Session {number}: {session['User Name Input']}")


def get_session_data(session_number, file_path='chat_sessions.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)

    session = data["sessions"].get(session_number)
    if session:
        return session["Assistant ID"], session["Thread ID"], session["User Name Input"]
    else:
        print("Session not found.")
        return None, None


def collect_message_history(assistant_id, thread_id, user_name_input):
    messages = run_assistant(client, assistant_id, thread_id)
    message_dict = json.loads(messages.model_dump_json())

    with open(f'{user_name_input}_message_log.txt', 'w') as message_log:
        for message in reversed(message_dict['data']):
            # Extracting the text value from the message
            text_value = message['content'][0]['text']['value']

            # Adding a prefix to distinguish between user and assistant messages
            if message['role'] == 'assistant':
                prefix = f"{user_name_input}: "
            else:  # Assuming any other role is the user
                prefix = "You: "

            # Writing the prefixed message to the log
            message_log.write(prefix + text_value + '\n')

    return f"Messages saved to {user_name_input}_message_log.txt"


def main_loop():
    user_choice = input("Type 'n' to make a new assistant session. Press 'Enter' to choose an existing assistant "
                      "session.")
    if user_choice == 'n':
        user_name_input = input("Please type a name for this chat session: ")
        IDS = setup_assistant(client, assistant_name=user_name_input)
        save_session(IDS[0], IDS[1], user_name_input)
        assistant_id = IDS[0]
        thread_id = IDS[1]
        if assistant_id and thread_id:
            print(f"Created Session with {user_name_input}, Assistant ID: {assistant_id} and Thread ID: {thread_id}")
            first_iteration = True
            while True:
                if first_iteration:
                    print("Press Page Down to start/stop recording your voice message:")
                    current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
                    user_message = whisper()
                    print(f"You: {user_message}")
                    user_message = f"It is now {current_time}. \n {user_message}"
                    first_iteration = False
                else:
                    user_message = whisper()
                    print(f"You: {user_message}")
                if user_message.lower() in {'exit', 'exit.'}:
                    print("Exiting the program.")
                    print(collect_message_history(assistant_id, thread_id, user_name_input))
                    break
                send_message(client, thread_id, user_message)
                messages = run_assistant(client, assistant_id, thread_id)
                message_dict = json.loads(messages.model_dump_json())
                most_recent_message = message_dict['data'][0]
                assistant_message = most_recent_message['content'][0]['text']['value']
                print(f"{user_name_input}: {assistant_message}")
                voice_stream(assistant_message)

    else:
        display_sessions()
        chosen_session_number = input("Enter the session number to load: ")
        assistant_id, thread_id, user_name_input = get_session_data(chosen_session_number)
        if assistant_id and thread_id:
            print(f"Loaded Session {chosen_session_number} with Assistant ID: {assistant_id} and Thread ID: {thread_id}")
            first_iteration = True
            while True:
                if first_iteration:
                    print("Press Page Down to start/stop recording your voice message:")
                    current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
                    user_message = whisper()
                    print(f"You: {user_message}")
                    user_message = f"It is now {current_time}. \n {user_message}"
                    first_iteration = False
                else:
                    user_message = whisper()
                    print(f"You: {user_message}")
                if user_message.lower() in {'exit', 'exit.'}:
                    print("Exiting the program.")
                    print(collect_message_history(assistant_id, thread_id, user_name_input))
                    break
                send_message(client, thread_id, user_message)
                messages = run_assistant(client, assistant_id, thread_id)
                message_dict = json.loads(messages.model_dump_json())
                most_recent_message = message_dict['data'][0]
                assistant_message = most_recent_message['content'][0]['text']['value']
                print(f"{user_name_input}: {assistant_message}")
                voice_stream(assistant_message)


if __name__ == "__main__":
    main_loop()
