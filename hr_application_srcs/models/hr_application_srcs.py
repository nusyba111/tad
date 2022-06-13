# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import models, fields, api, _



class ClassInherit(models.Model):
    _name = 'app.lines.inherit'

    family_name = fields.Char(string="Family Name",required=True)
    nationality= fields.Char(string="nationality")


class ApplicationHrSrcsCustom(models.Model):
    # _name = 'fleet.srcs.custom'
    _inherit = 'hr.applicant'

    application_type = fields.Selection([
        ('full time', 'Full time'),
        ('part time', 'part time'),
        ('other', 'Other')
    ], default='full time', string='Applicant Type',required=True)
    applicaition_no=fields.Integer(string='Applicant Number')
    frist_name = fields.Char(string="Frist Name",required=True)
    father_name = fields.Char(string="Father's Name", required=True)
    grand_father_name = fields.Char(string=" Grandfather's Name",required=True)
    family_name = fields.Char(string="Family Name",required=True)
    nationality= fields.Char(string="nationality")
    religion= fields.Char(string="Religion")
    gosi_no=fields.Integer(string='Gosi No')
    birth_date=fields.Date(string="Date of Birth")
    place_of_birth= fields.Char(string="Place of Birth")
    marital_status= fields.Char(string="Marital Status")
    no_of_childern=fields.Integer(string="No.of Chidern")
    current_address = fields.Char(string="Current Address",required=True)
    fax= fields.Integer(string="Fax")
    ed_background = fields.One2many("app.lines","employee_id",string="Education")
    ed_language=fields.One2many("app.lines","employee_id",string="Languages")
    ed_course=fields.One2many("app.lines","employee_id",string="Course")
    ed_experince=fields.One2many("app.lines","employee_id",string="Experince")
    disease = fields.Boolean(string="Do you have any chorinc disease?",default=True, required=True)
    disease_note=fields.Char(string="Disease Note")
    driving_license= fields.Boolean(string="Do you have a valid Sudanese driving license?")
    crime= fields.Selection([
        ('ys', 'Yes'),
        ('no', 'No'),
    ], default='no',string="have you committed any crime or been in prison?", required=True)
    crime_note=fields.Char(string="Crime Note")
    date_to_work=fields.Date(string="When you are able to work?")
    date=fields.Date(string="Date")
    signature=fields.Text(string="Signature")
    reference_info=fields.One2many("app.lines","employee_id",string="Refernce Information")
    log_of_src=fields.Binary(string="Src Logo")


class ApplicationLinesSrcsLines(models.Model):
    _name = 'app.lines'

    employee_id = fields.Many2one("hr.applicant",string="Employee Name")
    academic_qualification=fields.Char(string="Academic Qualification ")
    major=fields.Char(string="Major")
    name_of_school=fields.Char(string="Name of School")
    location=fields.Char(string="Location")
    no_of_years=fields.Integer(string='Number of Years')
    gpa=fields.Float(string='GPA')
    Graduation_year=fields.Date(string="Graduation Year")
    #    languages fields
    arabic = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], default='good', string='Arabic',required=True)
    english = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], default='good', string='English',required=True)
    other_languages= fields.Char(string="Other Languages")
    #    training courses fields
    course_title=fields.Char(string="Course Title")
    course_duration=fields.Text(string="Course Duartion")
    org_by=fields.Char(string="Course Title")
    date_of_course=fields.Date(string="Course Date")
    course_location=fields.Char(string="Course Location")
    #    experinces fields
    employer_name=fields.Char(string="Employer Name")
    position=fields.Char(string="Position")
    date_of_employer_start=fields.Date(string="Employer Started Date")
    date_of_employer_end=fields.Date(string="Employer Ended Date")
    monthly_salary=fields.Float(string='Monthly Salary')
    reason_for_leaving=fields.Text(string="Reason for Leaving")
    reference_name=fields.Char(string="Reference Name")
    reference_phone=fields.Text(string="Reference Phone")
    reference_email=fields.Char(string="Reference E-mail")
    reference_address=fields.Text(string="Reference Address")
    reference_position=fields.Char(string="Reference Position")

    #    other information fields
    # disease = fields.Selection([
    #     ('yes','Yes'),
    #     ('no','No')
    # ], default='yes', string=' Do you have any chorinc disease?')
    










