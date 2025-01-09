import tkinter as tk
from PIL import Image, ImageTk

class SearchableComboBox():
    def __init__(self, parent, options):
        self.dropdown_id = None
        self.options = options

        # Create a wrapper Frame to manage the layout
        self.wrapper = tk.Frame(parent)
        self.wrapper.grid()  # Use grid() to place it in the parent widget

        # Entry field for typing and searching
        self.entry = tk.Entry(self.wrapper, width=24)
        self.entry.bind("<KeyRelease>", self.on_entry_key)
        self.entry.bind("<FocusIn>", self.show_dropdown) 
        self.entry.grid(row=0, column=0, sticky="ew")  # Use grid() instead of pack()

        # Dropdown icon/button
        self.icon_path = "dropdown_arrow.png"
        self.icon = ImageTk.PhotoImage(Image.open(self.icon_path).resize((16, 16)))
        tk.Button(self.wrapper, image=self.icon, command=self.show_dropdown).grid(row=0, column=1)

        # Listbox for dropdown options
        self.listbox = tk.Listbox(parent, height=5, width=30)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for option in self.options:
            self.listbox.insert(tk.END, option)

    def grid(self, **kwargs):
        self.wrapper.grid(**kwargs)

    def on_entry_key(self, event):
        typed_value = event.widget.get().strip().lower()
        if not typed_value:
            self.listbox.delete(0, tk.END)
            for option in self.options:
                self.listbox.insert(tk.END, option)
        else:
            self.listbox.delete(0, tk.END)
            filtered_options = [option for option in self.options if typed_value in option.lower()]
            for option in filtered_options:
                self.listbox.insert(tk.END, option)
        self.show_dropdown()

    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_option = self.listbox.get(selected_index)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, selected_option)
            self.hide_dropdown()

    def show_dropdown(self, event=None):
        self.listbox.place(in_=self.entry, x=0, rely=1, relwidth=1.0, anchor="nw")
        self.listbox.lift()

        # Show dropdown for 2 seconds
        if self.dropdown_id: 
            self.listbox.after_cancel(self.dropdown_id)
        self.dropdown_id = self.listbox.after(2000, self.hide_dropdown)

    def hide_dropdown(self):
        self.listbox.place_forget()

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
