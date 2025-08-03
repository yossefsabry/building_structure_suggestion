#!/usr/bin/env python3
"""
Test script to demonstrate the PDF processing functionality
"""

import os
import tempfile
from pathlib import Path

def create_test_pdf():
    """
    Create a simple test PDF for demonstration
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        test_pdf_path = "test_document.pdf"
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        
        # Add some text
        c.drawString(100, 750, "Test Company Annual Report 2024")
        c.drawString(100, 720, "Company Name: Test Corp")
        c.drawString(100, 690, "Total Revenue: $1,000,000")
        c.drawString(100, 660, "Net Income: $100,000")
        c.drawString(100, 630, "Employees: 50")
        
        c.save()
        print(f"Created test PDF: {test_pdf_path}")
        return test_pdf_path
    except ImportError:
        print("reportlab not available, skipping test PDF creation")
        return None

def create_arabic_test_pdf():
    """
    Create a test PDF with Arabic text for demonstration
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Try to register Arabic font (if available)
        try:
            pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/arabic/amiri-regular.ttf'))
            arabic_font = 'Arabic'
        except:
            arabic_font = 'Helvetica'  # Fallback
        
        test_pdf_path = "test_arabic_document.pdf"
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        
        # Add Arabic text (right-to-left)
        c.setFont(arabic_font, 12)
        c.drawString(400, 750, "تقرير الشركة السنوي 2024")
        c.drawString(400, 720, "اسم الشركة: شركة الاختبار")
        c.drawString(400, 690, "إجمالي الإيرادات: 1,000,000 دولار")
        c.drawString(400, 660, "صافي الدخل: 100,000 دولار")
        c.drawString(400, 630, "عدد الموظفين: 50")
        
        c.save()
        print(f"Created Arabic test PDF: {test_pdf_path}")
        return test_pdf_path
    except ImportError:
        print("reportlab not available, skipping Arabic test PDF creation")
        return None

def main():
    """
    Test the PDF processing functionality
    """
    print("Testing Multi-Language PDF Processing System")
    print("=" * 50)
    
    # Check if we have any PDFs to process
    pdf_files = [f for f in os.listdir(".") if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory")
        print("Creating test PDFs...")
        
        # Create test PDFs
        test_pdf = create_test_pdf()
        arabic_pdf = create_arabic_test_pdf()
        
        if test_pdf or arabic_pdf:
            pdf_files = [f for f in [test_pdf, arabic_pdf] if f]
        else:
            print("Please add some PDF files to the current directory")
            return
    
    print(f"Found {len(pdf_files)} PDF file(s): {pdf_files}")
    
    # Import and run the main processing
    try:
        from main import process_pdfs_in_directory, save_to_csv_files
        
        print("\nStarting processing...")
        results = process_pdfs_in_directory(".")
        
        if results:
            save_to_csv_files(results)
            print(f"\nSuccessfully processed {len(results)} documents!")
            
            # Show directory structure
            print("\nGenerated files:")
            if os.path.exists("extracted_images"):
                image_files = os.listdir("extracted_images")
                print(f"  extracted_images/ ({len(image_files)} images)")
                for img in image_files[:3]:  # Show first 3
                    print(f"    - {img}")
                if len(image_files) > 3:
                    print(f"    ... and {len(image_files) - 3} more")
            
            # Show CSV files
            csv_files = []
            if os.path.exists("output/arabic_data.csv"):
                csv_files.append("  output/arabic_data.csv")
            if os.path.exists("output/english_data.csv"):
                csv_files.append("  output/english_data.csv")
            if os.path.exists("output/binary_data.csv"):
                csv_files.append("  output/binary_data.csv")
            
            if csv_files:
                print("  CSV files:")
                for csv_file in csv_files:
                    print(csv_file)
            
            # Show language distribution
            arabic_count = sum(1 for r in results if r.get("detected_language") == "arabic")
            english_count = len(results) - arabic_count
            print(f"\nLanguage distribution:")
            print(f"  Arabic documents: {arabic_count}")
            print(f"  English documents: {english_count}")
                
        else:
            print("No results generated")
            
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 