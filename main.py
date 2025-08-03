# main imports
import os
import json
import csv
import uuid
import random
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

import PyPDF2
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from PIL import Image
import io
import fitz  # PyMuPDF for image extraction

load_dotenv()

# Create directories for output
os.makedirs("extracted_images", exist_ok=True)
os.makedirs("output", exist_ok=True)

def detect_language(text: str) -> str:
    """
    Detect if text contains Arabic characters
    """
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    if arabic_pattern.search(text):
        return "arabic"
    return "english"

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extract images from PDF and save them to output directory
    Returns list of saved image paths
    """
    image_paths = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Generate random ID for image
                image_id = str(uuid.uuid4())[:8]
                image_filename = f"{Path(pdf_path).stem}_page_{page_num + 1}_img_{img_index + 1}_{image_id}.png"
                image_path = os.path.join(output_dir, image_filename)
                
                # Save image
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                image_paths.append(image_path)
        
        doc.close()
    except Exception as e:
        print(f"Error extracting images from {pdf_path}: {e}")
    
    return image_paths

def load_file(path: str) -> str:
    """
    Loading the file for operation
    """
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""

def generate_random_csv_structure(language: str = "english") -> Dict[str, str]:
    """
    Generate a random CSV structure with various field types
    """
    if language == "arabic":
        possible_fields = {
            "اسم_الشركة": "اسم الشركة كما هو مذكور في التقرير",
            "نوع_المستند": "نوع المستند (تقرير سنوي، 10-K، إلخ)",
            "تاريخ_التقديم": "تاريخ تقديم المستند",
            "السنة_المالية": "نهاية السنة المالية",
            "إجمالي_الإيرادات": "إجمالي الإيرادات بالدولار الأمريكي",
            "صافي_الدخل": "صافي الدخل بالدولار الأمريكي",
            "إجمالي_الأصول": "إجمالي الأصول بالدولار الأمريكي",
            "عدد_الموظفين": "عدد الموظفين",
            "اسم_المدقق": "اسم المدقق الخارجي",
            "اسم_الرئيس_التنفيذي": "اسم الرئيس التنفيذي",
            "قطاع_الصناعة": "قطاع الصناعة",
            "ملخص_الأعمال": "ملخص وصف الأعمال",
            "عدد_المخاطر": "عدد عوامل المخاطر المحددة",
            "عدد_الصفحات": "إجمالي صفحات المستند",
            "عدد_الصور": "عدد الصور المستخرجة",
            "وقت_المعالجة": "وقت معالجة المستند",
            "درجة_الثقة": "درجة ثقة الذكاء الاصطناعي في الاستخراج",
            "حجم_المستند_ميجابايت": "حجم ملف المستند",
            "حالة_الاستخراج": "حالة عملية الاستخراج",
            "المقاييس_الرئيسية": "ملخص المقاييس المالية الرئيسية"
        }
    else:
        possible_fields = {
            "company_name": "Company name as reported",
            "document_type": "Type of document (10-K, Annual Report, etc.)",
            "filing_date": "Date when document was filed",
            "fiscal_year": "Fiscal year end",
            "total_revenue": "Total revenue in USD",
            "net_income": "Net income in USD",
            "total_assets": "Total assets in USD",
            "employee_count": "Number of employees",
            "auditor_name": "External auditor name",
            "ceo_name": "CEO name",
            "industry_sector": "Industry sector",
            "business_summary": "Business description summary",
            "risk_count": "Number of risk factors identified",
            "page_count": "Total pages in document",
            "image_count": "Number of images extracted",
            "processing_timestamp": "When document was processed",
            "confidence_score": "AI confidence in extraction",
            "document_size_mb": "Document file size",
            "extraction_status": "Status of extraction process",
            "key_metrics": "Key financial metrics summary"
        }
    
    # Randomly select 8-12 fields
    num_fields = random.randint(8, 12)
    selected_fields = random.sample(list(possible_fields.items()), num_fields)
    
    return dict(selected_fields)

def analyze_pdf_with_ai(pdf_text: str, pdf_path: str, client: genai.Client, language: str = "english") -> Dict[str, Any]:
    """
    Analyze PDF content using AI and return structured data
    """
    # Generate random structure for this document
    csv_structure = generate_random_csv_structure(language)
    
    # Create a dynamic Pydantic model based on the structure
    field_definitions = {}
    for field_name, description in csv_structure.items():
        if "date" in field_name.lower() or "تاريخ" in field_name:
            field_definitions[field_name] = (Optional[str], Field(None, description=description))
        elif any(word in field_name.lower() for word in ["revenue", "income", "assets", "count", "score", "size", "إيرادات", "دخل", "أصول", "عدد", "درجة", "حجم"]):
            field_definitions[field_name] = (Optional[float], Field(None, description=description))
        else:
            field_definitions[field_name] = (Optional[str], Field(None, description=description))
    
    # Create dynamic model
    DynamicModel = type('DynamicModel', (BaseModel,), field_definitions)
    
    # Create schema definition
    schema_definition = json.dumps(DynamicModel.model_json_schema(), indent=2, ensure_ascii=False)
    
    # Create language-specific prompt
    if language == "arabic":
        prompt = f"""حلل المستند التالي واستخرج المعلومات وفقاً لهذا المخطط:

محتوى المستند:
{pdf_text[:5000]}...  # مختصر للحد من الرموز

استخرج وقم ببناء البيانات وفقاً لهذا المخطط:
{schema_definition}

أرجع فقط بيانات JSON المطابقة للمخطط تماماً."""
    else:
        prompt = f"""Analyze the following document and extract information according to this schema:

Document content:
{pdf_text[:5000]}...  # Truncated for token limits

Extract and structure the data according to this schema:
{schema_definition}

Return only the JSON data matching the schema exactly."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': DynamicModel
            }
        )
        
        # Parse response
        result = DynamicModel.model_validate_json(response.text or "{}")
        return result.model_dump()
    
    except Exception as e:
        print(f"Error analyzing {pdf_path}: {e}")
        # Return empty dict with structure
        return {field: None for field in csv_structure.keys()}

def convert_to_binary_data(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Convert data to binary format (0/1) for categorical fields
    """
    binary_data = {}
    
    for key, value in data.items():
        if isinstance(value, (int, float)) and value is not None:
            # For numeric values, use 1 if > 0, 0 otherwise
            binary_data[key] = 1 if value > 0 else 0
        elif isinstance(value, str) and value:
            # For string values, use 1 if not empty, 0 otherwise
            binary_data[key] = 1 if value.strip() else 0
        else:
            # For None or empty values, use 0
            binary_data[key] = 0
    
    return binary_data

def process_pdfs_in_directory(directory: str = ".") -> List[Dict[str, Any]]:
    """
    Process all PDF files in directory and return structured data
    """
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    results = []
    
    # Initialize Gemini client
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        print(f"Processing: {pdf_file}")
        
        # Extract images
        image_paths = extract_images_from_pdf(pdf_path, "extracted_images")
        print(f"  Extracted {len(image_paths)} images")
        
        # Extract text
        pdf_text = load_file(pdf_path)
        
        # Detect language
        language = detect_language(pdf_text)
        print(f"  Detected language: {language}")
        
        # Analyze with AI
        analysis_result = analyze_pdf_with_ai(pdf_text, pdf_path, client, language)
        
        # Add metadata
        analysis_result.update({
            "pdf_filename": pdf_file,
            "detected_language": language,
            "image_count": len(image_paths),
            "image_paths": ";".join(image_paths),
            "processing_timestamp": datetime.now().isoformat(),
            "document_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2)
        })
        
        results.append(analysis_result)
        print(f"  Completed analysis of {pdf_file}")
    
    return results

def save_to_csv_files(results: List[Dict[str, Any]]):
    """
    Save results to three different CSV files: Arabic, English, and Binary
    """
    if not results:
        print("No results to save")
        return
    
    # Separate results by language
    arabic_results = []
    english_results = []
    
    for result in results:
        if result.get("detected_language") == "arabic":
            arabic_results.append(result)
        else:
            english_results.append(result)
    
    # Save Arabic CSV
    if arabic_results:
        save_language_csv(arabic_results, "output/arabic_data.csv", "arabic")
    
    # Save English CSV
    if english_results:
        save_language_csv(english_results, "output/english_data.csv", "english")
    
    # Save Binary CSV (combine all results)
    save_binary_csv(results, "output/binary_data.csv")

def save_language_csv(results: List[Dict[str, Any]], output_file: str, language: str):
    """
    Save results to language-specific CSV file
    """
    if not results:
        return
    
    # Get all unique field names
    all_fields = set()
    for result in results:
        all_fields.update(result.keys())
    
    # Sort fields for consistent ordering
    field_names = sorted(list(all_fields))
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for result in results:
            # Ensure all fields are present
            row = {field: result.get(field, "") for field in field_names}
            writer.writerow(row)
    
    print(f"{language.capitalize()} data saved to {output_file}")

def save_binary_csv(results: List[Dict[str, Any]], output_file: str):
    """
    Save results to binary CSV file (0/1 values)
    """
    if not results:
        return
    
    # Get all unique field names
    all_fields = set()
    for result in results:
        all_fields.update(result.keys())
    
    # Sort fields for consistent ordering
    field_names = sorted(list(all_fields))
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for result in results:
            # Convert to binary format
            binary_row = convert_to_binary_data(result)
            # Ensure all fields are present
            row = {field: binary_row.get(field, 0) for field in field_names}
            writer.writerow(row)
    
    print(f"Binary data saved to {output_file}")

def main():
    """
    Main function to process PDFs and generate output
    """
    print("Starting PDF processing...")
    
    # Process all PDFs in current directory
    results = process_pdfs_in_directory()
    
    if results:
        # Save to multiple CSV files
        save_to_csv_files(results)
        
        # Print summary
        print(f"\nProcessing complete!")
        print(f"Processed {len(results)} PDF files")
        print(f"Extracted images saved to: extracted_images/")
        print(f"CSV files saved to: output/")
        print(f"  - arabic_data.csv (Arabic documents)")
        print(f"  - english_data.csv (English documents)")
        print(f"  - binary_data.csv (Binary format 0/1)")
        
        # Show language distribution
        arabic_count = sum(1 for r in results if r.get("detected_language") == "arabic")
        english_count = len(results) - arabic_count
        print(f"\nLanguage distribution:")
        print(f"  Arabic documents: {arabic_count}")
        print(f"  English documents: {english_count}")
        
        # Show sample of results
        if results:
            print(f"\nSample data from first document:")
            for key, value in list(results[0].items())[:5]:
                print(f"  {key}: {value}")
    else:
        print("No PDF files found to process")

if __name__ == "__main__":
    main()
