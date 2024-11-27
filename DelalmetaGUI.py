import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Define supported languages and their corresponding text
LANGUAGES = {
    "English": {
        "title": "Metadata Manager",
        "enter_path": "Enter Directory Path:",
        "browse": "Browse...",
        "delete_all_metadata": "Delete All Metadata",
        "artist_metadata": "Select Metadata Categories to Delete:",
        "new_metadata": "Add New Metadata:",
        "artist": "Artist:",
        "title_metadata": "Title:",
        "album": "Album:",
        "year": "Year:",
        "track_number": "Track Number:",
        "process": "Process Files",
        "success": "Files processed successfully!"
    },
    # Add more languages here
}

# Define metadata categories for different file types
METADATA_CATEGORIES = {
    "Image": ["Orientation", "ExifVersion", "DateTime"],
    "Audio": ["Artist", "Title", "Album", "Year", "TrackNumber"]
}

def get_selected_metadata_categories():
    return [category for category, var in metadata_vars.items() if var.get()]

def process_image_metadata(file_path, selected_categories):
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(file_path) as img:
            exif_data = {TAGS[k]: v for k, v in img._getexif().items() if k in TAGS}

            # Delete selected metadata categories
            for category in selected_categories:
                if category in exif_data:
                    del exif_data[category]

            # Save the image without the specified metadata
            img.save(file_path, quality=95)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_audio_metadata(file_path, selected_categories):
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3

        audio = MP3(file_path, ID3=ID3)

        # Delete selected metadata categories
        for category in selected_categories:
            if hasattr(audio.tags, category):
                delattr(audio.tags, category)

        # Save the audio without the specified metadata
        audio.save()
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_files(directory, selected_categories, new_metadata):
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    process_image_metadata(file_path, selected_categories)
                elif file_path.lower().endswith(('.mp3',)):
                    process_audio_metadata(file_path, selected_categories)

        # Add new metadata
        add_new_metadata(directory, new_metadata)
    except Exception as e:
        print(f"Error processing files in {directory}: {e}")

def add_new_metadata(directory, new_metadata):
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    from PIL import Image
                    img = Image.open(file_path)

                    # Add new metadata
                    exif_data = img.info['exif']
                    for key, value in new_metadata.items():
                        if value:
                            exif_data[key] = value

                    img.save(file_path, quality=95, exif=exif_data)
                elif file_path.lower().endswith(('.mp3',)):
                    from mutagen.mp3 import MP3
                    audio = MP3(file_path, ID3=ID3)

                    # Add new metadata
                    for key, value in new_metadata.items():
                        if value:
                            setattr(audio.tags, key, value)

                    audio.save()
    except Exception as e:
        print(f"Error adding new metadata to files in {directory}: {e}")

def get_new_metadata():
    return {
        'Artist': artist_entry.get(),
        'Title': title_entry.get(),
        'Album': album_entry.get(),
        'Year': year_entry.get(),
        'TrackNumber': track_number_entry.get()
    }

def process_files_button_click():
    directory = path_entry.get()
    if not os.path.isdir(directory):
        messagebox.showerror("Error", "Invalid directory path.")
        return

    selected_categories = get_selected_metadata_categories()
    new_metadata = get_new_metadata()

    process_files(directory, selected_categories, new_metadata)
    messagebox.showinfo("Success", "Files processed successfully!")

def update_ui_for_language(language):
    for widget, text in ui_elements.items():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
            widget.config(text=LANGUAGES[language][text])

def browse_button_click():
    path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(tk.END, path)

# Create the main window
root = tk.Tk()
root.title("Metadata Manager")

# Rest of your imports and function definitions remain the same
# Just remove any DND_FILES references

# Modified UI creation code
ui_elements = {}

path_label = tk.Label(root, text="Enter Directory Path:")
ui_elements[path_label] = "enter_path"
path_label.grid(row=0, column=0, padx=10, pady=10)

path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=1, padx=10, pady=10)

# Modified browse button functionality
def browse_button_click():
    path = filedialog.askdirectory()
    if path:  # Only update if a path was selected
        path_entry.delete(0, tk.END)
        path_entry.insert(tk.END, path)

browse_button = tk.Button(root, text="Browse...", command=browse_button_click)
ui_elements[browse_button] = "browse"
browse_button.grid(row=0, column=2, padx=10, pady=10)

delete_all_checkbox = tk.Checkbutton(root, text="Delete All Metadata")
delete_all_checkbox.grid(row=1, column=0, padx=10, pady=10)

metadata_categories_frame = ttk.LabelFrame(root, text="Select Metadata Categories to Delete:")
metadata_categories_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

metadata_vars = {}
for i, category in enumerate(METADATA_CATEGORIES["Image"] + METADATA_CATEGORIES["Audio"], start=1):
    metadata_var = tk.BooleanVar()
    metadata_checkbox = tk.Checkbutton(metadata_categories_frame, text=category, variable=metadata_var)
    metadata_vars[metadata_checkbox] = metadata_var
    metadata_checkbox.grid(row=i, column=0, padx=10, pady=5)

new_metadata_label = tk.Label(root, text="Add New Metadata:")
ui_elements[new_metadata_label] = "new_metadata"
new_metadata_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

artist_label = tk.Label(root, text="Artist:")
ui_elements[artist_label] = "artist"
artist_label.grid(row=4, column=0, padx=10, pady=5)
artist_entry = tk.Entry(root)
artist_entry.grid(row=4, column=1, padx=10, pady=5)

title_label = tk.Label(root, text="Title:")
ui_elements[title_label] = "title_metadata"
title_label.grid(row=5, column=0, padx=10, pady=5)
title_entry = tk.Entry(root)
title_entry.grid(row=5, column=1, padx=10, pady=5)

album_label = tk.Label(root, text="Album:")
ui_elements[album_label] = "album"
album_label.grid(row=6, column=0, padx=10, pady=5)
album_entry = tk.Entry(root)
album_entry.grid(row=6, column=1, padx=10, pady=5)

year_label = tk.Label(root, text="Year:")
ui_elements[year_label] = "year"
year_label.grid(row=7, column=0, padx=10, pady=5)
year_entry = tk.Entry(root)
year_entry.grid(row=7, column=1, padx=10, pady=5)

track_number_label = tk.Label(root, text="Track Number:")
ui_elements[track_number_label] = "track_number"
track_number_label.grid(row=8, column=0, padx=10, pady=5)
track_number_entry = tk.Entry(root)
track_number_entry.grid(row=8, column=1, padx=10, pady=5)

process_button = tk.Button(root, text="Process Files", command=process_files_button_click)
ui_elements[process_button] = "process"
process_button.grid(row=9, column=0, columnspan=3, padx=10, pady=20)

# Initialize UI for the default language
update_ui_for_language("English")

root.mainloop()