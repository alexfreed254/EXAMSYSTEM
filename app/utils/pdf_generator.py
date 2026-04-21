from io import BytesIO
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, KeepTogether, PageBreak)
from reportlab.pdfgen import canvas
import qrcode


def _make_styles():
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('T', parent=styles['Normal'], fontSize=16,
                                 textColor=colors.HexColor('#1F4E79'),
                                 alignment=TA_CENTER, spaceAfter=4,
                                 fontName='Helvetica-Bold'),
        'subtitle': ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                                    alignment=TA_CENTER, spaceAfter=2),
        'trans_title': ParagraphStyle('TT', parent=styles['Normal'], fontSize=13,
                                       fontName='Helvetica-Bold',
                                       textColor=colors.HexColor('#C00000'),
                                       alignment=TA_CENTER, spaceBefore=4),
        'label': ParagraphStyle('L', parent=styles['Normal'], fontSize=9,
                                 textColor=colors.HexColor('#555555'),
                                 fontName='Helvetica-Bold'),
        'value': ParagraphStyle('V', parent=styles['Normal'], fontSize=9,
                                 textColor=colors.HexColor('#111111')),
        'small': ParagraphStyle('Sm', parent=styles['Normal'], fontSize=8,
                                 textColor=colors.HexColor('#666666'),
                                 alignment=TA_CENTER),
        'section': ParagraphStyle('Sec', parent=styles['Normal'], fontSize=10,
                                   fontName='Helvetica-Bold',
                                   textColor=colors.white,
                                   alignment=TA_LEFT),
        'cell': ParagraphStyle('C', parent=styles['Normal'], fontSize=8),
        'cell_bold': ParagraphStyle('CB', parent=styles['Normal'], fontSize=8,
                                     fontName='Helvetica-Bold'),
        'footer': ParagraphStyle('F', parent=styles['Normal'], fontSize=7,
                                  textColor=colors.HexColor('#888888'),
                                  alignment=TA_CENTER),
        'competent': ParagraphStyle('Comp', parent=styles['Normal'], fontSize=8,
                                     textColor=colors.HexColor('#006400'),
                                     fontName='Helvetica-Bold'),
        'not_competent': ParagraphStyle('NC', parent=styles['Normal'], fontSize=8,
                                         textColor=colors.HexColor('#C00000'),
                                         fontName='Helvetica-Bold'),
    }

def _build_header(story, transcript, st):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    govt_logo = os.path.join(base_dir, 'GOVT LOGO.png')
    ttti_logo = os.path.join(base_dir, 'TTTI LOGO.png')
    logo_size = 2.5 * cm
    left_cell = Image(govt_logo, width=logo_size, height=logo_size) if os.path.exists(govt_logo) else Paragraph('GOK', st['label'])
    right_cell = Image(ttti_logo, width=logo_size, height=logo_size) if os.path.exists(ttti_logo) else Paragraph('TTTI', st['label'])
    center_cell = [
        Paragraph('THIKA TECHNICAL TRAINING INSTITUTE', st['title']),
        Paragraph('P.O. Box 93 - 01000, Thika | Tel: +254-67-22396 | Email: info@ttti.ac.ke', st['small']),
        Paragraph('OFFICIAL ACADEMIC TRANSCRIPT', st['trans_title']),
    ]
    hdr = Table([[left_cell, center_cell, right_cell]], colWidths=[3*cm, 12*cm, 3*cm])
    hdr.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EBF3FB')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1F4E79')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.2*cm))
    div = Table([['']], colWidths=[18*cm])
    div.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1F4E79')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(div)
    story.append(Spacer(1, 0.3*cm))
    status_color = colors.HexColor('#006400') if transcript.is_official else colors.grey
    serial_row = [[
        Paragraph('<b>Serial No:</b> ' + transcript.serial_number, st['value']),
        Paragraph('<b>Date Issued:</b> ' + transcript.generated_at.strftime('%d %B %Y'), st['value']),
        Paragraph('<b>Status:</b> ' + ('OFFICIAL' if transcript.is_official else 'UNOFFICIAL'),
                  ParagraphStyle('Stat', parent=getSampleStyleSheet()['Normal'],
                                  fontSize=9, fontName='Helvetica-Bold', textColor=status_color)),
    ]]
    st_tbl = Table(serial_row, colWidths=[6*cm, 6*cm, 6*cm])
    st_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F7FF')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#AAAAAA')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(st_tbl)
    story.append(Spacer(1, 0.4*cm))


def _section_header(title, st):
    t = Table([[Paragraph(title, st['section'])]], colWidths=[18*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1F4E79')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def _trainee_info(story, trainee, enrollment, program, st):
    story.append(_section_header('STUDENT INFORMATION', st))
    story.append(Spacer(1, 0.2*cm))
    dob = trainee.date_of_birth.strftime('%d %B %Y') if trainee.date_of_birth else 'N/A'
    intake = (enrollment.intake_month + ' ' + str(enrollment.intake_year)) if enrollment else 'N/A'
    info_data = [
        [Paragraph('<b>Full Name:</b>', st['label']), Paragraph(trainee.user.full_name.upper(), st['value']),
         Paragraph('<b>Admission No:</b>', st['label']), Paragraph(trainee.admission_number, st['value'])],
        [Paragraph('<b>National ID:</b>', st['label']), Paragraph(trainee.national_id or 'N/A', st['value']),
         Paragraph('<b>Date of Birth:</b>', st['label']), Paragraph(dob, st['value'])],
        [Paragraph('<b>Gender:</b>', st['label']), Paragraph(trainee.gender or 'N/A', st['value']),
         Paragraph('<b>County:</b>', st['label']), Paragraph(trainee.county or 'N/A', st['value'])],
        [Paragraph('<b>Programme:</b>', st['label']), Paragraph(program.name, st['value']),
         Paragraph('<b>Level:</b>', st['label']), Paragraph(program.level or 'N/A', st['value'])],
        [Paragraph('<b>Department:</b>', st['label']),
         Paragraph(program.department.name if program.department else 'N/A', st['value']),
         Paragraph('<b>Intake:</b>', st['label']), Paragraph(intake, st['value'])],
        [Paragraph('<b>ISCED Code:</b>', st['label']), Paragraph(program.isced_code or 'N/A', st['value']),
         Paragraph('<b>Duration:</b>', st['label']), Paragraph(str(program.duration_years) + ' Year(s)', st['value'])],
    ]
    info_tbl = Table(info_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    info_tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#DDDDDD')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F7FF')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0F7FF')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.4*cm))


def _results_table(story, results_by_module, academic_year, st):
    story.append(_section_header('ACADEMIC RESULTS - ' + academic_year.name, st))
    story.append(Spacer(1, 0.2*cm))
    col_headers = [
        Paragraph('<b>Unit Code</b>', st['cell_bold']),
        Paragraph('<b>Unit of Competency</b>', st['cell_bold']),
        Paragraph('<b>Cat</b>', st['cell_bold']),
        Paragraph('<b>Mod</b>', st['cell_bold']),
        Paragraph('<b>CA Theory</b>', st['cell_bold']),
        Paragraph('<b>CA Pract.</b>', st['cell_bold']),
        Paragraph('<b>SA Theory</b>', st['cell_bold']),
        Paragraph('<b>SA Pract.</b>', st['cell_bold']),
        Paragraph('<b>Wtd Theory</b>', st['cell_bold']),
        Paragraph('<b>Wtd Pract.</b>', st['cell_bold']),
        Paragraph('<b>Overall</b>', st['cell_bold']),
        Paragraph('<b>Rating</b>', st['cell_bold']),
        Paragraph('<b>Status</b>', st['cell_bold']),
    ]
    table_data = [col_headers]
    col_widths = [2.5*cm, 4.0*cm, 0.8*cm, 0.8*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.3*cm, 1.8*cm, 1.8*cm]
    total_credits = 0
    competent_credits = 0
    row_colors = []
    for mod_num in sorted(results_by_module.keys()):
        mod_results = results_by_module[mod_num]
        mod_row = [Paragraph('<b>MODULE ' + str(mod_num) + '</b>', st['cell_bold'])] + [''] * 12
        table_data.append(mod_row)
        row_colors.append(len(table_data) - 1)
        for r in mod_results:
            c = r.course
            is_comp = r.competency_status == 'Competent'
            status_style = st['competent'] if is_comp else st['not_competent']
            def fmt(v):
                return ('{:.1f}'.format(v)) if v is not None else '-'
            row = [
                Paragraph(c.tvet_unit_code or c.code, st['cell']),
                Paragraph(c.name, st['cell']),
                Paragraph(c.unit_category or '-', st['cell']),
                Paragraph(str(c.module_number or '-'), st['cell']),
                Paragraph(fmt(r.ca_theory), st['cell']),
                Paragraph(fmt(r.ca_practical), st['cell']),
                Paragraph(fmt(r.sa_theory), st['cell']),
                Paragraph(fmt(r.sa_practical), st['cell']),
                Paragraph(fmt(r.weighted_theory), st['cell']),
                Paragraph(fmt(r.weighted_practical), st['cell']),
                Paragraph('<b>' + fmt(r.overall_score) + '</b>', st['cell_bold']),
                Paragraph(r.competency_rating or '-', st['cell']),
                Paragraph(r.competency_status or '-', status_style),
            ]
            table_data.append(row)
            total_credits += c.credit_factor
            if is_comp:
                competent_credits += c.credit_factor
    results_tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E75B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F9FF')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
    ]
    for row_idx in row_colors:
        style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#D6E4F0')))
        style_cmds.append(('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))
        style_cmds.append(('SPAN', (0, row_idx), (-1, row_idx)))
    results_tbl.setStyle(TableStyle(style_cmds))
    story.append(results_tbl)
    story.append(Spacer(1, 0.4*cm))
    return total_credits, competent_credits


def _summary_section(story, total_credits, competent_credits, results_list, st):
    story.append(_section_header('SUMMARY AND COMPETENCY DECLARATION', st))
    story.append(Spacer(1, 0.2*cm))
    total_units = len(results_list)
    competent_units = sum(1 for r in results_list if r.competency_status == 'Competent')
    scores = [r.overall_score for r in results_list if r.overall_score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    summary_data = [
        [Paragraph('<b>Total Units Assessed:</b>', st['label']), Paragraph(str(total_units), st['value']),
         Paragraph('<b>Units Competent:</b>', st['label']), Paragraph(str(competent_units), st['value'])],
        [Paragraph('<b>Not Yet Competent:</b>', st['label']), Paragraph(str(total_units - competent_units), st['value']),
         Paragraph('<b>Average Score:</b>', st['label']), Paragraph('{:.1f}%'.format(avg_score), st['value'])],
        [Paragraph('<b>Total Credit Factor:</b>', st['label']), Paragraph('{:.1f}'.format(total_credits), st['value']),
         Paragraph('<b>Credits Attained:</b>', st['label']), Paragraph('{:.1f}'.format(competent_credits), st['value'])],
    ]
    sum_tbl = Table(summary_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    sum_tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#DDDDDD')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F7FF')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0F7FF')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.4*cm))
    story.append(_section_header('GRADING KEY (TVET CDACC)', st))
    story.append(Spacer(1, 0.2*cm))
    grade_data = [
        [Paragraph('<b>Marks Range</b>', st['cell_bold']), Paragraph('<b>Competence Rating</b>', st['cell_bold']), Paragraph('<b>Description</b>', st['cell_bold'])],
        [Paragraph('80 - 100', st['cell']), Paragraph('Attained Mastery', st['cell']), Paragraph('Exceptional performance exceeding all competency standards', st['cell'])],
        [Paragraph('65 - 79', st['cell']), Paragraph('Proficient', st['cell']), Paragraph('Above average performance meeting all competency standards', st['cell'])],
        [Paragraph('50 - 64', st['cell']), Paragraph('Competent', st['cell']), Paragraph('Satisfactory performance meeting minimum competency standards', st['cell'])],
        [Paragraph('Below 50', st['cell']), Paragraph('Not Yet Competent', st['cell']), Paragraph('Performance does not meet minimum competency standards', st['cell'])],
    ]
    grade_tbl = Table(grade_data, colWidths=[3*cm, 4*cm, 11*cm])
    grade_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E75B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F9FF')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(grade_tbl)
    story.append(Spacer(1, 0.4*cm))


def _signature_section(story, transcript, st):
    story.append(_section_header('AUTHENTICATION AND SIGNATURES', st))
    story.append(Spacer(1, 0.3*cm))
    sig_data = [
        [Paragraph('_______________________', st['value']), Paragraph('_______________________', st['value']), Paragraph('_______________________', st['value'])],
        [Paragraph('<b>Registrar</b>', st['label']), Paragraph('<b>Principal</b>', st['label']), Paragraph('<b>Head of Department</b>', st['label'])],
        [Paragraph('Date: _______________', st['small']), Paragraph('Date: _______________', st['small']), Paragraph('Date: _______________', st['small'])],
    ]
    sig_tbl = Table(sig_data, colWidths=[6*cm, 6*cm, 6*cm])
    sig_tbl.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sig_tbl)
    story.append(Spacer(1, 0.4*cm))
    qr_data = 'TTTI-TRANSCRIPT:' + transcript.serial_number + ':' + transcript.trainee.admission_number
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reportlab = Image(qr_buffer, width=2.5*cm, height=2.5*cm)
    qr_row = [[
        qr_reportlab,
        Paragraph(
            '<b>Verification Code:</b> ' + transcript.serial_number + '<br/>'
            'This transcript can be verified at: <i>results.ttti.ac.ke</i><br/>'
            '<b>IMPORTANT:</b> This document is only valid with the official stamp and signature of the Registrar.',
            st['small']
        )
    ]]
    qr_tbl = Table(qr_row, colWidths=[3*cm, 15*cm])
    qr_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFDE7')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#F0C040')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(qr_tbl)
    story.append(Spacer(1, 0.3*cm))
    footer_text = ('This is an official transcript of Thika Technical Training Institute. '
                   'Serial: ' + transcript.serial_number + ' | Generated: ' + transcript.generated_at.strftime('%d/%m/%Y %H:%M') + ' | '
                   'TTTI is accredited by TVETA. Unauthorized alteration of this document is a criminal offence.')
    story.append(Paragraph(footer_text, st['footer']))


def generate_transcript_pdf(transcript):
    from app.models import Result, Course, Enrollment
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             topMargin=1*cm, bottomMargin=1.5*cm,
                             leftMargin=1.5*cm, rightMargin=1.5*cm)
    story = []
    st = _make_styles()
    trainee = transcript.trainee
    program = transcript.program
    academic_year = transcript.academic_year
    enrollment = Enrollment.query.filter_by(trainee_id=trainee.id, program_id=program.id).first()
    results_list = (Result.query
                    .filter_by(trainee_id=trainee.id, academic_year_id=academic_year.id, is_published=True)
                    .join(Course)
                    .filter(Course.program_id == program.id)
                    .order_by(Course.module_number, Course.name).all())
    results_by_module = {}
    for r in results_list:
        mod = r.course.module_number or 0
        if mod not in results_by_module:
            results_by_module[mod] = []
        results_by_module[mod].append(r)
    _build_header(story, transcript, st)
    _trainee_info(story, trainee, enrollment, program, st)
    total_credits, competent_credits = _results_table(story, results_by_module, academic_year, st)
    _summary_section(story, total_credits, competent_credits, results_list, st)
    _signature_section(story, transcript, st)
    doc.build(story)
    buffer.seek(0)
    return buffer

