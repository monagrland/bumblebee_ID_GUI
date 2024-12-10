import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
from datetime import date


# ------Load Meta Data------
meta_file = "meta.csv"
meta_data = pd.read_csv(meta_file, sep = ";")

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
    (data_all["validator"].isna() | (data_all["validator"] == "Photo recognition api"))
    & (data_all["landuse"] == "AX_Landwirtschaft")
]

# ------Tkinter Application------
class HummelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hummel-Challenge 2024")
        
        self.current_index = 0

        # Dropdown for observation selection
        self.row_label = tk.Label(root, text="Beobachtung wählen:")
        self.row_label.grid(row=0, column=0, padx=10, pady=10)

        self.row_dropdown = ttk.Combobox(root, values=data_todo["id"].tolist(), state="readonly")
        self.row_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.row_dropdown.current(0)

        # Buttons for navigation
        self.prev_button = tk.Button(root, text="Vorherige Beobachtung", command=self.previous_row)
        self.prev_button.grid(row=1, column=0, padx=10, pady=10)

        self.next_button = tk.Button(root, text="Nächste Beobachtung", command=self.next_row)
        self.next_button.grid(row=1, column=1, padx=10, pady=10)

        # Validator dropdown
        self.validator_label = tk.Label(root, text="Validator:")
        self.validator_label.grid(row=2, column=0, padx=10, pady=10)
        self.validator_dropdown = ttk.Combobox(root, values=validator_options, state="readonly")
        self.validator_dropdown.grid(row=2, column=1, padx=10, pady=10)
        self.validator_dropdown.current(0)

        # Bestimmung Validator searchable dropdown
        self.man_val_label = tk.Label(root, text="Bestimmung Validator:")
        self.man_val_label.grid(row=3, column=0, padx=10, pady=10)
        self.man_val_dropdown = AutocompleteCombobox(root, values=bees_options)
        self.man_val_dropdown.grid(row=3, column=1, padx=10, pady=10)

        # Best Guess searchable dropdown
        self.best_guess_label = tk.Label(root, text="Best Guess:")
        self.best_guess_label.grid(row=4, column=0, padx=10, pady=10)
        self.best_guess_dropdown = AutocompleteCombobox(root, values=bees_options)
        self.best_guess_dropdown.grid(row=4, column=1, padx=10, pady=10)

        # Food Plant searchable dropdown
        self.food_plant_label = tk.Label(root, text="Food Plant:")
        self.food_plant_label.grid(row=5, column=0, padx=10, pady=10)
        self.food_plant_dropdown = AutocompleteCombobox(root, values=plants_options)
        self.food_plant_dropdown.grid(row=5, column=1, padx=10, pady=10)

        # Geschlecht dropdown
        self.gender_label = tk.Label(root, text="Geschlecht:")
        self.gender_label.grid(row=6, column=0, padx=10, pady=10)
        self.gender_dropdown = ttk.Combobox(root, values=gender_options, state="readonly")
        self.gender_dropdown.grid(row=6, column=1, padx=10, pady=10)

        # Submit button
        self.submit_button = tk.Button(root, text="ABSCHICKEN", command=self.submit_data)
        self.submit_button.grid(row=7, column=0, columnspan=2, pady=20)

    def update_fields(self):
        # Load current row data into fields
        current_row = data_todo.iloc[self.current_index]
        self.row_dropdown.set(current_row["id"])
        self.man_val_dropdown.set(current_row.get("man_val", ""))
        self.best_guess_dropdown.set(current_row.get("best_guess", ""))
        self.food_plant_dropdown.set(current_row.get("food_plant", ""))
        self.gender_dropdown.set(current_row.get("gender", ""))

    def previous_row(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_fields()

    def next_row(self):
        if self.current_index < len(data_todo) - 1:
            self.current_index += 1
            self.update_fields()

    def submit_data(self):
        # Save current row data
        current_id = self.row_dropdown.get()
        selection = data_todo[data_todo["id"] == current_id].index[0]

        data_all.loc[selection, "validator"] = self.validator_dropdown.get()
        data_all.loc[selection, "man_val"] = self.man_val_dropdown.get()
        data_all.loc[selection, "best_guess"] = self.best_guess_dropdown.get()
        data_all.loc[selection, "food_plant"] = self.food_plant_dropdown.get()
        data_all.loc[selection, "gender"] = self.gender_dropdown.get()

        # Save updated data
        filename = f"daten_hummel_challenge_2024_v_{date.today()}_{self.validator_dropdown.get()}.csv"
        data_all.to_csv(filename, sep=";", index=False)
        messagebox.showinfo("Success", f"Data submitted successfully! File saved as {filename}")

# Run the app
root = tk.Tk()
app = HummelApp(root)
root.mainloop()
