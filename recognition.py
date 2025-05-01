import speech_recognition as sr

    

def detectEnglish():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


def detectTurkish():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="tr-TR")  
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    


def detectGerman():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="de-DE")  
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    


def detectSpanish():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="ed-ES")  
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    


def detectFrench():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="fr-FR")  
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


def detectItalian():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language="it-IT")  
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
