import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from datetime import date
from dash import Dash, html, dcc, Input, Output, State



# ------READ DATA------
def select_file():
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', 1)  # Bring the file dialog to the foreground
    file_path = filedialog.askopenfilename(
        title="Select the data file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    root.destroy()  # Destroy the hidden root window
    return file_path


# ------READ DATA------
# data_all = pd.read_csv("challenge-welche-hummel-brummt-denn-da-waarnemingen_landuse_2024-10-07.csv", delimiter=";")
data_file_path = select_file()
data_all = pd.read_csv(data_file_path, delimiter=";")

# ------SELECT DATA------
# Ensure necessary columns exist
required_columns = ["man_val", "best_guess", "food_plant", "gender", "validator"]
for col in required_columns:
    if col not in data_all.columns:
        data_all[col] = None
test = data_all.columns
# Filter the data based on conditions
data_todo = data_all[
    (data_all.get("validator").isna() | (data_all.get("validator") == "Photo recognition api"))
    & (data_all["landuse"] == "AX_Landwirtschaft")
]


app = Dash(__name__)

# Populate options for dropdowns
row_options = [{"label": str(id), "value": id} for id in data_todo["id"]]
validator_options = [{"label": name, "value": name} for name in ["SO", "JM", "LK", "Test"]]

app.layout = html.Div([
    html.H1("Hummel-Challenge 2024"),
    html.Div([
        html.Label("Beobachtung wählen:"),
        dcc.Dropdown(id="row-dropdown", options=row_options, value=row_options[0]["value"] if row_options else None)
    ]),
    html.Div([
        html.Button("Vorherige Beobachtung", id="prev-button"),
        html.Button("Nächste Beobachtung", id="next-button"),
    ]),
    html.Br(),
    html.Div([
        html.Label("Validator:"),
        dcc.Dropdown(id="validator-dropdown", options=validator_options, value="JM")
    ]),
    html.Div([
        html.Label("Bestimmung Validator:"),
        dcc.Input(id="man-val-input", type="text")
    ]),
    html.Div([
        html.Label("Best Guess:"),
        dcc.Input(id="best-guess-input", type="text")
    ]),
    html.Div([
        html.Label("Food Plant:"),
        dcc.Input(id="food-plant-input", type="text")
    ]),
    html.Div([
        html.Label("Geschlecht:"),
        dcc.Input(id="gender-input", type="text")
    ]),
    html.Button("ABSCHICKEN", id="submit-button"),
    html.Div(id="output-status")
])

@app.callback(
    Output("output-status", "children"),
    Input("submit-button", "n_clicks"),
    State("row-dropdown", "value"),
    State("validator-dropdown", "value"),
    State("man-val-input", "value"),
    State("best-guess-input", "value"),
    State("food-plant-input", "value"),
    State("gender-input", "value"),
    prevent_initial_call=True
)
def submit_data(n_clicks, row, validator, man_val, best_guess, food_plant, gender):
    if row:
        selection = data_todo[data_todo["id"] == row].index[0]
        data_all.loc[selection, "validator"] = validator
        data_all.loc[selection, "man_val"] = man_val
        data_all.loc[selection, "best_guess"] = best_guess
        data_all.loc[selection, "food_plant"] = food_plant
        data_all.loc[selection, "gender"] = gender

        # Save the updated data
        filename = f"daten_hummel_challenge_2024_v_{date.today()}_{validator}.csv"
        data_all.to_csv(filename, sep=";", index=False)
        return f"Data submitted successfully! File saved as {filename}."

if __name__ == "__main__":
    app.run(debug=True)
