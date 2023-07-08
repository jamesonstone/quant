import tkinter as tk

def update_read_only_panel(event):
    content = text_entry.get("1.0", "end-1c")  # Get the text from the text box
    read_only_panel.config(state="normal")  # enable text entry for the read-only panel
    read_only_panel.delete("1.0", "end")  # Clear the read-only panel
    read_only_panel.insert("1.0", content)  # Insert the content from the text box
    # read_only_panel.config(state="disabled")  # Disable editing of the read-only panel

def switch_focus(event):
    if event.widget == text_entry:
        read_only_panel.focus_set()
    else:
        text_entry.focus_set()

root = tk.Tk()
root.title("quant_ai")
root.geometry("800x600")  # Set the initial size of the window

# Create the main container
main_container = tk.Frame(root)
main_container.grid(sticky="nsew")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Create the text entry pane
text_entry = tk.Text(main_container)
text_entry.grid(row=0, column=0, sticky="nsew")

# Create the read-only panel
read_only_panel = tk.Text(main_container, state="disabled")
read_only_panel.grid(row=0, column=1, sticky="nsew")

# Configure the weights of the grid rows and columns to make the panes fill the window
main_container.grid_columnconfigure(0, weight=1)
main_container.grid_columnconfigure(1, weight=1)
main_container.grid_rowconfigure(0, weight=1)

# Bind the update function to the KeyRelease event of the text entry
text_entry.bind("<KeyRelease>", update_read_only_panel)

# Bind the switch_focus function to the Command-] and Command-[ events
text_entry.bind("<Command-]>", switch_focus)
read_only_panel.bind("<Command-]>", switch_focus)
text_entry.bind("<Command-[>", switch_focus)
read_only_panel.bind("<Command-[>", switch_focus)

root.mainloop()
