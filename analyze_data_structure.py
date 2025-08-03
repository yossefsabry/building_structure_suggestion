#!/usr/bin/env python3
"""
Data Structure Analysis Script
Analyzes the data folder structure and PDF content to understand the building data format
"""

import os
import json
from pathlib import Path
import PyPDF2

def analyze_folder_structure(data_dir: str = "data"):
    """
    Analyze the folder structure and create a map of all buildings
    """
    print("تحليل هيكل المجلدات...")
    print("=" * 50)
    
    structure = {}
    
    for city_dir in os.listdir(data_dir):
        city_path = os.path.join(data_dir, city_dir)
        if not os.path.isdir(city_path):
            continue
            
        print(f"\nالمدينة: {city_dir}")
        structure[city_dir] = {}
        
        for category_dir in os.listdir(city_path):
            category_path = os.path.join(city_path, category_dir)
            if not os.path.isdir(category_path):
                continue
                
            print(f"  الفئة: {category_dir}")
            structure[city_dir][category_dir] = {}
            
            for building_type_dir in os.listdir(category_path):
                building_type_path = os.path.join(category_path, building_type_dir)
                if not os.path.isdir(building_type_path):
                    continue
                    
                print(f"    نوع المبنى: {building_type_dir}")
                structure[city_dir][category_dir][building_type_dir] = []
                
                for building_dir in os.listdir(building_type_path):
                    building_path = os.path.join(building_type_path, building_dir)
                    if not os.path.isdir(building_path):
                        continue
                        
                    print(f"      المبنى: {building_dir}")
                    
                    # Look for reports directory
                    reports_path = os.path.join(building_path, "تقارير")
                    if os.path.exists(reports_path):
                        for file in os.listdir(reports_path):
                            if file.lower().endswith('.pdf'):
                                pdf_path = os.path.join(reports_path, file)
                                structure[city_dir][category_dir][building_type_dir].append({
                                    "building_name": building_dir,
                                    "pdf_file": file,
                                    "pdf_path": pdf_path
                                })
                                print(f"        PDF: {file}")
    
    return structure

def analyze_pdf_content(pdf_path: str, max_pages: int = 3):
    """
    Analyze PDF content to understand the structure
    """
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            print(f"\nتحليل PDF: {os.path.basename(pdf_path)}")
            print(f"عدد الصفحات: {len(reader.pages)}")
            
            # Extract text from first few pages
            text_content = ""
            for i in range(min(max_pages, len(reader.pages))):
                page_text = reader.pages[i].extract_text() or ""
                text_content += f"\n--- الصفحة {i+1} ---\n{page_text}"
            
            return {
                "total_pages": len(reader.pages),
                "sample_text": text_content[:2000],  # First 2000 characters
                "file_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2)
            }
            
    except Exception as e:
        print(f"خطأ في قراءة PDF {pdf_path}: {e}")
        return None

def sample_pdf_analysis(structure: dict, sample_count: int = 3):
    """
    Analyze a sample of PDFs to understand content structure
    """
    print(f"\nتحليل عينة من {sample_count} ملفات PDF...")
    print("=" * 50)
    
    sample_analyses = []
    
    for city in structure:
        for category in structure[city]:
            for building_type in structure[city][category]:
                for building in structure[city][category][building_type][:sample_count]:
                    pdf_path = building["pdf_path"]
                    analysis = analyze_pdf_content(pdf_path)
                    
                    if analysis:
                        sample_analyses.append({
                            "city": city,
                            "category": category,
                            "building_type": building_type,
                            "building_name": building["building_name"],
                            "pdf_file": building["pdf_file"],
                            "analysis": analysis
                        })
    
    return sample_analyses

def generate_csv_structure_plan(analyses: list):
    """
    Generate a plan for CSV structure based on PDF content analysis
    """
    print(f"\nتخطيط هيكل CSV بناءً على تحليل المحتوى...")
    print("=" * 50)
    
    # Common fields found in building reports
    common_fields = {
        "building_id": "معرف فريد للمبنى",
        "city_name": "اسم المدينة",
        "building_category": "فئة المبنى (تحتاج تدعيم، آيل للسقوط)",
        "building_type": "نوع المبنى (مدرسة، مستشفى، فيلا، إلخ)",
        "building_name": "اسم المبنى",
        "neighborhood": "الحي أو المنطقة",
        "construction_year": "سنة البناء",
        "building_age": "عمر المبنى",
        "floors_count": "عدد الطوابق",
        "total_area": "المساحة الإجمالية",
        "structural_condition": "الحالة الإنشائية",
        "maintenance_status": "حالة الصيانة",
        "safety_issues": "مشاكل السلامة",
        "required_repairs": "الإصلاحات المطلوبة",
        "estimated_cost": "التكلفة التقديرية",
        "priority_level": "مستوى الأولوية",
        "last_inspection_date": "تاريخ آخر فحص",
        "inspector_name": "اسم المفتش",
        "report_date": "تاريخ التقرير",
        "image_paths": "مسارات الصور",
        "pdf_filename": "اسم ملف PDF",
        "processing_timestamp": "وقت المعالجة"
    }
    
    print("الحقول المقترحة للـ CSV:")
    for field, description in common_fields.items():
        print(f"  {field}: {description}")
    
    return common_fields

def main():
    """
    Main analysis function
    """
    print("تحليل هيكل البيانات والمحتوى")
    print("=" * 60)
    
    # Analyze folder structure
    structure = analyze_folder_structure()
    
    # Save structure to JSON
    with open("data_structure_analysis.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"\nتم حفظ تحليل الهيكل في: data_structure_analysis.json")
    
    # Count total buildings
    total_buildings = 0
    for city in structure:
        for category in structure[city]:
            for building_type in structure[city][category]:
                total_buildings += len(structure[city][category][building_type])
    
    print(f"\nإجمالي عدد المباني: {total_buildings}")
    
    # Analyze sample PDFs
    sample_analyses = sample_pdf_analysis(structure, sample_count=2)
    
    # Save sample analyses
    with open("pdf_content_samples.json", "w", encoding="utf-8") as f:
        json.dump(sample_analyses, f, ensure_ascii=False, indent=2)
    print(f"تم حفظ عينات المحتوى في: pdf_content_samples.json")
    
    # Generate CSV structure plan
    csv_fields = generate_csv_structure_plan(sample_analyses)
    
    # Save CSV structure plan
    with open("csv_structure_plan.json", "w", encoding="utf-8") as f:
        json.dump(csv_fields, f, ensure_ascii=False, indent=2)
    print(f"تم حفظ خطة هيكل CSV في: csv_structure_plan.json")
    
    print(f"\nاكتمل التحليل!")
    print(f"يمكنك الآن تشغيل building_analyzer.py لمعالجة جميع المباني")

if __name__ == "__main__":
    main() 