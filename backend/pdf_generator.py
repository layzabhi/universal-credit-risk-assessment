import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Draw header rule and text on pages after page 1
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(36, 756, 576, 756)
        self.drawString(36, 762, "Credit Risk Enterprise System - Underwriting Report")
        self.drawRightString(576, 762, datetime.now().strftime("%Y-%m-%d"))
        
        # Draw footer rule and page number
        self.line(36, 45, 576, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_text)
        self.drawString(36, 30, "CONFIDENTIAL - For Internal Use Only")
        self.restoreState()


def generate_underwriting_pdf(applicant_data: dict, explanation_data: dict) -> BytesIO:
    """
    Generates a beautifully styled corporate underwriting PDF report.
    applicant_data: dict of applicant properties
    explanation_data: dict of SHAP output (contributions)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor("#0f172a") # Slate 900
    accent_color = colors.HexColor("#06b6d4")  # Cyan 500
    border_color = colors.HexColor("#cbd5e1")  # Slate 300
    text_color = colors.HexColor("#334155")    # Slate 700
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color
    )
    
    label_style = ParagraphStyle(
        'LabelText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=primary_color
    )

    story = []
    
    # --- HEADER ---
    story.append(Spacer(1, 15))
    story.append(Paragraph("Enterprise Underwriting Decision Report", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"AI-Powered Credit Risk Intelligence Assessment Profile", ParagraphStyle('Sub', fontName='Helvetica', fontSize=12, leading=14, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 15))
    
    # --- DECISION BADGE BOX ---
    prob = applicant_data.get("default_probability", 0.0)
    decision = applicant_data.get("prediction", "N/A")
    
    if decision == "Non-Defaulter" or prob < 0.38:
        badge_bg = colors.HexColor("#dcfce7")
        badge_text_color = colors.HexColor("#15803d")
        badge_label = "APPROVED"
        summary_text = "Applicant demonstrates strong repayment stability with manageable financial exposure and favorable underwriting indicators."
    else:
        badge_bg = colors.HexColor("#fee2e2")
        badge_text_color = colors.HexColor("#b91c1c")
        badge_label = "REJECTED"
        summary_text = "Applicant demonstrates elevated default probability due to financial burden and underwriting instability indicators."
        
    decision_table_data = [
        [
            Paragraph("AI DECISION STATUS", ParagraphStyle('BadgeLabel', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#475569"))),
            Paragraph("DEFAULT PROBABILITY", ParagraphStyle('BadgeLabel', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#475569"))),
            Paragraph("RISK RATING", ParagraphStyle('BadgeLabel', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#475569")))
        ],
        [
            Paragraph(badge_label, ParagraphStyle('BadgeText', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=badge_text_color)),
            Paragraph(f"{prob * 100:.1f}%", ParagraphStyle('BadgeText', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=primary_color)),
            Paragraph("LOW RISK" if prob < 0.25 else ("MEDIUM RISK" if prob < 0.50 else "HIGH RISK"), ParagraphStyle('BadgeText', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=badge_text_color if prob >= 0.5 else primary_color))
        ]
    ]
    
    decision_table = Table(decision_table_data, colWidths=[180, 180, 180])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), badge_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 1, badge_text_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(decision_table)
    story.append(Spacer(1, 15))
    
    # --- SUMMARY SECTION ---
    story.append(Paragraph("Executive Underwriting Summary", section_style))
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 15))
    
    # --- APPLICANT PROFILE TABLE ---
    story.append(Paragraph("Applicant Financial Profile", section_style))
    
    profile_data = [
        [
            Paragraph("Full Name", label_style), Paragraph(str(applicant_data.get("full_name", "N/A")), body_style),
            Paragraph("Age", label_style), Paragraph(f"{int(applicant_data.get('age', 0))} Years", body_style)
        ],
        [
            Paragraph("Annual Income", label_style), Paragraph(f"${applicant_data.get('income', 0):,.2f}", body_style),
            Paragraph("Loan Requested", label_style), Paragraph(f"${applicant_data.get('loan_amount', 0):,.2f}", body_style)
        ],
        [
            Paragraph("Credit Score (FICO)", label_style), Paragraph(f"{int(applicant_data.get('credit_score', 0))}", body_style),
            Paragraph("Dependents", label_style), Paragraph(str(int(applicant_data.get('dependents', 0))), body_style)
        ],
        [
            Paragraph("Employment Tenure", label_style), Paragraph(f"{applicant_data.get('employment_years', 0):.1f} Years", body_style),
            Paragraph("Database ID Reference", label_style), Paragraph(f"REF#{applicant_data.get('id', 'N/A')}", body_style)
        ]
    ]
    
    profile_table = Table(profile_data, colWidths=[120, 150, 120, 150])
    profile_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f8fafc")),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 20))
    
    # --- EXPLAINABLE AI (SHAP FACTORS) ---
    story.append(Paragraph("Advanced Explainable AI (SHAP Analysis)", section_style))
    story.append(Paragraph("This section outlines the feature contributions that influenced the machine learning model's credit decision. Positive values increase default risk, negative values decrease default risk.", body_style))
    story.append(Spacer(1, 10))
    
    contributions = explanation_data.get("contributions", [])
    
    # Extract Risk Increasers (positive SHAP values) and Reducers (negative SHAP values)
    risk_increasers = [c for c in contributions if c["shap_value"] > 0][:3]
    risk_reducers = [c for c in contributions if c["shap_value"] < 0][:3]
    
    shap_rows = [
        [
            Paragraph("Feature Parameter", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white)),
            Paragraph("Actual Value", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white)),
            Paragraph("SHAP Value Impact", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white)),
            Paragraph("Risk Signal", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white))
        ]
    ]
    
    # Append Increasers
    for inc in risk_increasers:
        impact = f"+{inc['shap_value']:.4f}"
        feat_name = inc["feature"].replace("_", " ").title()
        val_formatted = f"{inc['value']:.2f}" if isinstance(inc['value'], float) else str(inc['value'])
        shap_rows.append([
            Paragraph(feat_name, body_style),
            Paragraph(val_formatted, body_style),
            Paragraph(impact, ParagraphStyle('RedImpact', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#b91c1c"))),
            Paragraph("Increases Default Risk", ParagraphStyle('RedLabel', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor("#b91c1c")))
        ])
        
    # Append Reducers
    for red in risk_reducers:
        impact = f"{red['shap_value']:.4f}"
        feat_name = red["feature"].replace("_", " ").title()
        val_formatted = f"{red['value']:.2f}" if isinstance(red['value'], float) else str(red['value'])
        shap_rows.append([
            Paragraph(feat_name, body_style),
            Paragraph(val_formatted, body_style),
            Paragraph(impact, ParagraphStyle('GreenImpact', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#15803d"))),
            Paragraph("Decreases Default Risk", ParagraphStyle('GreenLabel', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor("#15803d")))
        ])
        
    shap_table = Table(shap_rows, colWidths=[160, 110, 120, 150])
    shap_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(shap_table)
    story.append(Spacer(1, 20))
    
    # --- RECOMMENDATIONS SECTION ---
    story.append(Paragraph("Actionable Underwriting Recommendations", section_style))
    
    recs = []
    if prob >= 0.50:
        recs = [
            Paragraph("• <b>Decline/Restructure</b>: The borrower defaults probability exceeds the threshold limit. Decline or significantly reduce approved exposure.", body_style),
            Paragraph("• <b>Collateral Enhancement</b>: Request secondary co-signer validation or asset collateral backing before any override approval.", body_style),
            Paragraph("• <b>Verify Employment</b>: Perform direct visual check on job stability and verify monthly income declarations through bank audits.", body_style)
        ]
    elif prob >= 0.25:
        recs = [
            Paragraph("• <b>Conditional Approval</b>: Approve with down-adjusted loan amount or slightly elevated interest pricing tiers.", body_style),
            Paragraph("• <b>LTV Reduction</b>: Mandate a higher down-payment ratio to lower the Loan-To-Value exposure.", body_style),
            Paragraph("• <b>Monitoring Frequency</b>: Place the applicant on a quarterly account health monitoring checklist.", body_style)
        ]
    else:
        recs = [
            Paragraph("• <b>Streamlined Approval</b>: Standard low-risk applicant. Standard pricing model applies.", body_style),
            Paragraph("• <b>Cross-Sell Eligibility</b>: Eligible for secondary revolving products (e.g. premium credit cards).", body_style),
            Paragraph("• <b>Standard Monitoring</b>: Annual account audits recommended.", body_style)
        ]
        
    recs_table_data = [[r] for r in recs]
    recs_table = Table(recs_table_data, colWidths=[540])
    recs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(recs_table)
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
