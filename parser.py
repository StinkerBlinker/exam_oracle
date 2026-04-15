import pdfplumber
import re

def extract_exam_data(pdf_path):
    # Pattern: Digit(s) specifically inside parentheses ( ) 
    # This usually catches sub-questions: (2 Marks), (3 Marks)
    strict_pattern = re.compile(r'\(\s*(\d+)\s*Marks?\s*\)', re.IGNORECASE)
    total_found_marks = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i == 0: continue
            
            text = page.extract_text()
            if text:
                # Find all (X Marks)
                sub_marks = strict_pattern.findall(text)
                page_marks = [int(m) for m in sub_marks]
                
                page_sum = sum(page_marks)
                total_found_marks += page_sum
                
                if page_marks:
                    print(f"Page {i+1}: Sub-marks detected {page_marks}")

    print(f"\n--- Sub-mark Extraction ---")
    print(f"Total Marks Calculated: {total_found_marks}/100")
    return total_found_marks

extract_exam_data("CS311 Final Exam Paper S1 2025 9 May 2025.pdf")