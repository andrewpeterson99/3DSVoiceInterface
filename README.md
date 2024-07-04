# 3DSVoiceInterface
 A voice interface for the Nintendo 3DS that uses Keyboard I/O redirection. Uses word embeddings to detect wake words and voice commands and map them to defined intents.

# Requirements

- A Nintendo 3DS with Homebrew access (install NTR CFW so you can listen to input from the PC running this program)
- A computer with Python 3.6 or higher installed
- A microphone connected to the computer

# Usage

1. Run the file `keyboard_input.py` on your computer
2. Use x360ce to map the keyboard keys to the 3DS buttons (see program for reference)
3. Connect the 3DS to the computer using NTR CFW and have it listen for input
4. Use voice commands to control the 3DS via a wake word (e.g. "Mario" to wake up the 3DS and " Press the A button" to press the A button)