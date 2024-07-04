# Andrew Peterson
# This program executes keyboard input for a 3DS expecting redirected input from the PC
# Runs on Windows only due to pydirectinput dependency

import speech_recognition as sr
from fuzzywuzzy import fuzz
import spacy
import vgamepad as vg
import winsound

frequency = 2500
duration = 100


gamepad = vg.VX360Gamepad()
import pydirectinput


spacy_model = spacy.load("en_core_web_md")

VERBOSE = False

# create phrase lists for each 3DS button
LButton = ["L", "Press L", "Press the L Button"]
RButton = ["R", "Press R", "Press the R Button"]
AButton = [
    "A",
    "Press A",
    "Press the A Button",
    "jump",
    "press jump",
    "press the jump button",
]
BButton = ["B", "Press B", "Press the B Button"]
XButton = ["X", "Press X", "Press the X Button"]
YButton = ["Y", "Press Y", "Press the Y Button"]
StartButton = ["Start", "Press Start", "Press the Start Button"]
SelectButton = ["Select", "Press Select", "Press the Select Button"]
UpButton = [
    "Up",
    "Press Up",
    "Press the Up Button",
    "go up",
    "run up",
    "walk up",
    "move up",
]
DownButton = [
    "Down",
    "Press Down",
    "Press the Down Button",
    "go down",
    "run down",
    "walk down",
    "move down",
]
LeftButton = [
    "Left",
    "Press Left",
    "Press the Left Button",
    "go left",
    "run left",
    "walk left",
    "move left",
]
RightButton = [
    "Right",
    "Press Right",
    "Press the Right Button",
    "go right",
    "run right",
    "walk right",
    "move right",
]
DpadUpButton = ["Dpad Up", "Press Dpad Up", "d-pad up" "Press the Dpad Up Button"]
DpadDownButton = ["Dpad Down", "d-pad down" "Press Dpad Down", "Press the Dpad Down Button"]
DpadLeftButton = ["Dpad Left", "Press Dpad Left", "d-pad left" "Press the Dpad Left Button"]
DpadRightButton = ["Dpad Right", "Press Dpad Right", "d-pad right" "Press the Dpad Right Button"]
HomeButton = ["Home", "Press Home", "Press the Home Button"]

HoldPhrases = [
    "Hold",
    "Hold the",
    "Hold the button",
    "Hold the button for",
    "keep holding",
]
StopPhrases = ["Stop", "Stop holding", "Stop holding the button"]

HelpPhrases = [
    "Help",
    "Help me",
    "Help me",
    "What can I say",
    "Give me a list of commands",
    "What are the voice commands",
]

WAKE_WORD = ["mario", "cloud"]

# cast to tuple to make it hashable
BUTTON_MAPPINGS = {
    tuple(LButton): "l",
    tuple(RButton): "r",
    tuple(AButton): "a",
    tuple(BButton): "b",
    tuple(XButton): "x",
    tuple(YButton): "y",
    tuple(StartButton): "enter",
    tuple(SelectButton): "]",
    tuple(UpButton): "up",
    tuple(DownButton): "down",
    tuple(LeftButton): "left",
    tuple(RightButton): "right",
    tuple(DpadUpButton): "u",
    tuple(DpadDownButton): "i",
    tuple(DpadLeftButton): "o",
    tuple(DpadRightButton): "p",
    tuple(HomeButton): "[",
}

currentHeldButtons = set()


def callback(recognizer, audio):
    try:
        print("recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said: {}".format(text))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(
                e
            )
        )


def main():
    while True:
        print("Listening...")
        text = get_audio()
        text = text.lower()

        # if we detected a wake word
        if any(WAKE_WORD.lower() in text for WAKE_WORD in WAKE_WORD):
            # get the wake word
            wake_word = next(
                (WAKE_WORD for WAKE_WORD in WAKE_WORD if WAKE_WORD in text), None
            )
            # get the text after the wake word
            command = text.split(wake_word, 1)[1]
            verbose_print("Woke up!")
            # get the text after the wake word
            # remove any extra spaces at the beginning
            command = command.lstrip()

            # detect which button was pressed
            detect_button(command)
            continue

        # scan for help phrases
        if check_for_help_phrases(text):
            print_help()
        else:
            # if we didn't get wake word, play error sound
            audio_error(
                "Your audio did not start with the wake word (Mario or Cloud). To see what you can say, say 'help me'"
            )


def print_help():
    print("The following commands are supported:")
    print("Press A")
    print("Press B")
    print("Press X")
    print("Press Y")
    print("Press Start")
    print("Press Select")
    print("Press Up")
    print("Press Down")
    print("Press Left")
    print("Press Right")
    print("Press Dpad Up")
    print("Press Dpad Down")
    print("Press Dpad Left")
    print("Press Dpad Right")
    print("Press Home")


def check_for_help_phrases(command):
    # scan for help phrases
    if any(phrase.lower() in command for phrase in HelpPhrases):
        verbose_print("Help detected!")
        return True

    # use spacy to detect similarity
    for phrase in HelpPhrases:
        if get_sentence_similarity(command, phrase.lower()) > 0.8:
            verbose_print("Help in spacy detected!")
            return True

    # use fuzzywuzzy to detect similarity
    for phrase in HelpPhrases:
        if fuzz.ratio(command, phrase.lower()) > 90:
            verbose_print("Help in fuzzywuzzy detected!")
            return True

    return False


def detect_button(command):
    # if any kind of stop word is in the command and we didn't pick it up, stop holding all buttons
    if any(phrase.lower() in command for phrase in StopPhrases):
        verbose_print("Stopping all held buttons...")
        pydirectinput.keyUp("l")
        pydirectinput.keyUp("r")
        pydirectinput.keyUp("a")
        pydirectinput.keyUp("b")
        pydirectinput.keyUp("x")
        pydirectinput.keyUp("y")
        pydirectinput.keyUp("enter")
        pydirectinput.keyUp(";")
        pydirectinput.keyUp("up")
        pydirectinput.keyUp("down")
        pydirectinput.keyUp("left")
        pydirectinput.keyUp("right")
        pydirectinput.keyUp("home")
        return

    # check if there is a hold phrase in the command
    hold = False
    holdPhraseIndex = 0
    for holdPhrase in HoldPhrases:
        if holdPhrase.lower() in command:
            hold = True
            holdPhraseIndex = command.index(holdPhrase.lower())
            break

    # if hold, trim the command to remove the hold phrase
    if hold:
        command = command[holdPhraseIndex + len(holdPhrase) :]
        # remove any extra spaces at the beginning
        command = command.lstrip()

    # do direct string comparison against each button first. If no match, do spacy similarity
    for buttonStringList in [
        LButton,
        RButton,
        AButton,
        BButton,
        XButton,
        YButton,
        StartButton,
        SelectButton,
        UpButton,
        DownButton,
        LeftButton,
        RightButton,
        DpadUpButton,
        DpadDownButton,
        DpadLeftButton,
        DpadRightButton,
        HomeButton,
    ]:
        for phrase in buttonStringList:
            if (
                fuzz.ratio(command, phrase.lower()) > 90
            ):  # might want to just do direct comparison (or use higher threshold)
                verbose_print("Direct match found!")

                # check if there is a hold phrase in the command
                if hold:
                    verbose_print("Holding button (" + phrase + ")...")
                    currentHeldButtons.add(BUTTON_MAPPINGS[tuple(buttonStringList)])
                    pydirectinput.keyDown(BUTTON_MAPPINGS[tuple(buttonStringList)])
                    return

                pydirectinput.press(BUTTON_MAPPINGS[tuple(buttonStringList)])
                return

    verbose_print("No direct match, comparing spacy...")
    # compare spacy similarity
    for buttonStringList in [
        LButton,
        RButton,
        AButton,
        BButton,
        XButton,
        YButton,
        StartButton,
        SelectButton,
        UpButton,
        DownButton,
        LeftButton,
        RightButton,
        DpadUpButton,
        DpadDownButton,
        DpadLeftButton,
        DpadRightButton,
        HomeButton,
    ]:
        for phrase in buttonStringList:
            if get_sentence_similarity(command, phrase.lower()) > 0.8:
                verbose_print("Spacy similarity match found!")

                # check if we need to hold the button
                if hold:
                    verbose_print("Holding button (" + phrase + ")...")
                    pydirectinput.keyDown(BUTTON_MAPPINGS[tuple(buttonStringList)])
                    return

                pydirectinput.press(BUTTON_MAPPINGS[tuple(buttonStringList)])
                return

    audio_error("Your command did not match any button.")


def get_sentence_similarity(sentence1, sentence2):
    # get similarity between two sentences using spacy
    doc1 = spacy_model(sentence1)
    doc2 = spacy_model(sentence2)
    return doc1.similarity(doc2)


def get_audio():
    # get audio from microphone and return as lowercased string
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, phrase_time_limit=3)
        try:
            text = r.recognize_google(audio, show_all=False)
            verbose_print("You said: " + text)
        except sr.UnknownValueError:
            audio_error("Google Speech Recognition could not understand audio")
            return ""
        return text.lower()


def audio_error(errorMsg):
    print(errorMsg + " Try again.")
    print("You can say things like:\n")
    print("Press A")
    print("Press the B button")
    print("Press right, etc\n")
    winsound.Beep(frequency, duration)
    return


def verbose_print(text):
    if VERBOSE:
        print(text)


if __name__ == "__main__":
    main()
