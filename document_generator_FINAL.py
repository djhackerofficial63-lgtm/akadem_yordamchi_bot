from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Generate documents with different styles"""
    
    def __init__(self):
        self.output_dir = Path("documents")
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # APA Style
        self.styles.add(ParagraphStyle(
            name='APA_Title',
            parent=self.styles['Heading1'],
            fontSize=14,
            bold=True,
            spaceAfter=12,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='APA_Body',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=24,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            firstLineIndent=36
        ))
        
        # Harvard Style
        self.styles.add(ParagraphStyle(
            name='Harvard_Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            bold=True,
            spaceAfter=18,
        ))
        
        self.styles.add(ParagraphStyle(
            name='Harvard_Body',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=22,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
        ))
    
    def generate_document(self, doc_type, style, title, content, user_id):
        """Generate document based on type and style"""
        
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/{user_id}_{doc_type}_{timestamp}.pdf"
            
            # Create PDF
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Build story
            story = []
            
            # Title
            if style == "apa":
                story.append(Paragraph(title, self.styles['APA_Title']))
            else:
                story.append(Paragraph(title, self.styles['Harvard_Title']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Content
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    if style == "apa":
                        story.append(Paragraph(para.strip(), self.styles['APA_Body']))
                    else:
                        story.append(Paragraph(para.strip(), self.styles['Harvard_Body']))
                    story.append(Spacer(1, 0.2*inch))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%d.%m.%Y')}",
                self.styles['Normal']
            ))
            
            # Build PDF
            doc.build(story)
            logger.info(f"✅ Document generated: {filename}")
            
            return filename
        
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return None
