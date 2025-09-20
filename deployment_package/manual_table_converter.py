#!/usr/bin/env python3
"""
Manual Table Markdown to PDF Converter
Manually reconstructs the tables from the specific markdown format.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import re
from datetime import datetime

def create_styles():
    """Create paragraph styles."""
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Times-Roman',
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=HexColor('#2c3e50')
    )
    
    # Section style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor('#2c3e50')
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor=HexColor('#333333')
    )
    
    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=white
    )
    
    # Table cell style
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        alignment=TA_LEFT,
        textColor=black
    )
    
    return {
        'title': title_style,
        'section': section_style,
        'normal': normal_style,
        'table_header': table_header_style,
        'table_cell': table_cell_style
    }

def clean_text(text):
    """Clean markdown formatting from text and make it ReportLab-safe."""
    # Remove bold markers
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Remove any remaining markdown bullets
    text = re.sub(r'^\s*[\*\-\+]\s*', '', text, flags=re.MULTILINE)
    # Replace line breaks with spaces (ReportLab handles wrapping automatically)
    text = re.sub(r'<br\s*/?>', ' ', text)
    
    # Special handling for numbered lists - preserve line breaks before numbered items
    # Convert "1) something 2) another" to "1) something<br/>2) another"
    text = re.sub(r'(\S)\s+(\d+\))', r'\1<br/>\2', text)
    
    # Now replace remaining newlines with spaces
    text = re.sub(r'\n', ' ', text)
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove problematic HTML tags that ReportLab doesn't like
    text = re.sub(r'</?para>', '', text)
    return text.strip()

# Hardcoded table functions removed - now using dynamic LLM content parsing

def create_table_element(table_data, styles):
    """Create a reportlab Table element."""
    if not table_data or len(table_data) < 2:
        return None
    
    # Prepare table data
    formatted_data = []
    
    # Header row
    header_row = []
    for cell in table_data[0]:
        clean_cell = clean_text(cell)
        header_row.append(Paragraph(clean_cell, styles['table_header']))
    formatted_data.append(header_row)
    
    # Data rows
    for row in table_data[1:]:
        data_row = []
        for cell in row:
            clean_cell = clean_text(cell)
            data_row.append(Paragraph(clean_cell, styles['table_cell']))
        formatted_data.append(data_row)
    
    # Create table
    table = Table(formatted_data, repeatRows=1)
    
    # Apply styling
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data row styling
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('TEXTCOLOR', (0, 1), (-1, -1), black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    
    return table

def convert_markdown_to_pdf(markdown_file, output_file=None):
    """Convert markdown to PDF using actual LLM content."""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{markdown_file}' not found.")
        return False
    
    if output_file is None:
        output_file = Path(markdown_file).with_suffix('.pdf')
    
    try:
        styles = create_styles()
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=0.8*inch,
            leftMargin=0.8*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        story = []
        
        # Parse the actual LLM markdown content
        lines = content.strip().split('\n')
        
        current_section = None
        table_data = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Main title
            if line.startswith('# '):
                title_text = clean_text(line[2:])
                story.append(Paragraph(title_text, styles['title']))
                story.append(Spacer(1, 0.3*inch))
                
            # Section headers
            elif line.startswith('## '):
                # Finalize any current table before adding heading
                if in_table and table_data:
                    table_element = create_table_element(table_data, styles)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 0.2*inch))
                    table_data = []
                    in_table = False
                    
                section_text = clean_text(line[3:])
                story.append(Paragraph(section_text, styles['section']))
                current_section = section_text
                
            # Subsection headers  
            elif line.startswith('### '):
                # Finalize any current table before adding heading
                if in_table and table_data:
                    table_element = create_table_element(table_data, styles)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 0.2*inch))
                    table_data = []
                    in_table = False
                    
                subsection_text = clean_text(line[4:])
                story.append(Paragraph(subsection_text, styles['section']))
                
            # Table separator detection (ignore markdown table separators)
            elif '|' in line and ('---' in line or ':---' in line or '---:' in line):
                # Skip markdown table separator lines like |---|---|---| or |:---|:---|:---|
                continue
                
            # Table detection
            elif '|' in line:
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty cells at start/end
                if cells and not cells[0]:
                    cells = cells[1:]
                if cells and not cells[-1]:
                    cells = cells[:-1]
                
                # Check if this is a valid table row (must have at least 4 columns)
                if cells and len(cells) >= 4:
                    # If we're not in a table, or if column count changed, finalize previous table
                    if in_table and table_data and len(table_data[0]) != len(cells):
                        # Column count changed - finalize previous table
                        print(f"🔄 Column count changed from {len(table_data[0])} to {len(cells)} - finalizing previous table")
                        table_element = create_table_element(table_data, styles)
                        if table_element:
                            story.append(table_element)
                            story.append(Spacer(1, 0.2*inch))
                        table_data = []
                    
                    # Start new table or continue current one
                    if not in_table:
                        table_data = []
                        in_table = True
                        print(f"🆕 Starting new table with {len(cells)} columns")
                    
                    print(f"✅ Adding table row with {len(cells)} columns: {cells[0][:30]}...")
                    table_data.append(cells)
                else:
                    print(f"❌ SKIPPING incomplete table row with {len(cells)} columns: {line[:60]}...")
                    
            # Table separator (ignore lines starting with ---)
            elif line.startswith('---'):
                continue
                
            # End of table or regular text
            else:
                # If we were in a table, create it now
                if in_table and table_data:
                    table_element = create_table_element(table_data, styles)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 0.2*inch))
                    table_data = []
                    in_table = False
                
                # Regular paragraph
                if line:
                    clean_line = clean_text(line)
                    story.append(Paragraph(clean_line, styles['normal']))
        
        # Handle final table if exists
        if in_table and table_data:
            table_element = create_table_element(table_data, styles)
            if table_element:
                story.append(table_element)
                story.append(Spacer(1, 0.2*inch))
        
        # Footer space
        story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Successfully converted '{markdown_file}' to '{output_file}'")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 manual_table_converter.py <markdown_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_markdown_to_pdf(input_file, output_file)
    if success:
        print("🎉 PDF conversion completed successfully!")
    else:
        print("❌ PDF conversion failed.")
        sys.exit(1)



