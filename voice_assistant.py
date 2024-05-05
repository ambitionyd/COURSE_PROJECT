import requests
import speech_recognition as sr
from gtts import gTTS
import pygame
import pyautogui
import webbrowser
import os


def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        return None
    except sr.RequestError:
        print("Unable to access the Google Speech Recognition API.")
        return None

def respond(response_text):
    print("Response:", response_text)
    tts = gTTS(text=response_text, lang='en')
    current_directory = os.getcwd()
    output_file = os.path.join(current_directory, "response.mp3")
    tts.save(output_file)
    print("Response audio saved successfully.")
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    print("Response audio playback finished.")

def read_index_file(file_path):
    index_map = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  
                parts = line.split(':', 1)
                if len(parts) == 2:
                    index, question = parts
                    try:
                        index = int(index)
                        index_map[question.strip()] = index
                    except ValueError:
                        print(f"Ignore invalid index in {file_path}: {index}")
                else:
                    print(f"Ignore invalid line in {file_path}: {line}")
    return index_map

def get_answer(index_map, answer_file, user_question):
    if user_question in index_map:
        index = index_map[user_question]
        with open(answer_file, 'r') as file:
            for line in file:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    idx, answer = parts
                    try:
                        idx = int(idx)
                        if idx == index:
                            return answer.strip()
                    except ValueError:
                        print(f"Ignore invalid index in {answer_file}: {idx}")
    return None

def get_current_weather(api_key, city):
    # API endpoint for current weather data
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        # Sending HTTP GET request to the API endpoint
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # Extracting relevant weather information from the API response
            # weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            # Building weather response text
            weather_response = (
                f"Weather in {city}: "
                # f"{weather_description}. "
                f"Temperature: {temperature}°C. "
                f"Humidity: {humidity}%. "
                f"Wind Speed: {wind_speed} m/s."
            )

            return weather_response
        else:
            return f"Failed to retrieve weather data: {data['message']}"

    except Exception as e:
        return f"Error occurred: {str(e)}"

def main():
    questions_index_file = 'C:\\Users\\hp\\Desktop\\COURSE_PROJECT\\question.txt'
    answers_file = 'C:\\Users\\hp\\Desktop\\COURSE_PROJECT\\answers.txt'
    api_key = 'cbf0eb19e636574461a35518f412e190'

    # Read the index file to create the question index map
    question_index_map = read_index_file(questions_index_file)

    while True:
        command = listen_for_command()

        if command:
            # print("Recognized command:", command)

            # Check if recognized command matches any question in the dataset
            matched_question = None
            for question in question_index_map:
                if question.lower() in command:
                    matched_question = question
                    break
            
            if matched_question:
                # Retrieve the corresponding answer
                answer = get_answer(question_index_map, answers_file, matched_question)
                if answer is not None:
                    respond(answer)
                else:
                    respond("Sorry, I don't have an answer for that question.")
            else:
                # Handle other specific commands
                if "hi" in command or "hello" in command:
                    respond("Hello! How may I help you?")
                elif "add a task" in command:
                    respond("Sure, what is the task?")
                elif "list tasks" in command:
                    respond("Sure. Your tasks are:")
                    # Insert code to list tasks here
                elif "take a screenshot" in command:
                    pyautogui.screenshot("screenshot.png")
                    respond("I took a screenshot for you.")
                elif "open browser" in command:
                    respond("Opening browser.")
                    webbrowser.open("http://www.google.com")
                elif "weather in" in command:
                    # Extract city from command
                    city = command.split("weather in", 1)[-1].strip()
                    weather_response = get_current_weather(api_key, city)
                    respond(weather_response)
                elif "exit" in command:
                    respond("Goodbye!")
                    break
                else:
                    respond("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main()
