import re
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from PyPDF2 import PdfReader

results_pattern = r"^(?!0\d+$)0?$|^[1-9]\d*(\.\d+)?$|^0\.\d+$"

def extract_collected_date(text):
    for line in text:
        if line.startswith("COLLECTED:"):
            date_pattern = r"^COLLECTED:\s*(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(\d{4})"
            match = re.match(date_pattern, line)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        elif "Collection Date/Time:" in line:
            date_pattern = r"Collection Date/Time:\s*(\d{2}/\d{2}/\d{4})"
            match = re.search(date_pattern, line)
            if match:
                return match.group(1)
    return None

def extract_lines_from_pdf(pdf_path):
    all_lines = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:  
                    lines = text.splitlines()
                    all_lines.extend(lines)
    except FileNotFoundError:
        return f"Error: File not found at '{pdf_path}'"

    return all_lines

def get_index_of_first_digit(tokens):
  for i, s in enumerate(tokens):
    if s and s[0].isdigit():
      return i
  return None

def save_plots_to_pdf(results, output_pdf="results_plots.pdf"):
    with PdfPages(output_pdf) as pdf:
        for key, data_points in results.items():
            x_dates = []
            y_values = []
            valid_data_points = []

            for value, date_str in data_points:
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
                    numeric_value = float(value)
                    valid_data_points.append((date_obj, numeric_value))
                except ValueError:
                    print(f"Warning: Skipping invalid data point for {key}: ({value}, {date_str})")
                except TypeError:
                    print(f"Warning: Skipping invalid data point for {key}: ({value}, {date_str})")

            if valid_data_points:
                valid_data_points.sort(key=lambda item: item[0])
                x_dates = [dp[0] for dp in valid_data_points]
                y_values = [dp[1] for dp in valid_data_points]

                fig = plt.figure(figsize=(10, 5))
                ax = fig.add_subplot(1, 1, 1)
                ax.plot(x_dates, y_values, marker='o', linestyle='-')
                ax.set_title(key)
                ax.set_xlabel("Date")
                ax.set_ylabel("Value")
                ax.grid(True)
                ax.tick_params(axis='x', rotation=45, which='major', labelsize=8)
                plt.tight_layout()

                pdf.savefig(fig)
                plt.close(fig)
            else:
                print(f"No valid numerical data to plot for {key}, skipping PDF page.")
        print(f"Plots saved to '{output_pdf}'")

if __name__ == "__main__":
    pdf_files = [] 

    try:
        for filename in os.listdir("docs"):
            if filename.endswith(".pdf"):
                pdf_files.append(os.path.join("docs", filename))
    except FileNotFoundError:
        print(f"Error: Directory '{"docs"}' not found.")

    results = {}
    for file in pdf_files:
        extracted_lines = extract_lines_from_pdf(file)
        if isinstance(extracted_lines, list):
            date = extract_collected_date(extracted_lines)
            if date is None: 
                print(f"Error collecting date for file {file}: This file will be skipped")
                continue
            else:
                print(f"Reading results collected on {date}")

            last_line = ""
            for line in extracted_lines:
                # work with older PDFs
                match = re.match(results_pattern, line)
                if match:
                    if last_line in ["01", "02", " of "] or last_line.startswith("MD") or last_line.startswith("Director") or last_line.startswith("90"):
                        continue

                    last_line = last_line.strip()
                    line = line.strip()

                    if last_line not in results:
                        results[last_line] = [] 

                    results[last_line].append((line, date))
                
                # work with Walk In Labs results
                if "/" in line and "Final" in line:
                    if line.startswith("Specimen"):
                        continue

                    tokens = line.split()
                    if "25-Hydroxy" in tokens: 
                        tokens.remove("25-Hydroxy")

                    index = get_index_of_first_digit(tokens)
                    k = " ".join(tokens[:index])
                    k = k.replace("Above High Normal", "")
                    k = k.replace("Below High Normal", "")
                    k = k.strip()
                    v = tokens[index]
                    v = v.strip()

                    if k not in results:
                        results[k] = [] 

                    results[k].append((v, date))

                last_line = line

        else:
            print(f"Error extracting {file}: {extracted_lines}")
    
    sorted_results = sorted(results.items())
    # for key, val in sorted_results:
    #     print(f"{key}:\t{val}")

    for k in sorted(results.keys()):
        print(k)

    save_plots_to_pdf(results) 
