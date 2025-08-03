# Multi-Language PDF Document Processor
A comprehensive tool to extract information, images, and generate structured data from multiple PDF documents in Arabic and English using Google's Gemini AI model.

## Features
- **Multi-PDF Processing**: Process multiple PDF files in a directory
- **Multi-Language Support**: Automatically detect and handle Arabic and English content
- **Image Extraction**: Extract images from PDFs with random ID generation
- **Dynamic CSV Structure**: Generate random CSV schemas for each document
- **Three Output Formats**: Generate Arabic, English, and Binary (0/1) CSV files
- **AI-Powered Analysis**: Use Gemini AI to extract structured information
- **Flexible Output**: Generate CSV files with dynamic field structures
- **Image Management**: Organize extracted images in dedicated directories

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yossefsabry/reports_summarize.git
cd reports_summarize
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash  
cp .env.example .env
GEMINI_API_KEY=your_api_key_here # in your .env
```

## Usage

### Basic Usage
```bash
uv run main.py
```

### Test the System
```bash
uv run test_processing.py
```

## File Structure
```bash
reports_summarize/
├── main.py                                     # Main processing script
├── test_processing.py                          # Test script
├── pyproject.toml                              # Project configuration
├── README.md                                   # This file
├── uv.lock                                     # UV lock file
├── extracted_images/                           # Extracted images directory
│   ├── document1_page_1_img_1_abc12345.png
│   └── document2_page_2_img_1_def67890.png
├── output/                                     # Output directory
│   ├── arabic_data.csv                        # Arabic documents data
│   ├── english_data.csv                       # English documents data
│   └── binary_data.csv                        # Binary format (0/1) data
└── *.pdf                                       # Input PDF files
```

## How It Works

### 1. Language Detection
- Automatically detects Arabic vs English content using Unicode patterns
- Arabic detection covers: Arabic, Arabic Supplement, Arabic Extended-A, Arabic Presentation Forms-A, Arabic Presentation Forms-B
- Processes documents with appropriate language-specific schemas

### 2. PDF Processing
- Scans current directory for PDF files
- Extracts text content using PyPDF2
- Extracts images using PyMuPDF (fitz)

### 3. Image Extraction
- Generates random 8-character IDs for each image
- Saves images as PNG files with descriptive names
- Organizes images in `extracted_images/` directory

### 4. AI Analysis
- Creates dynamic Pydantic models with random field structures
- Uses language-specific prompts for Arabic and English
- Sends PDF content to Gemini AI for analysis
- Extracts structured data based on generated schema

### 5. Multi-Format CSV Generation
- **Arabic CSV**: Contains only Arabic documents with Arabic field names
- **English CSV**: Contains only English documents with English field names
- **Binary CSV**: Contains all documents converted to 0/1 format

## Dynamic CSV Structure

### English Fields
The system generates random CSV structures for English documents, including fields like:
- Company information (name, type, sector)
- Financial data (revenue, income, assets)
- Document metadata (filing date, page count, image count)
- Processing information (timestamp, confidence score)
- Business summaries and risk factors

### Arabic Fields
For Arabic documents, the system uses Arabic field names:
- `اسم_الشركة` (Company Name)
- `نوع_المستند` (Document Type)
- `تاريخ_التقديم` (Filing Date)
- `إجمالي_الإيرادات` (Total Revenue)
- `صافي_الدخل` (Net Income)
- `عدد_الموظفين` (Employee Count)
- And many more...

### Binary Format
The binary CSV converts all data to 0/1 values:
- Numeric values > 0 become 1, otherwise 0
- Non-empty strings become 1, empty strings become 0
- None/null values become 0

## Dependencies
```txt
Python 3.10+
Google Generative AI (google-genai)
Pydantic (v2+)
PyPDF2
PyMuPDF (fitz)
Pillow (PIL)
python-dotenv
```

## Output Files

### CSV Structure
The generated CSV files include:
- Dynamic fields based on AI analysis
- Image count and paths
- Document metadata
- Processing timestamps
- Language detection results

### Image Files
- Named with pattern: `{document_name}_page_{page}_img_{index}_{random_id}.png`
- Stored in `extracted_images/` directory
- Random IDs ensure unique filenames

## Token Counting Utility
> The counter.py script helps estimate token usage:
```bash
uv run counter.py
```

## Example Output

### Arabic CSV Sample
```csv
اسم_الشركة,نوع_المستند,تاريخ_التقديم,إجمالي_الإيرادات,صافي_الدخل,عدد_الصور,وقت_المعالجة
"شركة الاختبار","تقرير سنوي","2024-01-15",1000000.0,100000.0,3,"2024-01-20T10:30:00"
```

### English CSV Sample
```csv
company_name,document_type,filing_date,total_revenue,net_income,image_count,processing_timestamp
"Test Corp","Annual Report","2024-01-15",1000000.0,100000.0,3,"2024-01-20T10:30:00"
"Sample Inc","10-K","2024-02-01",5000000.0,500000.0,5,"2024-01-20T10:35:00"
```

### Binary CSV Sample
```csv
company_name,document_type,filing_date,total_revenue,net_income,image_count,processing_timestamp
1,1,1,1,1,1,1
1,1,1,1,1,1,1
```

### Directory Structure After Processing
```
extracted_images/
├── test_document_page_1_img_1_a1b2c3d4.png
├── arabic_document_page_2_img_1_e5f6g7h8.png
└── ...

output/
├── arabic_data.csv
├── english_data.csv
└── binary_data.csv
```

## Language Detection

The system automatically detects the language of each PDF using Unicode character ranges:
- **Arabic**: Detects Arabic script characters (U+0600-U+06FF, U+0750-U+077F, etc.)
- **English**: Default for non-Arabic content

This ensures that:
- Arabic documents are processed with Arabic field names and prompts
- English documents are processed with English field names and prompts
- The AI model receives language-appropriate instructions


