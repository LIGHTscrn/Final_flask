import pyttsx3
import datetime
import speech_recognition as sr ##for getting input voices 
import wikipedia  ##for surfing wikipedia
import os  ##for opening files
import webbrowser ##for opening web browser
import pyaudio

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def greet():
    hour = int(datetime.datetime.now().hour)
    if hour > 0 and hour < 12:
        speak("Good Morning")
    elif hour >= 12 and hour <= 18:
        speak("Good Afternoon")
    elif hour >= 18 and hour <= 20:
        speak("Good Evening")
    else:
        speak("Good Night")

def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"You said: {query}\n")

    except Exception as e:
        print(f"Say that again please...{e}")
        return "None"
    return query

if __name__ == "__main__":
    greet()
    if 1:
        query = command().lower()
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(f"{query}", sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)
        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
        elif 'open google' in query:
            webbrowser.open("google.com")
        elif 'open instagram' in query:
            webbrowser.open("instagram.com")
        elif 'open facebook' in query:
            webbrowser.open("facebook.com")
        elif 'open twitter' in query:
            webbrowser.open("twitter.com")
        elif 'open linkedin' in query:
            webbrowser.open("linkedin.com")
        elif 'open keagle' in query:
            webbrowser.open("keagle.com")
        elif 'play music' in query:
            music_dir = 'path to your music directory'
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, songs[0]))
            else:
                speak("No music files found in the directory")
        else:
            speak("I am sorry, I can't help you with that")