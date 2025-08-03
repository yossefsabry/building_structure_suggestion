#!/usr/bin/env python3
"""
Progress Monitoring Script
Check the progress of building analysis
"""

import os
import json
from datetime import datetime

def check_progress():
    """
    Check the current progress of building analysis
    """
    print("مراقبة تقدم تحليل المباني")
    print("=" * 40)
    
    # Check building images
    if os.path.exists("building_images"):
        building_dirs = [d for d in os.listdir("building_images") if os.path.isdir(os.path.join("building_images", d))]
        total_images = 0
        for building_dir in building_dirs:
            building_path = os.path.join("building_images", building_dir)
            images = [f for f in os.listdir(building_path) if f.endswith('.png')]
            total_images += len(images)
        
        print(f"عدد المباني المعالجة: {len(building_dirs)}")
        print(f"إجمالي الصور المستخرجة: {total_images}")
        
        # Show sample of processed buildings
        if building_dirs:
            print(f"\nأمثلة على المباني المعالجة:")
            for i, building_dir in enumerate(building_dirs[:5]):
                print(f"  {i+1}. {building_dir}")
            if len(building_dirs) > 5:
                print(f"  ... و {len(building_dirs) - 5} مبنى آخر")
    
    # Check building data
    if os.path.exists("building_data"):
        building_files = os.listdir("building_data")
        print(f"\nملفات البيانات:")
        for file in building_files:
            file_path = os.path.join("building_data", file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  {file}: {size} bytes")
    
    # Check AI suggestions
    if os.path.exists("ai_suggestions"):
        suggestion_files = os.listdir("ai_suggestions")
        print(f"\nملفات الاقتراحات:")
        for file in suggestion_files:
            file_path = os.path.join("ai_suggestions", file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  {file}: {size} bytes")
    
    # Check if process is still running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'building_analyzer'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n✅ عملية التحليل لا تزال تعمل...")
        else:
            print(f"\n✅ عملية التحليل اكتملت!")
    except:
        print(f"\n❓ لا يمكن التحقق من حالة العملية")

if __name__ == "__main__":
    check_progress() 