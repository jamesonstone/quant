import tkinter as tk
import threading
import time

def processing(text):
    time.sleep(2)
    return text + "\n\nprocessed..."

def update_read_only_panel(event):
    global timer
    if timer is not None:
        timer.cancel()
    timer = threading.Timer(2, process_text)
    timer.start()

def process_text():
    content = text_entry.get("1.0", "end-1c")  # Get the text from the text box
    processed_content = processing(content)  # Process the text
    read_only_panel.config(state="normal")  # Enable text entry for the read-only panel
    existing_content = read_only_panel.get("1.0", "end")  # Get the existing content from the read-only panel
    read_only_panel.delete("1.0", "end")  # Clear the read-only panel
    read_only_panel.insert("1.0", processed_content)  # Insert the processed content at the top
    read_only_panel.insert("end", "\n------------------------------\n")  # Insert dividing line
    read_only_panel.insert("end", existing_content)  # Append the existing content
    read_only_panel.config(state="disabled")  # Disable editing of the read-only panel



root = tk.Tk()
root.title("quant_ai")
root.geometry("800x600")  # Set the initial size of the window

timer = None  # Initialize the timer

# Create the main container
main_container = tk.Frame(root)
main_container.pack(fill='both', expand=True)  # change from grid to pack manager for simplicity

# Create the text entry pane
text_entry = tk.Text(main_container)
text_entry.pack(side='left', fill='both', expand=True)

# Create the read-only panel
read_only_panel = tk.Text(main_container, state="disabled")
read_only_panel.pack(side='right', fill='both', expand=True)

# Bind the update function to the KeyRelease event of the text entry
text_entry.bind("<KeyRelease>", update_read_only_panel)

# Create a list of options for the dropdown box
options = ["OpenAI_GPT3.5", "OpenAI_GPT4", "LlamaCpp", "GPT4All"]

# Create a StringVar to store the selected option
selected_option = tk.StringVar()

# Set the default value of the StringVar to the first option
selected_option.set(options[0])

# Create the label for the dropdown box
dropdown_label = tk.Label(root)
dropdown_label.pack(side='left')  # place it at the bottom of the root window

# Create the dropdown box
dropdown = tk.OptionMenu(root, selected_option, *options)
dropdown.pack(side='left')  # place it at the bottom of the root window, to the right of the label

root.mainloop()
