#Created by Owen Riddle 1/09/2025. This python app parses csv's for duplicate data and invalid file names. Has a simple GUI. Thanks for checking this out :)

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
from collections import defaultdict
import os
import re
from datetime import datetime

# Initialize the main window
root = tk.Tk()
root.title("WMATA Data Quality Validator")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

# Header
header_label = tk.Label(root, text="WMATA Data Quality Validator", font=("Helvetica", 16, "bold"), bg="#4a90e2", fg="white", pady=10)
header_label.pack(fill=tk.X)

# Subtitle
subtitle_label = tk.Label(root, text="Ensure procore or other data accuracy with customizable validation rules", font=("Helvetica", 12, "italic"), bg="#f0f0f0", fg="black", pady=5)
subtitle_label.pack(fill=tk.X)

# Global variables
validate_filenames = tk.BooleanVar(value=False)  # Variable to track file name validation checkbox
dataframes = []  # List to store loaded dataframes and file paths
current_year = datetime.now().year  # Get the current year

# Function to display help instructions
def show_help():
    instructions = """Data Quality Validator Instructions:

    1. Check 'Validate File Names' and enter a file name pattern if you want to validate file names.
       - Ensure this is done before loading files.
       
    2. Click 'Load Files' to upload your CSV, Excel, or JSON files.

    3. Enter required columns to check for missing columns and missing values.

    4. Optionally, enter a column to check for duplicates.
    """
    messagebox.showinfo("Help - Data Quality Validator", instructions)

# Frame for inputs and buttons
input_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
input_frame.pack(fill=tk.X, pady=5)

# Help button
help_button = tk.Button(input_frame, text="Help", command=show_help, bg="#4a90e2", fg="white", padx=10, pady=5)
help_button.grid(row=0, column=0, padx=5, pady=5)

# File name validation checkbox and dropdown
validate_filenames_checkbox = tk.Checkbutton(input_frame, text="Validate File Names", variable=validate_filenames, bg="#f0f0f0")
validate_filenames_checkbox.grid(row=0, column=1, padx=5, pady=5)

file_name_pattern_label = tk.Label(input_frame, text="Enter file name pattern (regex):", bg="#f0f0f0")
file_name_pattern_label.grid(row=0, column=2, sticky="w")

file_name_pattern_dropdown = tk.StringVar()
file_name_pattern_dropdown.set(r"^[A-Z]{2}\d{4,}_[A-Za-z]+_Invoices_\d{4}\.\d{2}\.\d{2}\.csv$")  # Default regex pattern
file_name_pattern_menu = tk.OptionMenu(input_frame, file_name_pattern_dropdown, r"^[A-Z]{2}\d{4,}_[A-Za-z]+_Invoices_\d{4}\.\d{2}\.\d{2}\.csv$")
file_name_pattern_menu.config(width=50)
file_name_pattern_menu.grid(row=0, column=3, padx=5)

# Load Files button
load_button = tk.Button(input_frame, text="Load Files", command=lambda: load_files(output_area), bg="#4a90e2", fg="white", padx=10, pady=5)
load_button.grid(row=1, column=0, padx=5, pady=5)

required_columns_label = tk.Label(input_frame, text="Enter required columns (comma-separated):", bg="#f0f0f0")
required_columns_label.grid(row=1, column=1, sticky="w")

required_columns_entry = tk.Entry(input_frame, width=50)
required_columns_entry.grid(row=1, column=2, padx=5)

duplicate_column_label = tk.Label(input_frame, text="Enter column to check for duplicates:", bg="#f0f0f0")
duplicate_column_label.grid(row=2, column=1, sticky="w")

duplicate_column_entry = tk.Entry(input_frame, width=50)
duplicate_column_entry.grid(row=2, column=2, padx=5)

validate_button = tk.Button(input_frame, text="Validate Data", command=lambda: validate_data(output_area), bg="#4a90e2", fg="white", padx=10, pady=5)
validate_button.grid(row=2, column=0, padx=5, pady=5)

# Frame for output area
output_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
output_frame.pack(fill=tk.BOTH, expand=True)

output_area = scrolledtext.ScrolledText(output_frame, width=100, height=30, borderwidth=2, relief="solid")
output_area.pack(fill=tk.BOTH, expand=True)

# Configure tags for output formatting
output_area.tag_config("bold", font=("Helvetica", 10, "bold"))
output_area.tag_config("indent", lmargin1=20, lmargin2=20)

#Welcome message
output_area.insert(tk.END, "Welcome Lumenor/Procon! See help button above if needed\n")

# Function to load multiple files (CSV, Excel, JSON)
def load_files(output_area):
    file_name_pattern = file_name_pattern_dropdown.get().strip()
    if validate_filenames.get() and not file_name_pattern:
        messagebox.showwarning("Warning", "Please enter a file name pattern for validation.")
        return
    global dataframes, selected_files
    selected_files = filedialog.askopenfilenames(filetypes=[
        ("All Supported Files", "*.csv *.xlsx *.json"),
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx"),
        ("JSON files", "*.json")
    ])
    if selected_files:
        dataframes.clear()
        output_area.delete(1.0, tk.END)

        total_rows_all_files = 0  # Initialize total row count

        for file_path in selected_files:
            try:
                file_name = os.path.basename(file_path)  # Get the file name without path

                # Validate file name if checkbox is checked
                if validate_filenames.get():
                    is_valid = True
                    if not re.match(file_name_pattern, file_name):
                        output_area.insert(tk.END, f"File: {file_name} (Invalid)\n", "bold")
                        output_area.insert(tk.END, "Reason:\n", "indent")
                        output_area.insert(tk.END, f"  - The file name does not match the expected pattern:\n    {file_name_pattern}\n", "indent")
                        is_valid = False

                    # Check if the file name year matches the current year
                    match = re.search(r'_(\d{4})\.\d{2}\.\d{2}\.csv$', file_name)
                    if match:
                        file_year = int(match.group(1))
                        if file_year != current_year:
                            if is_valid:
                                output_area.insert(tk.END, f"File: {file_name} (Invalid)\n", "bold")
                                output_area.insert(tk.END, "Reason:\n", "indent")
                            output_area.insert(tk.END, f"  - The file is not from the current year. Expected: {current_year}, Found: {file_year}\n", "indent")
                            is_valid = False

                    if not is_valid:
                        output_area.insert(tk.END, "\n")
                        continue  # Skip this file if it doesn't match the pattern or year
                    else:
                        output_area.insert(tk.END, f"File: {file_name} (Valid)\n", "bold")

                # Load the file if it passes validation
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                elif file_path.endswith(".json"):
                    df = pd.read_json(file_path)
                else:
                    raise ValueError("Unsupported file format")

                dataframes.append((df, file_path))
                output_area.insert(tk.END, f"Loaded file: {file_path}\n")
                output_area.insert(tk.END, f"Columns: {', '.join(df.columns)}\n\n")

                # Add data summary for each file
                num_rows = len(df)
                total_rows_all_files += num_rows  # Increment total row count
                output_area.insert(tk.END, f"Summary for {file_name}:\n")
                output_area.insert(tk.END, f"  - Total rows: {num_rows}\n")
                output_area.insert(tk.END, f"  - Total columns: {len(df.columns)}\n\n")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file '{file_path}': {e}")

        # Display total rows across all files
        output_area.insert(tk.END, f"\nTotal rows across all files: {total_rows_all_files}\n", "bold")
        output_area.insert(tk.END, "All selected files have been processed.\n")
        
# Function to validate data in multiple files based on user-defined rules and compare invoice numbers across files
def validate_data(output_area):
    global dataframes
    if not dataframes:
        messagebox.showwarning("Warning", "No files loaded. Please load files first.")
        return

    required_columns = required_columns_entry.get().split(",")
    duplicate_column = duplicate_column_entry.get().strip()
    overall_errors = []
    invoice_tracker = defaultdict(set)  # Dictionary to track invoices and the files they appear in

    for df, file_path in dataframes:
        errors = []
        file_name = file_path.split("/")[-1]

        # Check for missing required columns and values
        for column in required_columns:
            column = column.strip()
            if column not in df.columns:
                errors.append(f"Missing required column: {column}")
            elif df[column].isnull().any():
                missing_count = df[column].isnull().sum()
                errors.append(f"Column '{column}' has {missing_count} missing values")

        # Check for duplicates in the specified column
        if duplicate_column:
            if duplicate_column not in df.columns:
                errors.append(f"Duplicate check column '{duplicate_column}' not found")
            else:
                # Preprocess the column: convert to string, strip spaces, and remove non-printable characters
                df[duplicate_column] = df[duplicate_column].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

                # Identify duplicates within the file
                duplicates = df[duplicate_column].duplicated(keep=False)
                if duplicates.any():
                    duplicate_values = df.loc[duplicates, duplicate_column].value_counts()
                    errors.append(f"Found {len(duplicate_values)} unique duplicate values in '{duplicate_column}'")

                    for value, count in duplicate_values.items():
                        indices = df.loc[df[duplicate_column] == value].index.tolist()
                        errors.append(f"  - '{value}' appears {count} times at rows: {indices}")

                # Track invoice numbers across files
                for invoice in df[duplicate_column]:
                    invoice_tracker[invoice].add(file_name)

        # Collect errors for each file
        if errors:
            overall_errors.append(f"Validation Errors in '{file_name}':\n  - " + "\n  - ".join(errors))
        else:
            overall_errors.append(f"No validation errors found in '{file_name}'.")

    # Compare invoice numbers across files and identify duplicates
    cross_file_duplicates = {inv: files for inv, files in invoice_tracker.items() if len(files) > 1}
    if cross_file_duplicates:
        overall_errors.append("\nDuplicate Invoices Found Across Files:")
        for inv, files in cross_file_duplicates.items():
            overall_errors.append(f"  - Invoice '{inv}' appears in files: {', '.join(files)}")

    # Display overall results
    output_area.delete(1.0, tk.END)
    output_area.insert(tk.END, "\n\n".join(overall_errors))

# Run the main event loop
root.mainloop()
