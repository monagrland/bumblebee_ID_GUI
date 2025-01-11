import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import os
import webbrowser
import pyperclip
from searchable_combobox import SearchableComboBox
import pandas as pd
import io

# ------Load Meta Data------
meta_file = "meta.csv"
meta_data = pd.read_csv(meta_file, sep=";", encoding="latin-1")

validator_options = meta_data["validator"].dropna().unique().tolist()
bees_options = meta_data["bees"].dropna().unique().tolist()
plants_options = meta_data["plants"].dropna().unique().tolist()
gender_options = ["male", "female", "unknown"]

# ------READ DATA------
def select_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', 1)
    file_path = filedialog.askopenfilename(
        title="Select the data file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    root.destroy()
    return file_path

# ------Load the Data------
data_file_path = select_file()
data_all = pd.read_csv(data_file_path, delimiter=";")

# Ensure necessary columns exist
required_columns = ["man_val", "best_guess", "food_plant", "gender", "validator"]
for col in required_columns:
    if col not in data_all.columns:
        data_all[col] = None

# Filter the data based on conditions
data_todo = data_all[
    (data_all["validator name"].isna() | (data_all["validator name"] == "Photo recognition api"))
    & (data_all["landuse"] == "AX_Landwirtschaft") & (data_all["validator"].isna() | (data_all["validator"].isin(["LK", "Test"])))
]
data_todo = data_todo.reset_index(drop=True)


# Scrape the image URL
def get_image_src(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class': 'app-ratio-box-image'})
        img_sans_preview = images[:-1]
        img_url_lst = []
        for img in img_sans_preview:
            url_ending = img['src'].rsplit('?')[0]
            img_url_lst.append(f"https://observation.org{url_ending}")
        if len(img_url_lst) != 0:
            return img_url_lst
        else:
            return "Image tag with the specified criteria not found."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# ------Tkinter Application------
class HummelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hummel-Challenge 2024")
        
        self.current_index = 0
        self.previous_id = data_todo["id"].iloc[0]

        # Dropdown for observation selection
        self.row_label = tk.Label(root, text="Beobachtung wählen:")
        self.row_label.grid(row=0, column=0, padx=10, pady=10)

        self.row_dropdown = ttk.Combobox(root, values=data_todo["id"].tolist(), state="readonly")
        self.row_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.row_dropdown.current(0)
        self.row_dropdown.bind("<<ComboboxSelected>>", self.row_selected)
        
        # Add a canvas for the image
        self.image_canvas = tk.Canvas(root, width=300, height=300, bg="gray")
        self.image_canvas.grid(row=0, column=2, rowspan=8, padx=10, pady=10)
        
        # Navigation buttons
        self.prev_button = tk.Button(root, text="Vorherige Beobachtung", command=self.previous_row)
        self.prev_button.grid(row=1, column=0, padx=10, pady=10)

        self.next_button = tk.Button(root, text="Nächste Beobachtung", command=self.next_row)
        self.next_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons for opening and copying the link
        self.open_link_button = tk.Button(root, text="Open Link", command=self.open_link)
        self.open_link_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.copy_link_button = tk.Button(root, text="Copy Link", command=self.copy_link)
        self.copy_link_button.grid(row=2, column=1, padx=10, pady=10)
        
        # Validator dropdown
        self.validator_label = tk.Label(root, text="Validator:")
        self.validator_label.grid(row=3, column=0, padx=10, pady=10)
        self.validator_dropdown = ttk.Combobox(root, values=validator_options, state="readonly")
        self.validator_dropdown.grid(row=3, column=1, padx=10, pady=10)

        # Searchable combobox for bees
        self.man_val_label = tk.Label(root, text="Bestimmung Validator:")
        self.man_val_label.grid(row=4, column=0, padx=10, pady=10)
        self.man_val_dropdown = SearchableComboBox(root, bees_options)
        self.man_val_dropdown.grid(row=4, column=1, padx=10, pady=10)

        # Searchable combobox for best_guess
        self.best_guess_label = tk.Label(root, text="Best Guess:")
        self.best_guess_label.grid(row=5, column=0, padx=10, pady=10)
        self.best_guess_dropdown = SearchableComboBox(root, bees_options)
        self.best_guess_dropdown.grid(row=5, column=1, padx=10, pady=10)

        # Searchable combobox for plants
        self.food_plant_label = tk.Label(root, text="Food Plant:")
        self.food_plant_label.grid(row=6, column=0, padx=10, pady=10)
        self.food_plant_dropdown = SearchableComboBox(root, plants_options)
        self.food_plant_dropdown.grid(row=6, column=1, padx=10, pady=10)

        # Geschlecht dropdown
        self.gender_label = tk.Label(root, text="Geschlecht:")
        self.gender_label.grid(row=7, column=0, padx=10, pady=10)
        self.gender_dropdown = ttk.Combobox(root, values=gender_options, state="readonly")
        self.gender_dropdown.grid(row=7, column=1, padx=10, pady=10)

        # Submit button
        self.submit_button = tk.Button(root, text="SPEICHERN", command=self.submit_data)
        self.submit_button.grid(row=9, column=0, columnspan=2, pady=20)
        
        # Image navigation label
        self.image_label = tk.Label(root, text="")
        self.image_label.grid(row=7, column=2, pady=5)
        
        # Add a button to load the images
        self.load_image_button = tk.Button(root, text="Load Images", command=self.load_images)
        self.load_image_button.grid(row=8, column=2, padx=10, pady=10)

        # Frame for image navigation buttons
        self.image_nav_frame = tk.Frame(root)
        self.image_nav_frame.grid(row=9, column=2, pady=5)

        # Add buttons for image navigation inside the frame
        self.prev_image_button = tk.Button(self.image_nav_frame, text="< Previous Image", command=self.previous_image)
        self.prev_image_button.pack(side="left", padx=5)

        self.next_image_button = tk.Button(self.image_nav_frame, text="Next Image >", command=self.next_image)
        self.next_image_button.pack(side="right", padx=5)

    def clear_canvas(self):
        """Clear the image canvas."""
        self.image_canvas.delete("all")
        self.image_canvas.config(bg="gray")  # Reset background color

    def update_image_label(self):
        """Update the label showing the current image index."""
        if self.image_urls:
            self.image_label.config(text=f"{self.image_index + 1}/{len(self.image_urls)}")
        else:
            self.image_label.config(text="")

    def load_images(self):
        """Load images for the current row."""
        # Get the current row and fetch the link
        current_row = data_todo.iloc[self.current_index]
        link = current_row["link"]

        if pd.notna(link) and link.strip():
            # Scrape the image sources
            self.image_urls = get_image_src(link)
            if self.image_urls:
                self.image_index = 0  # Reset index
                self.display_image(self.image_urls[self.image_index])
            else:
                messagebox.showerror("Error", "No images found for the selected link.")
                self.image_urls = []
                self.clear_canvas()
        else:
            messagebox.showerror("Error", "No valid link found for this row.")
            self.image_urls = []

        self.update_image_label()  # Update the image label

    def display_image(self, image_src):
        try:
            response = requests.get(image_src, stream=True)
            response.raise_for_status()
            img_data = response.content

            # Open the image using Pillow
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((300, 300), Image.LANCZOS)  # Resize to fit the canvas
            img_tk = ImageTk.PhotoImage(img)

            # Clear the canvas and display the image
            self.clear_canvas()
            self.image_canvas.create_image(0, 0, anchor="nw", image=img_tk)
            self.image_canvas.image = img_tk  # Keep a reference to avoid garbage collection
        except Exception as e:
            print(f"Error displaying image: {e}")
            messagebox.showerror("Error", "Failed to load the image.")
            
    def next_image(self):
        """Show the next image in the list."""
        if self.image_urls and self.image_index < len(self.image_urls) - 1:
            self.image_index += 1
            self.display_image(self.image_urls[self.image_index])
        self.update_image_label()

    def previous_image(self):
        """Show the previous image in the list."""
        if self.image_urls and self.image_index > 0:
            self.image_index -= 1
            self.display_image(self.image_urls[self.image_index])
        self.update_image_label()

    def update_fields(self):
        # Load current row data into fields
        current_row = data_todo.iloc[self.current_index]
        
        self.row_dropdown.set(current_row["id"])
        self.man_val_dropdown.set(current_row["man_val"] if current_row["man_val"] is not None else "")
        self.best_guess_dropdown.set(current_row["best_guess"] if current_row["best_guess"] is not None else "")
        self.food_plant_dropdown.set(current_row["food_plant"] if current_row["food_plant"] is not None else "")
        self.gender_dropdown.set(current_row["gender"] if current_row["gender"] is not None else "")
        self.validator_dropdown.set(current_row["validator"] if pd.notna(current_row["validator"]) else "")

    def row_selected(self, event):
        # Save the current row data before switching to the new row
        self.save_previous_row()

        # Update the current_index based on the selected ID
        selected_id = int(self.row_dropdown.get())
        self.current_index = data_todo[data_todo["id"] == selected_id].index[0]

        # After selecting, update the fields to reflect the new data
        self.update_fields()
        
        self.previous_id = selected_id
        self.clear_canvas()  # Clear the canvas when changing the row

    def previous_row(self):
        # Save changes before moving to the previous row
        self.save_current_row()
    
        if self.current_index > 0:
            self.current_index -= 1
            self.update_fields()
            self.clear_canvas()  # Clear the canvas when changing the row
    
    def next_row(self):
        # Save changes before moving to the next row
        self.save_current_row()
    
        if self.current_index < len(data_todo) - 1:
            self.current_index += 1
            self.update_fields()
            self.clear_canvas()  # Clear the canvas when changing the row

    def save_current_row(self):
        # Get the current row based on the dropdown value
        current_id = int(self.row_dropdown.get())
        selection = data_todo[data_todo["id"] == current_id].index[0]
    
        # Save changes to the data_todo DataFrame
        data_todo.loc[selection, "man_val"] = self.man_val_dropdown.get()
        data_todo.loc[selection, "best_guess"] = self.best_guess_dropdown.get()
        data_todo.loc[selection, "food_plant"] = self.food_plant_dropdown.get()
        data_todo.loc[selection, "gender"] = self.gender_dropdown.get()
        data_todo.loc[selection, "validator"] = self.validator_dropdown.get()
        
    def save_previous_row(self):
        # Get the current row based on the dropdown value
        current_id = int(self.previous_id)
        selection = data_todo[data_todo["id"] == current_id].index[0]
    
        # Save changes to the data_todo DataFrame
        data_todo.loc[selection, "man_val"] = self.man_val_dropdown.get()
        data_todo.loc[selection, "best_guess"] = self.best_guess_dropdown.get()
        data_todo.loc[selection, "food_plant"] = self.food_plant_dropdown.get()
        data_todo.loc[selection, "gender"] = self.gender_dropdown.get()
        data_todo.loc[selection, "validator"] = self.validator_dropdown.get()
    
    def open_link(self):
        # Open the link in the default web browser
        current_row = data_todo.iloc[self.current_index]
        link = current_row["link"]
        if pd.notna(link) and link.strip():
            webbrowser.open(link)
        else:
            messagebox.showerror("Error", "No valid link found for this row.")
    
    def copy_link(self):
        # Copy the link to the clipboard
        current_row = data_todo.iloc[self.current_index]
        link = current_row["link"]
        if pd.notna(link) and link.strip():
            pyperclip.copy(link)
        else:
            messagebox.showerror("Error", "No valid link found for this row.")
    
    def submit_data(self):
        # Save current row data
        self.save_current_row()
        for index, row in data_todo.iterrows():
            current_id = row["id"]
            selection = data_all[data_all["id"] == current_id].index[0]
        
            data_all.loc[selection, "validator"] = row["validator"]
            data_all.loc[selection, "man_val"] = row["man_val"]
            data_all.loc[selection, "best_guess"] = row["best_guess"]
            data_all.loc[selection, "food_plant"] = row["food_plant"]
            data_all.loc[selection, "gender"] = row["gender"]

        # File save dialog
        default_dir = os.path.dirname(data_file_path)
        default_filename = f"{datetime.today().strftime('%d_%m_%Y')}.csv"
        file_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            initialdir=default_dir,
            initialfile=default_filename,
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )

        if file_path:
            data_all.to_csv(file_path, sep=";", index=False)
            messagebox.showinfo("Success", f"Data submitted successfully! File saved as {file_path}")

# Run the app
root = tk.Tk()
app = HummelApp(root)
root.mainloop()
