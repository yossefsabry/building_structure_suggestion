#!/usr/bin/env python3
"""
Test script for Building Analysis System
"""

import os
import sys
from pathlib import Path

def main():
    """
    Test the building analysis functionality
    """
    print("اختبار نظام تحليل المباني")
    print("=" * 40)
    
    # Check if data directory exists
    if not os.path.exists("data"):
        print("❌ مجلد البيانات غير موجود!")
        print("يرجى التأكد من وجود مجلد 'data' يحتوي على تقارير المباني")
        return
    
    # Count PDF files
    pdf_count = 0
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_count += 1
    
    if pdf_count == 0:
        print("❌ لم يتم العثور على ملفات PDF في مجلد البيانات!")
        print("يرجى إضافة تقارير المباني بصيغة PDF")
        return
    
    print(f"✅ تم العثور على {pdf_count} ملف PDF")
    
    # Show directory structure
    print("\nهيكل البيانات:")
    for city_dir in os.listdir("data"):
        city_path = os.path.join("data", city_dir)
        if os.path.isdir(city_path):
            print(f"  📁 {city_dir}")
            
            for condition_dir in os.listdir(city_path):
                condition_path = os.path.join(city_path, condition_dir)
                if os.path.isdir(condition_path):
                    print(f"    📁 {condition_dir}")
                    
                    # Count buildings in this condition
                    building_count = 0
                    for root, dirs, files in os.walk(condition_path):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                building_count += 1
                    
                    if building_count > 0:
                        print(f"      📄 {building_count} تقرير")
    
    # Import and run the building analysis
    try:
        from building_analyzer import process_building_reports
        
        print(f"\n🚀 بدء تحليل المباني...")
        process_building_reports()
        
        # Show results
        print(f"\n📊 النتائج:")
        
        if os.path.exists("building_data/buildings_analysis.csv"):
            import csv
            with open("building_data/buildings_analysis.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                buildings = list(reader)
                print(f"  📋 تم تحليل {len(buildings)} مبنى")
        
        if os.path.exists("building_suggestions/building_suggestions.csv"):
            with open("building_suggestions/building_suggestions.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                suggestions = list(reader)
                print(f"  💡 تم إنشاء {len(suggestions)} اقتراح")
        
        if os.path.exists("building_images"):
            image_dirs = [d for d in os.listdir("building_images") if os.path.isdir(os.path.join("building_images", d))]
            total_images = 0
            for img_dir in image_dirs:
                img_path = os.path.join("building_images", img_dir)
                images = [f for f in os.listdir(img_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                total_images += len(images)
            print(f"  🖼️  تم استخراج {total_images} صورة")
        
        print(f"\n✅ اكتمل التحليل بنجاح!")
        print(f"📁 الملفات المحفوظة:")
        print(f"  - building_data/buildings_analysis.csv")
        print(f"  - building_suggestions/building_suggestions.csv")
        print(f"  - building_images/ (مجلد الصور)")
        
    except Exception as e:
        print(f"❌ خطأ أثناء التحليل: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 