import pandas as pd
import glob
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Brute Force Search Algorithm
def brute_force_search(text, pattern):
    n = len(text)
    m = len(pattern)
    locations = []

    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            locations.append(i)
    
    return locations

# KMP Search Algorithm
def compute_lps(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    n = len(text)
    m = len(pattern)
    lps = compute_lps(pattern)
    locations = []
    i = 0
    j = 0

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == m:
            locations.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return locations

# Updated search_dataframe function to include case sensitivity and whole word match
def search_dataframe(df, pattern, algorithm='brute_force', case_sensitive=False, whole_word=False):
    results = []
    
    if not pattern:
        raise ValueError("Search pattern cannot be empty.")

    # Modify pattern and content based on case sensitivity
    if not case_sensitive:
        pattern = pattern.lower()

    # Choose search algorithm
    search_func = brute_force_search if algorithm == 'brute_force' else kmp_search

    # Search each file (row in the DataFrame)
    for index, row in df.iterrows():
        filename = row['Filename']
        content = row['Content']
        
        # Modify content based on case sensitivity
        if not case_sensitive:
            content = content.lower()

        # Search the pattern in the content
        start_time = time.time()
        try:
            positions = search_func(content, pattern)
        except Exception as e:
            raise RuntimeError(f"Error while searching in file {filename}: {str(e)}")

        end_time = time.time()

        # Filter results based on whole word match
        if whole_word:
            positions = [pos for pos in positions if (pos == 0 or not content[pos - 1].isalnum()) and
                         (pos + len(pattern) == len(content) or not content[pos + len(pattern)].isalnum())]

        # Record time taken and matches
        for pos in positions:
            results.append({
                'Filename': filename,
                'Row': index,
                'Column (position)': pos,
                'Time Taken (s)': round(end_time - start_time, 4)
            })

    return results

# Function to run the search when the button is clicked
def run_search():
    search_text = search_entry.get()
    algorithm = algorithm_choice.get()
    case_sensitive = case_sensitive_var.get()
    whole_word = whole_word_var.get()

    if not search_text:
        messagebox.showerror("Input Error", "Please enter the search text.")
        return

    try:
        results = search_dataframe(df, search_text, algorithm, case_sensitive, whole_word)
        if results:
            output_text.delete(1.0, tk.END)  # Clear previous results
            output_text.insert(tk.END, "Search Results:\n")
            output_text.insert(tk.END, "-"*50 + "\n")
            
            # Format and display each result
            for result in results:
                output_text.insert(tk.END, f"Filename: {result['Filename']}\n")
                output_text.insert(tk.END, f"Row: {result['Row']}\n")
                output_text.insert(tk.END, f"Position (Column): {result['Column (position)']}\n")
                output_text.insert(tk.END, f"Time Taken: {result['Time Taken (s)']} seconds\n")
                output_text.insert(tk.END, "-"*50 + "\n")  # Separator for each result
        else:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "No matches found.\n")

    except ValueError as ve:
        messagebox.showerror("Search Error", str(ve))
    except RuntimeError as re:
        messagebox.showerror("Search Error", str(re))
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

# Load the text files into DataFrame
file_pattern = "Research#*.txt"
data = {'Filename': [], 'Content': []}

try:
    files_found = glob.glob(file_pattern)
    if not files_found:
        raise FileNotFoundError(f"No files found matching pattern {file_pattern}")

    for filepath in files_found:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data['Filename'].append(filepath)
                data['Content'].append(file.read())
        except Exception as e:
            raise IOError(f"Error reading file {filepath}: {str(e)}")
    
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No valid content found in files.")

except FileNotFoundError as fnf_error:
    messagebox.showerror("File Error", str(fnf_error))
except IOError as io_error:
    messagebox.showerror("File Error", str(io_error))
except Exception as e:
    messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Text Search App")

# Create the search text input
tk.Label(root, text="Enter search text:").pack(pady=10)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

# Create the algorithm choice dropdown
tk.Label(root, text="Choose algorithm:").pack(pady=10)
algorithm_choice = ttk.Combobox(root, values=["brute_force", "kmp"])
algorithm_choice.current(0)  # Set default to 'brute_force'
algorithm_choice.pack(pady=5)

# Create a checkbox for case sensitivity
case_sensitive_var = tk.BooleanVar()
case_sensitive_checkbox = tk.Checkbutton(root, text="Case Sensitive", variable=case_sensitive_var)
case_sensitive_checkbox.pack(pady=5)

# Create a checkbox for whole word match
whole_word_var = tk.BooleanVar()
whole_word_checkbox = tk.Checkbutton(root, text="Whole Word Match", variable=whole_word_var)
whole_word_checkbox.pack(pady=5)

# Create the search button
search_button = tk.Button(root, text="Search", command=run_search)
search_button.pack(pady=10)

# Create a text widget to display the output
output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
