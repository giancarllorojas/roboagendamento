import requests

def _email(title, text):
    chatID = "-314311013"
    token  = "696336641:AAE4PwtywoQEV3XqOYUFoxvYNl3e4DQ5pCQ"

    r = requests.post("https://api.telegram.org/bot" + token + "/sendMessage", {"chat_id": chatID, "text": text})   


_email("hello", "aloooo")