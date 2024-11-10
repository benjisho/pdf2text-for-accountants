import os
import logging
import argparse
import subprocess

# Configure logging
parser = argparse.ArgumentParser(description="Main PDF parser entry point.")
parser.add_argument('--form_type', required=True, help="Specify the form type (e.g., asc606, asc842, etc.)")
parser.add_argument('--debug', action='store_true', help="Enable debug logging")
args = parser.parse_args()

logging_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('p2ta_pdf_parser.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Map form types to parser scripts
PARSER_SCRIPTS = {
    "asc606": "asc606-pdf-parser.py",
    "asc842": "asc842-pdf-parser.py",
    "asc805": "asc805-pdf-parser.py",
    "asc718": "asc718-pdf-parser.py",
    "asc815": "asc815-pdf-parser.py",
    "ifrs15": "ifrs15-pdf-parser.py",
    "asc450": "asc450-pdf-parser.py",
    "asc320": "asc320-pdf-parser.py",
    "asc330": "asc330-pdf-parser.py",
    "asc250": "asc250-pdf-parser.py",
}

def get_parser_script(form_type):
    """Retrieve the specific parser script for the given form type."""
    return PARSER_SCRIPTS.get(form_type)

def main():
    form_type = args.form_type
    parser_script = get_parser_script(form_type)

    if not parser_script:
        logging.error(f"No parser found for form type: {form_type}")
        return

    pdf_directory = "pdf_files_to_parse"
    output_directory = "output_files"

    if not os.path.exists(pdf_directory):
        logging.error(f"Directory not found: {pdf_directory}")
        return

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    if not pdf_files:
        logging.error("No PDF files found to parse.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        output_path = os.path.join(output_directory, f"{os.path.splitext(pdf_file)[0]}.txt")
        
        logging.info(f"Processing PDF: {pdf_path} with parser {parser_script}")

    try:
        # Start the selected parser script
        cmd = ['python3', f'/app/{parser_script}']
        if args.debug:
            cmd.append('--debug')
        subprocess.run(cmd, check=True)
        logging.info(f"Successfully parsed {pdf_file}, output written to {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while parsing {pdf_file} with {parser_script}: {e}")

if __name__ == "__main__":
    main()
