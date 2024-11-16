import logging
import os
import subprocess
import re
import pymupdf  # Import pymupdf from PyMuPDF
import argparse
from collections import defaultdict

# Parse command line arguments
parser = argparse.ArgumentParser(description="Process PDF files and extract relevant information.")
parser.add_argument('--debug', action='store_true', help="Enable debug logging")
args = parser.parse_args()

# Configure logging
logging_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')
# Add file handler to retain logs for future reference
file_handler = logging.FileHandler('asc842_pdf_parser.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)

# Step 1: Extract text from PDF using PyMuPDF

def extract_text_from_pdf(pdf_path):
    try:
        logging.info(f"Extracting text from PDF file: {pdf_path}")
        # Open the PDF file using PyMuPDF
        with pymupdf.open(pdf_path) as doc:
            text = ""
            # Iterate through all pages and extract text
            for page_num in range(len(doc)):
                logging.debug(f"Extracting text from page {page_num + 1}")
                text += doc.load_page(page_num).get_text("text")
        logging.info("Finished extracting text from PDF")
        return text
    except FileNotFoundError:
        # Handle case where the file is not found
        logging.error(f"File not found: {pdf_path}")
        return ""
    except PermissionError:
        # Handle case where the file cannot be accessed due to permission issues
        logging.error(f"Permission denied: {pdf_path}")
        return ""
    except Exception as e:
        # Handle any other exceptions that may occur
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

# Step 2: Define functions to identify key information from the PDF

def identify_lease(text):
    logging.debug("Identifying lease...")
    patterns = [r'lease agreement', r'lease contract', r'terms of lease']
    result = extract_section(text, patterns, "Lease Identification")
    return result

def determine_lease_term(text):
    logging.debug("Determining lease term...")
    patterns = [r'lease term.*?(months|years)', r'renewal option', r'lease period']
    result = extract_section(text, patterns, "Lease Term Determination")
    return result

def calculate_lease_payments(text):
    logging.debug("Calculating lease payments...")
    patterns = [r'lease payments.*?amounts', r'total lease cost', r'periodic payment']
    result = extract_section(text, patterns, "Lease Payments")
    return result

def calculate_discount_rate(text):
    logging.debug("Calculating discount rate...")
    patterns = [r'discount rate.*?is', r'interest rate.*?applied']
    result = extract_section(text, patterns, "Discount Rate Calculation")
    return result

def recognize_lease_liability_and_asset(text):
    logging.debug("Recognizing lease liability and asset...")
    patterns = [r'right-of-use asset', r'lease liability', r'liability recognized']
    result = extract_section(text, patterns, "Liability and Asset Recognition")
    return result

# Step 3: Extract sections based on patterns

def extract_section(text, patterns, step_name):
    all_matches = []
    for pattern in patterns:
        # Use regex to find all matches for the given pattern
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            logging.debug(f"Matches found with pattern '{pattern}': {[match.group() for match in matches]}")
        all_matches.extend(match.group() for match in matches)
    if all_matches:
        # Return all matched text with the step name
        return f"{step_name}: {'; '.join(all_matches)}"
    return None  # Return None if no match is found

# Step 4: Parse and summarize key information

def summarize_pdf_contents(text):
    summary = []
    # Define the steps and their descriptions
    steps = [
        (identify_lease, "Lease Identification"),
        (determine_lease_term, "Lease Term Determination"),
        (calculate_lease_payments, "Lease Payments"),
        (calculate_discount_rate, "Discount Rate Calculation"),
        (recognize_lease_liability_and_asset, "Liability and Asset Recognition")
    ]

    # Iterate through each step and generate the summary
    for step, description in steps:
        result = step(text)
        if result:
            summary.append(result)
        else:
            summary.append(f"{description}: Not Found")
    return "\n".join(summary)  # Join all steps into a single summary string

# Main function

def main():
    # Main function to start the process of extracting and summarizing information from all PDFs in the directory
    pdf_directory = "pdf_files_to_parse"
    output_directory = "output_files"
    # Check if the directory exists
    if not os.path.exists(pdf_directory):
        logging.error(f"Directory not found: {pdf_directory}")
        return
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Get a list of all PDF files in the directory
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    if not pdf_files:
        logging.error(f"No PDF files found in directory: {pdf_directory}")
        return
    # Iterate through each PDF file and process it
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        output_path = os.path.join(output_directory, f"{os.path.splitext(pdf_file)[0]}.txt")
        try:
            logging.info(f"Starting process for PDF: {pdf_path}")
            text = extract_text_from_pdf(pdf_path)  # Extract text from the provided PDF path
            if not text.strip():  # Add a check for empty or invalid text earlier in the workflow
                logging.error("No valid text extracted from PDF. Skipping.")
                continue
            # Clean and preprocess the extracted text
            text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace and special characters
            # Summarize the key information based on the extracted text
            summary = summarize_pdf_contents(text)
            # Write the summary to a text file
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(summary)
            logging.info(f"Summary written to: {output_path}")
        except FileNotFoundError:
            logging.error(f"File not found: {pdf_path}")
        except PermissionError:
            logging.error(f"Permission denied: {pdf_path}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()