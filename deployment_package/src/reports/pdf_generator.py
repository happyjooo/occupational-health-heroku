"""
PDF Generator Module
Converts markdown summaries to professionally formatted PDF reports
"""

import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, orange, blue, green, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import re
from io import BytesIO
from datetime import datetime

class PDFGenerator:
    """Generates PDF reports from markdown summaries"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=24,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=black,
            bold=True
        ))
        
        # Subsection heading style
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=black,
            bold=True
        ))
        
        # High-risk exposure style (highlighted in red)
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4,
            textColor=red,
            bold=True
        ))
        
        # Normal bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4,
            textColor=black
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=black,
            bold=True
        ))
    
    def _process_markdown_to_elements(self, markdown_text: str) -> list:
        """
        Convert markdown text to ReportLab flowable elements with proper table support
        
        Args:
            markdown_text: Raw markdown text from AI summary
            
        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        lines = markdown_text.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Handle main titles
            if line.startswith('# '):
                title_text = self._clean_markdown(line[2:])
                elements.append(Paragraph(title_text, self.styles['CustomTitle']))
                elements.append(Spacer(1, 12))
                
            # Handle section headings
            elif line.startswith('## '):
                heading_text = self._clean_markdown(line[3:])
                elements.append(Paragraph(heading_text, self.styles['SectionHeading']))
                
            # Handle subsections
            elif line.startswith('### '):
                heading_text = self._clean_markdown(line[4:])
                elements.append(Paragraph(heading_text, self.styles['SubHeading']))
                
            # Handle tables
            elif '|' in line and not line.startswith('---'):
                table_data, i = self._parse_table(lines, i)
                if table_data:
                    table = self._create_table(table_data)
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                continue
                
            # Handle horizontal rules
            elif line.startswith('---'):
                elements.append(Spacer(1, 12))
                
            # Handle bullet points
            elif line.startswith('- '):
                bullet_text = self._clean_markdown(line[2:])
                if bullet_text.startswith('(!)'):
                    # High-risk exposure
                    risk_text = bullet_text[3:].strip()
                    formatted_text = f"⚠️ {risk_text}"
                    elements.append(Paragraph(formatted_text, self.styles['HighRisk']))
                else:
                    formatted_text = f"• {bullet_text}"
                    elements.append(Paragraph(formatted_text, self.styles['BulletPoint']))
                    
            # Handle bold text
            elif line.startswith('**') and line.endswith('**'):
                bold_text = self._clean_markdown(line)
                elements.append(Paragraph(bold_text, self.styles['JobTitle']))
                
            # Handle regular paragraphs
            else:
                cleaned_text = self._clean_markdown(line)
                if cleaned_text:
                    elements.append(Paragraph(cleaned_text, self.styles['Normal']))
            
            i += 1
        
        return elements
    
    def _clean_markdown(self, text: str) -> str:
        """Clean markdown syntax from text"""
        # Remove markdown bold syntax
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Remove markdown italic syntax
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Remove markdown code syntax
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        return text
    
    def _parse_table(self, lines: list, start_index: int) -> tuple:
        """Parse markdown table into data structure"""
        table_data = []
        i = start_index
        
        # Find the end of the table
        while i < len(lines):
            line = lines[i].strip()
            if not line or '|' not in line:
                break
            if line.startswith('---'):
                i += 1
                continue
            table_data.append(line)
            i += 1
        
        if not table_data:
            return None, i
        
        # Parse table rows
        parsed_data = []
        for row in table_data:
            cells = [cell.strip() for cell in row.split('|')]
            # Remove empty cells at start/end
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            parsed_data.append(cells)
        
        return parsed_data, i - 1
    
    def _create_table(self, table_data: list) -> Table:
        """Create a ReportLab Table from parsed data"""
        if not table_data:
            return None
        
        # Create table
        table = Table(table_data)
        
        # Style the table
        table_style = TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
        
        # Apply alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9'))
        
        table.setStyle(table_style)
        return table
    
    def generate_pdf(self, markdown_summary: str) -> bytes:
        """
        Generate a PDF from markdown summary text using the fast converter
        
        Args:
            markdown_summary: Markdown-formatted summary from AI
            
        Returns:
            PDF file as bytes
        """
        try:
            # Use the final converter that shows table data in structured format
            from manual_table_converter import convert_markdown_to_pdf
            
            # Create temporary files for both markdown and PDF
            import tempfile
            import os
            
            # Create temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
                md_file.write(markdown_summary)
                temp_md_filename = md_file.name
            
            # Create temporary PDF file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                temp_pdf_filename = pdf_file.name
            
            # Convert markdown to PDF (now with correct parameters)
            convert_markdown_to_pdf(temp_md_filename, temp_pdf_filename)
            
            # Read the PDF bytes
            with open(temp_pdf_filename, 'rb') as f:
                pdf_bytes = f.read()
            
            # Clean up temp files
            os.unlink(temp_md_filename)
            os.unlink(temp_pdf_filename)
            
            return pdf_bytes
            
        except Exception as e:
            print(f"❌ PDF generation error: {e}")
            raise
    
    def save_pdf_to_file(self, markdown_summary: str, filename: str) -> str:
        """
        Save PDF to a file (for testing purposes)
        
        Args:
            markdown_summary: Markdown text to convert
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        pdf_bytes = self.generate_pdf(markdown_summary)
        
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        
        return filename
