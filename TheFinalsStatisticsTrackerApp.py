from pytesseract import pytesseract
pytesseract.tesseract_cmd = r'J:\Coding\Tesseract\tesseract.exe'
from tkinter import Tk, Label, Button, Frame, Text, Canvas, Scrollbar, ttk, PhotoImage
import pyautogui
from PIL import Image, ImageTk
from pytesseract import image_to_string
import os

# Global variables
all_screenshots = []  # To store all screenshot paths
search_string = "SOWEREINCOPPER"  # String to search in the text
stats_y_offset = 125  # Start near the bottom of the canvas for stats
calculated_stats_table = None  # Placeholder for the calculated stats table

total_eliminations = 0
total_deaths = 0
total_assists = 0
total_revives = 0

# Function to take a screenshot
def take_screenshot():
    global screenshot_label, text_display, Stats_canvas, stats_y_offset

    # Clear previous screenshot and text
    screenshot_label.config(image="")
    screenshot_label.image = None
    text_display.delete("1.0", "end")

    # Take and save the screenshot
    screenshot = pyautogui.screenshot()
    screenshot_path = f"screenshot_{len(all_screenshots)+1}.png"
    screenshot.save(screenshot_path)
    all_screenshots.append(screenshot_path)

    # Load and display the new screenshot
    img = Image.open(screenshot_path)
    img = img.resize((500, 300))  # Resize for display
    img = ImageTk.PhotoImage(img)
    screenshot_label.config(image=img)
    screenshot_label.image = img

    # Extract and display text
    text = image_to_string(Image.open(screenshot_path))
    text_display.insert("end", f"Extracted Text:\n{text}\n\n")
    text_display.see("end")

    # Search for the string and display in the stats tab
    for line in text.split("\n"):
        if search_string in line:
            # Dynamically add text to the stats tab
            Stats_canvas.create_text(
                1160, stats_y_offset, text=line, font=("Arial", 20), fill="black", anchor="center"
            )
            stats_y_offset += 30  # Decrement offset for stack effect

            # Parse and add to the Calculated Stats table
            parse_and_update_table(line)

    # Update third tab with all screenshots
    update_screenshot_tab()

# Function to parse the line and update the table
def parse_and_update_table(line):
    global calculated_stats_table, total_eliminations, total_deaths, total_assists, total_revives

    # Split the line and extract relevant data
    parts = line.split()
    class_type = parts[0]  # First part is the class
    name = parts[1]  # Second part is the name

    # Extract numbers, skipping symbols
    numbers = [int(s) for s in parts if s.isdigit()]

    if len(numbers) == 7:  # Ensure all required stats are present
        eliminations, assists, deaths, revives, combat, support, objective = numbers

        # Update cumulative stats
        total_eliminations += eliminations
        total_deaths += deaths
        total_assists += assists
        total_revives += revives

        # Insert a new row at the top of the table
        calculated_stats_table.insert(
            "", 0,  # "" means top-level, "0" adds it to the top
            values=(class_type, name, eliminations, assists, deaths, revives, combat, support, objective)
        )

        # Update stats display on the main page
        update_main_stats_display()

def update_main_stats_display():
    global total_eliminations, total_deaths, total_assists, total_revives

    e_d = total_eliminations / total_deaths if total_deaths > 0 else total_eliminations
    e_d_label.config(text=f"E/D: {e_d:.2f}")
    assists_label.config(text=f"Assists: {total_assists}")
    revives_label.config(text=f"Revives: {total_revives}")

# Function to update the screenshots tab
def update_screenshot_tab():
    for widget in screenshots_frame.winfo_children():
        widget.destroy()

    for i, screenshot_path in enumerate(reversed(all_screenshots)):  # Newest first
        img = Image.open(screenshot_path)
        img = img.resize((300, 180))  # Larger size for better visibility
        img = ImageTk.PhotoImage(img)
        img_label = Label(screenshots_frame, image=img)
        img_label.image = img
        img_label.grid(row=i // 6, column=i % 6, padx=6, pady=0)

# Function to clear stats
def clear_app():
    screenshot_label.config(image="")
    screenshot_label.image = None
    text_display.delete("1.0", "end")

# Function to handle the hotkey
def handle_hotkey(event):
    take_screenshot()

# Function to stop the program
def stop_program():
    root.destroy()

# Initialize the app window
root = Tk()
root.title("The Finals Statistics Tracker")
root.geometry("2000x772")  # Full HD resolution

# Create a styled theme for the UI
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", font=("Arial", 16, "bold"), padding=[10, 5])
style.configure("TButton", font=("Arial", 14), padding=[5, 5])
style.configure("TLabel", font=("Arial", 14))

# Load background image
background_img = PhotoImage(file="S4_top_web_banner.png")

# Create a tabbed interface
tabs = ttk.Notebook(root)
main_tab = Frame(tabs)
calculated_stats_tab = Frame(tabs)
stats_tab = Frame(tabs)
screenshots_tab = Frame(tabs)
tabs.add(main_tab, text="Main")
tabs.add(calculated_stats_tab, text="Calculated Stats")
tabs.add(stats_tab, text="Stats")
tabs.add(screenshots_tab, text="Screenshots")
tabs.pack(fill="both", expand=True)

# Main Tab
title_label = Label(main_tab, text="The Finals Statistics Tracker", font=("Arial", 36, "bold"), bg="#292b2c", fg="white")
title_label.pack(pady=20, fill="x")

button_frame = Frame(main_tab, bg="#292b2c")
button_frame.pack(fill="x", pady=10)

capture_button = ttk.Button(button_frame, text="Capture Screenshot", command=take_screenshot)
capture_button.pack(side="left", padx=20)
clear_button = ttk.Button(button_frame, text="Clear App", command=clear_app)
clear_button.pack(side="left", padx=20)
stop_button = Button(button_frame, text="Stop Program", command=stop_program, bg="red", fg="white", font=("Arial", 14))
stop_button.pack(side="left", padx=20)

content_frame = Frame(main_tab)
content_frame.pack(fill="both", expand=True, pady=20)

canvas = Canvas(content_frame)
scrollbar = Scrollbar(content_frame, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

screenshot_label = Label(scrollable_frame)
screenshot_label.pack()
text_display = Text(scrollable_frame, wrap="word", height=20, font=("Arial", 16))
text_display.pack(fill="both", expand=True)

# Stats Display Frame
stats_frame = Frame(main_tab, bg="#292b2c")
stats_frame.pack(side="right", padx=30, pady=30)

e_d_label = Label(stats_frame, text="E/D: 0", font=("Arial", 35, "bold"), bg="#292b2c", fg="white")
e_d_label.pack(anchor="w", pady=5)
assists_label = Label(stats_frame, text="Assists: 0", font=("Arial", 35, "bold"), bg="#292b2c", fg="white")
assists_label.pack(anchor="w", pady=5)
revives_label = Label(stats_frame, text="Revives: 0", font=("Arial", 35, "bold"), bg="#292b2c", fg="white")
revives_label.pack(anchor="w", pady=5)

# Calculated Stats Tab
columns = ("Class", "Name", "Eliminations", "Assists", "Deaths", "Revives", "Combat", "Support", "Objective")
calculated_stats_table = ttk.Treeview(calculated_stats_tab, columns=columns, show="headings", height=20)

# Define headings
for col in columns:
    calculated_stats_table.heading(col, text=col)
    calculated_stats_table.column(col, width=150, anchor="center")

calculated_stats_table.pack(fill="both", expand=True, padx=20, pady=10)

# Stats Tab
Stats_canvas = Canvas(stats_tab, width=2000, height=772)
Stats_canvas.pack(fill="both")
Stats_canvas.create_image(0, 0, image=background_img, anchor="nw")
Stats_canvas.create_text(1160, 50, text="Statistics", font=("Arial", 55, "bold"), fill="Black")

# Screenshots Tab
Screenshots_canvas = Canvas(screenshots_tab, width=2000, height=772)
Screenshots_canvas.pack(fill="both")
Screenshots_canvas.create_image(0, 0, image=background_img, anchor="nw")
Screenshots_canvas.create_text(1160, 50, text="All Screenshots", font=("Arial", 55, "bold"), fill="Black")
screenshots_frame = Frame(screenshots_tab)
screenshots_frame_window = Screenshots_canvas.create_window(10, 100, anchor="nw", window=screenshots_frame)

# Hotkey binding
root.bind("<Tab>", handle_hotkey)

# Run the app
root.mainloop()



# ------------ Unused Testing Code ------------ #
# screenshots_frame.pack(fill="both", pady=20)#expand=True)
# my_canvas.create_text(960,100, text="All Screenshots", font=("Arial", 28, "bold"))
# screenshots_label = Label(screenshots_tab, text="All Screenshots", font=("Arial", 28, "bold"))
# screenshots_label.pack(pady=20)

# stats_label = Label(stats_tab, text="Statistics", font=("Arial", 28, "bold"))
# stats_label.pack(pady=20)
# stats_display = Label(stats_tab, text="", font=("Arial", 16), wraplength=1600, justify="left", bg="white", anchor="n")
# stats_display.pack(pady=10, fill="both", expand=True)



# M SOWEREINCOPPER 10 1 3 4 1000 500 600