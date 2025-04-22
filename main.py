import re
from PyPDF2 import PdfReader

pdf_files = ['docs/7_18_23.pdf']
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
    
    for line in all_lines:
        print(line)
    return all_lines

if __name__ == "__main__":
    results = {}
    for file in pdf_files:
        extracted_lines = extract_lines_from_pdf(file)
        if isinstance(extracted_lines, list):
            date = extract_collected_date(extracted_lines)
            if date is None: 
                print("Error collecting date for file <get filename>")
            else:
                print(f"Reading results collected on {date}")

            last_line = ""
            for line in extracted_lines:
                match = re.match(results_pattern, line)
                if match:
                    if last_line in ["01", " of "] or last_line.startswith("MD"):
                        continue

                    if last_line not in results:
                        results[last_line] = [] 

                    results[last_line].append((line, date))

                last_line = line

        else:
            print(f"Error extracting <get_filename>: {extracted_lines}")
    
    for key, val in results.items():
        print(f"{key}:\t{val}")