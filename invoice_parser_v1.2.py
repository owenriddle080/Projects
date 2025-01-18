import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import re
import csv
from collections import Counter

class InvoiceParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Parser App")
        self.root.geometry("700x1000")
        self.root.resizable(False, False)

        # Modern UI Elements
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TLabel", font=("Arial", 14))

        self.label = ttk.Label(root, text="Upload invoice PDFs to extract details")
        self.label.pack(pady=20)

        self.upload_button = ttk.Button(root, text="Upload PDFs", command=self.upload_pdfs)
        self.upload_button.pack(pady=10)

        self.result_text = tk.Text(root, height=30, width=60, font=("Courier", 10))
        self.result_text.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.export_button = ttk.Button(root, text="Export to CSV", command=self.export_to_csv, state=tk.DISABLED)
        self.export_button.pack(pady=10)

        self.extracted_data = []
        self.invoice_numbers = Counter()
        self.warnings = {"duplicates": []}

    def upload_pdfs(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if file_paths:
            self.parse_pdfs(file_paths)
            self.display_warnings()

    def parse_pdfs(self, file_paths):
        self.extracted_data.clear()
        self.result_text.delete(1.0, tk.END)
        self.invoice_numbers.clear()
        self.warnings = {"duplicates": []}

        self.progress["maximum"] = len(file_paths)
        self.progress["value"] = 0

        for i, file_path in enumerate(file_paths):
            try:
                with pdfplumber.open(file_path) as pdf:
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()
                    
                    # Normalize text by replacing non-breaking spaces and line breaks with regular spaces
                    text = re.sub(r"\s+", " ", text.replace("\u00a0", " ").replace("\n", " "))
                    
                    print(repr(text))  # Debug: Print normalized text to check formatting

                    # Extract fields using regex with error handling
                    contract_match = re.search(r"Contract\s*Number:\s*(\S+)", text)
                    contract = contract_match.group(1) if contract_match else "N/A"

                    date_match = re.search(r"Invoice\s*Date:\s*([\d/]+)", text)
                    invoice_date = date_match.group(1) if date_match else "N/A"

                    number_match = re.search(r"Invoice\s*Number:\s*(\S+)", text)
                    invoice_number = number_match.group(1) if number_match else "N/A"

                    task_order_match = re.search(r"Task\s*Order\s*Number:\s*(\S+)", text)
                    task_order_number = task_order_match.group(1) if task_order_match else "N/A"

                    billing_period_match = re.search(r"Billing\s*Period:\s*([\d/]+\s*-\s*[\d/]+)", text)
                    billing_period = billing_period_match.group(1) if billing_period_match else "N/A"

                    total_invoice_match = re.search(r"TOTAL\s*THIS\s*INVOICE.*?\$\s*([\d\s,\.]+)", text, re.DOTALL)
                    if total_invoice_match:
                        total_invoice = re.sub(r"\s+", "", total_invoice_match.group(1))
                    else:
                        total_invoice = "N/A"

                    total_billed_match = re.search(r"Total\s*Billed\s*To\s*Date\s*:\s*\$\s*([\d\s,\.]+)", text, re.IGNORECASE)
                    if total_billed_match:
                        total_billed = re.sub(r"\s+", "", total_billed_match.group(1))
                    else:
                        total_billed = "N/A"

                    dbe_billed_match = re.search(r"DBE\s*Billed\s*To\s*Date:\s*([\d\s,\.]+)", text)
                    if dbe_billed_match:
                        dbe_billed = re.sub(r"\s+", "", dbe_billed_match.group(1))
                    else:
                        dbe_billed = "N/A"

                    # Locate 'Task Order DBE Spending Data' and extract the next three dollar amounts
                    dbe_section_index = text.find("Task Order DBE Spending Data")
                    if dbe_section_index != -1:
                        print("Found 'Task Order DBE Spending Data' section")  # Debug: Confirm section found
                        # Extract the text after the section and search for dollar amounts
                        following_text = text[dbe_section_index:]
                        
                        # Updated regex to handle potential spaces within numeric values
                        amounts = re.findall(r"\$\s*([\d\s,\.]+)", following_text)

                        print(f"Extracted amounts (raw): {amounts}")  # Debug: Check raw extracted amounts

                        # Clean extracted amounts by removing all spaces
                        cleaned_amounts = [re.sub(r"\s+", "", amount) for amount in amounts]

                        print(f"Extracted amounts (cleaned): {cleaned_amounts}")  # Debug: Check cleaned amounts

                        # Ensure the cleaned amounts list contains at least three entries
                        if len(cleaned_amounts) >= 3:
                            previously_billed_dbe = cleaned_amounts[0]
                            total_this_invoice_dbe = cleaned_amounts[1]
                            billed_to_date_dbe = cleaned_amounts[2]
                        else:
                            previously_billed_dbe = "N/A"
                            total_this_invoice_dbe = "N/A"
                            billed_to_date_dbe = "N/A"
                    else:
                        previously_billed_dbe = "N/A"
                        total_this_invoice_dbe = "N/A"
                        billed_to_date_dbe = "N/A"

                    # Check for duplicate invoice numbers
                    self.invoice_numbers[invoice_number] += 1
                    if self.invoice_numbers[invoice_number] > 1:
                        self.warnings["duplicates"].append(invoice_number)

                    self.extracted_data.append({
                        "File": file_path.split("/")[-1],
                        "Contract #": contract,
                        "Invoice Date": invoice_date,
                        "Invoice Number": invoice_number,
                        "Task Order Number": task_order_number,
                        "Billing Period": billing_period,
                        "Total This Invoice": total_invoice,
                        "Total Billed To Date": total_billed,
                        "DBE Previously Billed": previously_billed_dbe,
                        "DBE Total This Invoice": total_this_invoice_dbe,
                        "DBE Billed To Date": billed_to_date_dbe
                    })

                    # Display extracted data in the text widget
                    self.result_text.insert(tk.END, f"File: {file_path.split('/')[-1]}\n")
                    self.result_text.insert(tk.END, f"Contract #: {contract}\n")
                    self.result_text.insert(tk.END, f"Invoice Date: {invoice_date}\n")
                    self.result_text.insert(tk.END, f"Invoice Number: {invoice_number}\n")
                    self.result_text.insert(tk.END, f"Task Order Number: {task_order_number}\n")
                    self.result_text.insert(tk.END, f"Billing Period: {billing_period}\n")
                    self.result_text.insert(tk.END, f"Total This Invoice: {total_invoice}\n")
                    self.result_text.insert(tk.END, f"Total Billed To Date: {total_billed}\n")
                    self.result_text.insert(tk.END, f"DBE Previously Billed: {previously_billed_dbe}\n")
                    self.result_text.insert(tk.END, f"DBE Total This Invoice: {total_this_invoice_dbe}\n")
                    self.result_text.insert(tk.END, f"DBE Billed To Date: {billed_to_date_dbe}\n")
                    self.result_text.insert(tk.END, "\n-------------------------------------------\n")

                self.export_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse {file_path}: {e}")

            # Update progress bar
            self.progress["value"] = i + 1
            self.root.update_idletasks()

    def display_warnings(self):
        self.result_text.insert(tk.END, "\nWarnings Summary:\n", "warning")

        if self.warnings["duplicates"]:
            self.result_text.insert(tk.END, "Duplicate Invoice Numbers:\n", "warning")
            for duplicate in set(self.warnings["duplicates"]):
                self.result_text.insert(tk.END, f"  - {duplicate}\n", "warning")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=["File", "Contract #", "Invoice Date", "Invoice Number", "Task Order Number", "Billing Period", "Total This Invoice", "Total Billed To Date", "DBE Previously Billed", "DBE Total This Invoice", "DBE Billed To Date"])
                    writer.writeheader()
                    writer.writerows(self.extracted_data)
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")

if __name__ == "__main__":
    root = tk.Tk()

    # Add custom tags for warnings
    root.option_add('*Text.warning', 'foreground red')

    app = InvoiceParserApp(root)
    root.mainloop()
