#!/usr/bin/env python3
"""
Convert FINAL_REPORT.md to PDF format
"""
import os
import sys
import markdown
from pathlib import Path

# Try different PDF conversion methods
try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

try:
    import markdown2
    HAS_MARKDOWN2 = True
except ImportError:
    HAS_MARKDOWN2 = False

def convert_markdown_to_pdf_markdown2(md_file, pdf_file):
    """Convert using markdown2 and weasyprint"""
    if not HAS_MARKDOWN2 or not HAS_WEASYPRINT:
        return False
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])
    
    # Add CSS styling
    html_with_style = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Arial', 'Helvetica', sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #555;
                margin-top: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 15px;
                margin-left: 0;
                color: #666;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    HTML(string=html_with_style).write_pdf(pdf_file)
    return True

def convert_markdown_to_pdf_pdfkit(md_file, pdf_file):
    """Convert using pdfkit (requires wkhtmltopdf)"""
    if not HAS_PDFKIT:
        return False
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Add CSS styling
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #3498db; color: white; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        pdfkit.from_string(html_with_style, pdf_file, options={'page-size': 'A4', 'margin-top': '0.75in', 'margin-bottom': '0.75in', 'margin-left': '0.75in', 'margin-right': '0.75in'})
        return True
    except Exception as e:
        print(f"Error with pdfkit: {e}")
        return False

def convert_markdown_to_pdf_pypandoc(md_file, pdf_file):
    """Convert using pypandoc (requires pandoc)"""
    try:
        import pypandoc
        pypandoc.convert_file(md_file, 'pdf', outputfile=pdf_file, extra_args=['--pdf-engine=xelatex', '-V', 'geometry:margin=2cm'])
        return True
    except Exception as e:
        print(f"Error with pypandoc: {e}")
        return False

def main():
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    md_file = project_root / "reports" / "FINAL_REPORT.md"
    pdf_file = project_root / "reports" / "FINAL_REPORT.pdf"
    
    if not md_file.exists():
        print(f"Error: {md_file} not found!")
        sys.exit(1)
    
    print(f"Converting {md_file} to PDF...")
    
    # Try different conversion methods
    success = False
    
    # Method 1: Try markdown2 + weasyprint
    if convert_markdown_to_pdf_markdown2(md_file, pdf_file):
        print(f"✅ Successfully created PDF using markdown2 + weasyprint: {pdf_file}")
        success = True
    # Method 2: Try pdfkit
    elif convert_markdown_to_pdf_pdfkit(md_file, pdf_file):
        print(f"✅ Successfully created PDF using pdfkit: {pdf_file}")
        success = True
    # Method 3: Try pypandoc
    elif convert_markdown_to_pdf_pypandoc(md_file, pdf_file):
        print(f"✅ Successfully created PDF using pypandoc: {pdf_file}")
        success = True
    
    if not success:
        print("\n❌ Could not convert to PDF. Please install one of:")
        print("   1. pip install markdown2 weasyprint")
        print("   2. pip install pdfkit (and install wkhtmltopdf)")
        print("   3. pip install pypandoc (and install pandoc)")
        print("\nAlternatively, use pandoc directly:")
        print(f"   pandoc {md_file} -o {pdf_file} --pdf-engine=xelatex")
        sys.exit(1)

if __name__ == "__main__":
    main()
