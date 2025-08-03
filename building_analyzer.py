#!/usr/bin/env python3
"""
Building Analysis and Suggestion System
Extracts building information from PDFs and generates AI-powered suggestions for improvements
"""

import os
import json
import csv
import uuid
import random
import re
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import shutil

import PyPDF2
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from PIL import Image
import io
import fitz  # PyMuPDF for image extraction

load_dotenv()

# Create directories for output
os.makedirs("building_images", exist_ok=True)
os.makedirs("building_data", exist_ok=True)
os.makedirs("ai_suggestions", exist_ok=True)

class BuildingInfo(BaseModel):
    """Building information model"""
    building_id: str = Field(..., description="Unique building identifier")
    city_name: str = Field(..., description="City name")
    building_category: str = Field(..., description="Building category (needs reinforcement, collapsing, etc.)")
    building_type: str = Field(..., description="Building type (residential, government, commercial, etc.)")
    building_name: str = Field(..., description="Building name or address")
    neighborhood: Optional[str] = Field(None, description="Neighborhood or area")
    construction_year: Optional[int] = Field(None, description="Year of construction")
    building_age: Optional[int] = Field(None, description="Building age in years")
    floors_count: Optional[int] = Field(None, description="Number of floors")
    total_area: Optional[float] = Field(None, description="Total building area in square meters")
    structural_condition: Optional[str] = Field(None, description="Current structural condition")
    maintenance_status: Optional[str] = Field(None, description="Maintenance status")
    safety_issues: Optional[List[str]] = Field(None, description="List of safety issues identified")
    required_repairs: Optional[List[str]] = Field(None, description="Required repairs and maintenance")
    estimated_cost: Optional[float] = Field(None, description="Estimated repair cost in USD")
    priority_level: Optional[str] = Field(None, description="Priority level (high, medium, low)")
    last_inspection_date: Optional[str] = Field(None, description="Last inspection date")
    inspector_name: Optional[str] = Field(None, description="Name of inspector")
    report_date: Optional[str] = Field(None, description="Report date")
    image_paths: Optional[List[str]] = Field(None, description="Paths to building images")
    pdf_filename: Optional[str] = Field(None, description="Source PDF filename")
    processing_timestamp: Optional[str] = Field(None, description="Processing timestamp")

class BuildingSuggestion(BaseModel):
    """AI-generated building improvement suggestions"""
    building_id: str = Field(..., description="Building identifier")
    suggestion_id: str = Field(..., description="Unique suggestion identifier")
    suggestion_type: str = Field(..., description="Type of suggestion (structural, safety, maintenance, enhancement)")
    title: str = Field(..., description="Suggestion title")
    description: str = Field(..., description="Detailed description of the suggestion")
    priority: str = Field(..., description="Priority level (critical, high, medium, low)")
    estimated_cost: Optional[float] = Field(None, description="Estimated implementation cost")
    timeline: Optional[str] = Field(None, description="Recommended timeline for implementation")
    benefits: Optional[List[str]] = Field(None, description="Expected benefits")
    risks: Optional[List[str]] = Field(None, description="Potential risks")
    requirements: Optional[List[str]] = Field(None, description="Requirements for implementation")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score (0-1)")
    generated_timestamp: Optional[str] = Field(None, description="When suggestion was generated")

def extract_images_from_pdf(pdf_path: str, building_id: str) -> List[str]:
    """
    Extract images from PDF and save them to building-specific directory
    Returns list of saved image paths
    """
    image_paths = []
    building_image_dir = os.path.join("building_images", building_id)
    os.makedirs(building_image_dir, exist_ok=True)
    
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
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}_{image_id}.png"
                image_path = os.path.join(building_image_dir, image_filename)
                
                # Save image
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                image_paths.append(image_path)
        
        doc.close()
    except Exception as e:
        print(f"Error extracting images from {pdf_path}: {e}")
    
    return image_paths

def load_pdf_text(path: str) -> str:
    """
    Extract text from PDF file
    """
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""

def extract_building_info_from_text(pdf_text: str, pdf_path: str, building_id: str, 
                                  city_name: str, category: str, building_name: str) -> Dict[str, Any]:
    """
    Extract building information from PDF text using AI
    """
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Create schema for building information
    schema_definition = json.dumps(BuildingInfo.model_json_schema(), indent=2, ensure_ascii=False)
    
    prompt = f"""تحليل تقرير فني لمبنى واستخراج المعلومات المهمة:

محتوى التقرير:
{pdf_text[:8000]}...

استخرج المعلومات التالية من التقرير:
- سنة البناء
- عدد الطوابق
- المساحة الإجمالية
- الحالة الإنشائية الحالية
- حالة الصيانة
- المشاكل الأمنية المحددة
- الإصلاحات المطلوبة
- التكلفة التقديرية
- مستوى الأولوية
- تاريخ آخر فحص
- اسم المفتش
- تاريخ التقرير

أرجع البيانات في هذا التنسيق:
{schema_definition}

ملاحظات:
- building_id: {building_id}
- city_name: {city_name}
- building_category: {category}
- building_name: {building_name}
- pdf_filename: {os.path.basename(pdf_path)}
- processing_timestamp: {datetime.now().isoformat()}

أرجع فقط JSON صحيح يطابق المخطط."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': BuildingInfo
            }
        )
        
        # Parse response
        result = BuildingInfo.model_validate_json(response.text or "{}")
        return result.model_dump()
    
    except Exception as e:
        print(f"Error analyzing building {building_id}: {e}")
        # Return basic structure
        return {
            "building_id": building_id,
            "city_name": city_name,
            "building_category": category,
            "building_name": building_name,
            "pdf_filename": os.path.basename(pdf_path),
            "processing_timestamp": datetime.now().isoformat(),
            "structural_condition": "غير محدد",
            "maintenance_status": "غير محدد",
            "safety_issues": [],
            "required_repairs": [],
            "priority_level": "متوسط"
        }

def generate_building_suggestions(building_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate AI-powered suggestions for building improvements
    """
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Create schema for suggestions
    schema_definition = json.dumps(BuildingSuggestion.model_json_schema(), indent=2, ensure_ascii=False)
    
    # Safely handle lists
    safety_issues = building_info.get('safety_issues', [])
    if not isinstance(safety_issues, list):
        safety_issues = []
    
    required_repairs = building_info.get('required_repairs', [])
    if not isinstance(required_repairs, list):
        required_repairs = []
    
    building_summary = f"""
معلومات المبنى:
- اسم المبنى: {building_info.get('building_name', 'غير محدد')}
- المدينة: {building_info.get('city_name', 'غير محدد')}
- الفئة: {building_info.get('building_category', 'غير محدد')}
- الحالة الإنشائية: {building_info.get('structural_condition', 'غير محدد')}
- حالة الصيانة: {building_info.get('maintenance_status', 'غير محدد')}
- المشاكل الأمنية: {', '.join(safety_issues)}
- الإصلاحات المطلوبة: {', '.join(required_repairs)}
- مستوى الأولوية: {building_info.get('priority_level', 'متوسط')}
"""
    
    prompt = f"""بناءً على معلومات المبنى التالية، قم بتوليد اقتراحات ذكية لتحسين المبنى:

{building_summary}

قم بتوليد 3-5 اقتراحات مختلفة تشمل:
1. اقتراحات إنشائية وأمنية
2. اقتراحات صيانة وتحسين
3. اقتراحات تطوير وتحديث
4. اقتراحات كفاءة الطاقة
5. اقتراحات تحسين المظهر العام

لكل اقتراح حدد:
- نوع الاقتراح
- العنوان والوصف
- مستوى الأولوية
- التكلفة التقديرية
- الجدول الزمني
- الفوائد المتوقعة
- المخاطر المحتملة
- المتطلبات

أرجع الاقتراحات في هذا التنسيق:
{schema_definition}

ملاحظات:
- building_id: {building_info.get('building_id', 'unknown')}
- suggestion_id: استخدم uuid عشوائي لكل اقتراح
- generated_timestamp: {datetime.now().isoformat()}

أرجع قائمة JSON تحتوي على 3-5 اقتراحات."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        # Parse response
        suggestions_data = json.loads(response.text or "[]")
        if isinstance(suggestions_data, dict):
            suggestions_data = [suggestions_data]
        
        suggestions = []
        for suggestion_data in suggestions_data:
            try:
                suggestion = BuildingSuggestion.model_validate(suggestion_data)
                suggestions.append(suggestion.model_dump())
            except Exception as e:
                print(f"Error validating suggestion: {e}")
                continue
        
        return suggestions
    
    except Exception as e:
        print(f"Error generating suggestions for building {building_info.get('building_id', 'unknown')}: {e}")
        return []

def scan_data_directory(data_dir: str = "data") -> List[Tuple[str, str, str, str, str]]:
    """
    Scan data directory and return list of (city, category, building_type, building_name, pdf_path)
    """
    building_files = []
    
    for city_dir in os.listdir(data_dir):
        city_path = os.path.join(data_dir, city_dir)
        if not os.path.isdir(city_path):
            continue
            
        for category_dir in os.listdir(city_path):
            category_path = os.path.join(city_path, category_dir)
            if not os.path.isdir(category_path):
                continue
                
            for building_type_dir in os.listdir(category_path):
                building_type_path = os.path.join(category_path, building_type_dir)
                if not os.path.isdir(building_type_path):
                    continue
                    
                for building_dir in os.listdir(building_type_path):
                    building_path = os.path.join(building_type_path, building_dir)
                    if not os.path.isdir(building_path):
                        continue
                        
                    # Look for reports directory
                    reports_path = os.path.join(building_path, "تقارير")
                    if os.path.exists(reports_path):
                        for file in os.listdir(reports_path):
                            if file.lower().endswith('.pdf'):
                                pdf_path = os.path.join(reports_path, file)
                                building_files.append((
                                    city_dir,
                                    category_dir,
                                    building_type_dir,
                                    building_dir,
                                    pdf_path
                                ))
    
    return building_files

def process_buildings():
    """
    Main function to process all buildings in data directory
    """
    print("بدء تحليل المباني...")
    
    # Scan for building files
    building_files = scan_data_directory()
    print(f"تم العثور على {len(building_files)} مبنى للتحليل")
    
    all_buildings = []
    all_suggestions = []
    
    for i, (city, category, building_type, building_name, pdf_path) in enumerate(building_files, 1):
        print(f"\nمعالجة المبنى {i}/{len(building_files)}: {building_name}")
        
        # Generate unique building ID
        building_id = str(uuid.uuid4())[:12]
        
        # Extract images
        image_paths = extract_images_from_pdf(pdf_path, building_id)
        print(f"  تم استخراج {len(image_paths)} صورة")
        
        # Extract text
        pdf_text = load_pdf_text(pdf_path)
        
        # Extract building information
        building_info = extract_building_info_from_text(
            pdf_text, pdf_path, building_id, city, category, building_name
        )
        building_info['image_paths'] = image_paths
        building_info['building_type'] = building_type
        
        all_buildings.append(building_info)
        print(f"  تم استخراج معلومات المبنى")
        
        # Generate AI suggestions
        suggestions = generate_building_suggestions(building_info)
        all_suggestions.extend(suggestions)
        print(f"  تم توليد {len(suggestions)} اقتراح")
    
    # Save results
    save_building_data(all_buildings)
    save_suggestions_data(all_suggestions)
    
    print(f"\nاكتمل التحليل!")
    print(f"تم معالجة {len(all_buildings)} مبنى")
    print(f"تم توليد {len(all_suggestions)} اقتراح")
    print(f"الصور محفوظة في: building_images/")
    print(f"البيانات محفوظة في: building_data/")
    print(f"الاقتراحات محفوظة في: ai_suggestions/")

def save_building_data(buildings: List[Dict[str, Any]]):
    """
    Save building data to CSV files
    """
    if not buildings:
        return
    
    # Main building data
    building_file = "building_data/buildings.csv"
    os.makedirs(os.path.dirname(building_file), exist_ok=True)
    
    # Get all unique field names
    all_fields = set()
    for building in buildings:
        all_fields.update(building.keys())
    
    field_names = sorted(list(all_fields))
    
    with open(building_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for building in buildings:
            # Convert lists to strings
            row = {}
            for field in field_names:
                value = building.get(field, "")
                if isinstance(value, list):
                    row[field] = "; ".join(str(v) for v in value)
                else:
                    row[field] = value
            writer.writerow(row)
    
    print(f"تم حفظ بيانات المباني في: {building_file}")
    
    # Save JSON for detailed analysis
    json_file = "building_data/buildings_detailed.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(buildings, f, ensure_ascii=False, indent=2)
    
    print(f"تم حفظ البيانات التفصيلية في: {json_file}")

def save_suggestions_data(suggestions: List[Dict[str, Any]]):
    """
    Save AI suggestions to CSV files
    """
    if not suggestions:
        return
    
    # Main suggestions data
    suggestions_file = "ai_suggestions/suggestions.csv"
    os.makedirs(os.path.dirname(suggestions_file), exist_ok=True)
    
    # Get all unique field names
    all_fields = set()
    for suggestion in suggestions:
        all_fields.update(suggestion.keys())
    
    field_names = sorted(list(all_fields))
    
    with open(suggestions_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        
        for suggestion in suggestions:
            # Convert lists to strings
            row = {}
            for field in field_names:
                value = suggestion.get(field, "")
                if isinstance(value, list):
                    row[field] = "; ".join(str(v) for v in value)
                else:
                    row[field] = value
            writer.writerow(row)
    
    print(f"تم حفظ الاقتراحات في: {suggestions_file}")
    
    # Save JSON for detailed analysis
    json_file = "ai_suggestions/suggestions_detailed.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, ensure_ascii=False, indent=2)
    
    print(f"تم حفظ الاقتراحات التفصيلية في: {json_file}")

if __name__ == "__main__":
    process_buildings() 