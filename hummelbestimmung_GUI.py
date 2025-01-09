import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import os
import webbrowser
import pyperclip
from searchable_combobox import SearchableComboBox

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
        
        # Buttons for navigation
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
        self.submit_button.grid(row=8, column=0, columnspan=2, pady=20)


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

    def previous_row(self):
        # Save changes before moving to the previous row
        self.save_current_row()
    
        if self.current_index > 0:
            self.current_index -= 1
            self.update_fields()
    
    def next_row(self):
        # Save changes before moving to the next row
        self.save_current_row()
    
        if self.current_index < len(data_todo) - 1:
            self.current_index += 1
            self.update_fields()

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
