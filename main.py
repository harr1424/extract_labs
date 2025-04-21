import re
from PyPDF2 import PdfReader

pdf_file = 'docs/1_6_23.pdf' 
results_pattern = r"^(?!0\d+$)0?$|^[1-9]\d*(\.\d+)?$|^0\.\d+$"

def extract_collected_date(text):
    for line in text: 
        if line.startswith("COLLECTED:"):
            date_pattern = r"^COLLECTED:\s*(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(\d{4})"
            match = re.match(date_pattern, line)
            if match:
                print(f"date 1: {match.group(1)}")
                print(f"date 2: {match.group(2)}")
                print(f"date 3: {match.group(3)}")

                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
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

if __name__ == "__main__":
    results = {}
    extracted_lines = extract_lines_from_pdf(pdf_file)
    if isinstance(extracted_lines, list):
        date = extract_collected_date(extracted_lines)
        if date is None: 
            print("Error collecting date for file <get filename>")

        last_line = ""
        for line in extracted_lines:
            match = re.match(results_pattern, line)
            if match:
                results[last_line] = (line, date)

            last_line = line
            #print(line)
        for key, val in results.items():
            print(f"{key}:\t{val}")

    else:
        print(extracted_lines)