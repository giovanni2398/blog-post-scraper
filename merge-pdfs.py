import pypdf
import os
from pathlib import Path

def merge_pdfs(input_dir, output_file):
    """
    Merge all PDF files in the input directory into a single PDF file.
    
    Args:
        input_dir (str): Directory containing PDF files to merge
        output_file (str): Path to save the merged PDF file
    """
    # Create PDF merger object
    merger = pypdf.PdfWriter()
    
    # Get all PDF files in the input directory
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to merge")
    
    # Add each PDF to the merger
    for pdf_file in pdf_files:
        file_path = os.path.join(input_dir, pdf_file)
        try:
            merger.append(file_path)
            print(f"Added {pdf_file} to merger")
        except Exception as e:
            print(f"Error adding {pdf_file}: {str(e)}")
    
    # Write the merged PDF to the output file
    try:
        merger.write(output_file)
        merger.close()
        print(f"Successfully merged PDFs into {output_file}")
    except Exception as e:
        print(f"Error writing merged PDF: {str(e)}")

if __name__ == "__main__":
    # Configuration
    INPUT_DIR = "output"  # Directory containing the PDF files
    OUTPUT_FILE = "merged_output.pdf"  # Name of the merged PDF file
    
    # Ensure input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory {INPUT_DIR} does not exist")
        exit(1)
    
    # Merge PDFs
    merge_pdfs(INPUT_DIR, OUTPUT_FILE)
