# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class CarOwner(models.Model):
    _inherit = 'res.partner'

    is_car_owner = fields.Boolean(string='is car owner')
    is_contractor = fields.Boolean(string='is contractor')

    @api.onchange('is_car_owner', 'is_contractor')
    def car_or_contractor(self):
        for rec in self:
            if rec.is_car_owner and rec.is_contractor:
                raise ValidationError(_("You Can't Choose Both Car Owner and Contractor !"))


class LoanCarNo(models.Model):
    _inherit = 'fleet.vehicle'
    _rec_name = 'car_noe'

    is_company_car = fields.Boolean(string='is company car')
    is_outsource_car = fields.Boolean(string='is outsource car')
    car_owner = fields.Many2one('res.partner', string='Car Owner', domain="[('is_car_owner', '=', True)]")

    @api.onchange('is_company_car', 'is_outsource_car')
    def company_or_outsource(self):
        for rec in self:
            if rec.is_company_car and rec.is_outsource_car:
                raise ValidationError(_("You Can't Choose Both Company Car and Outsource Car !"))

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.model_id.name, rec.car_noe)))
        return res


class LoanCarReq(models.Model):
    _name = 'loan.car'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _description = 'create loan car '

    doc_num = fields.Char(string='Doc No', copy=False)
    from_date = fields.Date(string='From Date', )
    to_date = fields.Date(string='To Date', )
    date = fields.Date(string='Date')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]")
    line = fields.Many2one('transportation.line.request', string='transportation destination', )
    driver_name = fields.Many2one('hr.employee', string='Driver name(Requester Name)')
    deduction_period = fields.Integer(string='deduction period', required=True)
    loan_type = fields.Selection([('contractor', 'Contractor'), ('driver', 'Car Owner')], string='Loan Type')
    contractor = fields.Many2one('res.partner', string='Contractor', domain="[('is_contractor', '!=', False)]")
    loan_amount = fields.Float(string='Loan Amount', )
    loan_reasons = fields.Many2one('loan.reasons', string='Loan Reasons')
    ded_start_date = fields.Date(string='Deduction Start Date', required=True)
    depreciation_date = fields.Date()
    period = fields.Char(string='period')
    # loan_reason = fields.Text(string='Loan Reason')
    remain_loan_amount = fields.Float(string='remain amount', compute='action_compute_deduction', store=True)
    notes = fields.Text(string='notes')
    loan_count = fields.Integer(compute='compute_loan_count')
    amount = fields.Float(string='amount', compute='action_compute_deduction')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Driver / Requester'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    loan_car_ids = fields.One2many('loan.car.info', 'loan_car_id', string='Deduction Details')
    total_loan_for_car = fields.Float(string='total loan for specific car', compute='total_loan_for_spec_car')

    def total_loan_for_spec_car(self):
        for rec in self:
            total = 0.0
            total_rec = self.env['loan.car'].search([('car_no', '=', rec.car_no.id)])
            if total_rec:
                for loan in total_rec:
                    total += loan.loan_amount
            rec.total_loan_for_car = total

    def compute_loan_count(self):
        for rec in self:
            total_loan_count = self.env['loan.car'].search_count([('car_no', '=', rec.car_no.id)])
            rec.loan_count = total_loan_count

    def action_depreciation_date(self, ded_start_date, num):
        if ded_start_date:
            return ded_start_date + relativedelta(months=+num)

    def action_compute_deduction(self):
        self.amount = 0.0
        for rec in self:
            rec.loan_car_ids.unlink()
            counter = 0
            period = rec.deduction_period
            for x in range(period):
                rec.amount = rec.loan_amount / rec.deduction_period
                rem = rec.loan_amount - float(rec.amount)
                rec.remain_loan_amount = rem
                date = self.action_depreciation_date(rec.ded_start_date, counter)
                if date:
                    new_line = self.env['loan.car.info'].create({
                        'amount': rec.amount,
                        'date': date,
                        'loan_car_id': rec.id,
                    })
                    counter += 1
                    period -= 1

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        return self.write({'state': 'done'})

    # sequence function for doc_num
    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'loan.seq') or 'New'
        return super(LoanCarReq, self).create(vals)


class LoanCarReqInfo(models.Model):
    _name = 'loan.car.info'

    loan_car_id = fields.Many2one('loan.car', string='Deduction Details')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount', )
    paid = fields.Boolean(string='Paid')


class LoanCarStop(models.Model):
    _name = 'loan.car.stop'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'stop loan car request'

    doc_num = fields.Char(string='Doc No', readonly=True, required=True, copy=False, default='New')
    date = fields.Date(string='Date')
    loan_no = fields.Many2one('loan.car', string='Loan No')
    car_no = fields.Many2one(string="Car Number", related='loan_no.car_no', readonly=True)
    driver_contractor = fields.Char(string='Driver/Contractor', compute='compute_driver_contractor')
    # contractor = fields.Char(string='contractor', related='loan_no.contractor.name')
    line = fields.Many2one(string='transportation destination', related='loan_no.line')
    loan_amount_stop = fields.Float(string='Loan Amount', related='loan_no.loan_amount')
    monthly_ded = fields.Float(string='Monthly Deduction', compute='_loan_monthly_ded')
    res_ded_date = fields.Date(string='Resume Deduction Date')
    stop_loan_reason = fields.Text(string='Reasons for Stopping Loans for Cars Deduction')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Driver / Requester'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')
    amount_after_stop = fields.Float(string='Remaining Amount', compute='compute_after_stop')

    @api.onchange('loan_no')
    def compute_after_stop(self):
        pass
        global amount_length
        for rec in self:
            selected = self.env['loan.car.info'].search(
                [('loan_car_id.car_no', '=', rec.car_no.id), ])
            bool_list = []
            amount_list = []
            for x in selected:
                if not x.paid:
                    bool_list.append(x.paid)
                    amount_list.append(x.amount)
                    bool_length = len(bool_list)
                    amount_length = sum(amount_list)
                    print(bool_length, amount_length)
            rec.amount_after_stop = amount_length
            print(rec.amount_after_stop)

    @api.onchange('loan_no')
    def compute_driver_contractor(self):
        for rec in self:
            if rec.loan_no.driver_name:
                rec.driver_contractor = rec.loan_no.driver_name.driver_name
            else:
                rec.driver_contractor = rec.loan_no.contractor.name

    @api.onchange('loan_no')
    def _loan_monthly_ded(self):
        global value
        for rec in self:
            if rec.loan_no:
                selected = self.env['loan.car.info'].search([('loan_car_id.car_no', '=', rec.car_no.id)])
                for x in selected:
                    value = x.amount
                rec.monthly_ded = value

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        return self.write({'state': 'done'})

        # sequence function for doc_num

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'stop.loan.seq') or 'New'
        return super(LoanCarStop, self).create(vals)


class LoanCarClearance(models.Model):
    _name = 'loan.car.clearance'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'create loan car clearance'

    doc_num = fields.Char(string='Doc No', readonly=True, required=True, copy=False, default='New')
    date = fields.Date(string='Date')
    loan_no = fields.Many2one('loan.car', string='Loan No')
    stop_no = fields.Many2one('loan.car.stop')
    car_no = fields.Many2one(string="Car Number", related='loan_no.car_no', readonly=True)
    driver_contractor = fields.Char(string='Driver/Contractor', compute='compute_driver_contractor')
    line = fields.Many2one(string='transportation destination', related='loan_no.line')
    # seen by supervisor only after first approve
    clearance_type = fields.Selection([('full', 'Full'), ('partial', 'Partial')], string='Clearance Type')
    loan_amount = fields.Float(string='Loan Amount', related='stop_no.amount_after_stop')
    remain_loan_amount = fields.Float(string='Remaining Loan Amount', related='stop_no.amount_after_stop')
    amount_to_cleared = fields.Float(string='Amount To be Cleared', related='stop_no.amount_after_stop', store=True)
    rem_amount_after_ded = fields.Float(string='Remaining Amount After Deduction')
    deduction_period = fields.Integer(string='deduction period', related='loan_no.deduction_period')
    ded_start_date = fields.Date(string='Deduction Start Date', related='loan_no.ded_start_date')
    amount = fields.Float(string='amount', compute='action_compute_deduction')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Driver / Requester'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    car_clear_ids = fields.One2many('loan.car.clearance.info', 'car_clear_id', string='Deduction Details')

    @api.onchange('clearance_type', 'remain_loan_amount')
    def remain_amount(self):
        for rec in self:
            if rec.clearance_type == 'full':
                rec.amount_to_cleared = rec.remain_loan_amount

    @api.onchange('loan_no')
    def compute_driver_contractor(self):
        for rec in self:
            if rec.loan_no.driver_name:
                rec.driver_contractor = rec.loan_no.driver_name.driver_name
            else:
                rec.driver_contractor = rec.loan_no.contractor.name

    def action_depreciation_date(self, ded_start_date, num):
        if ded_start_date:
            return ded_start_date + relativedelta(months=+num)

    def action_compute_deduction(self):
        for rec in self:
            rec.car_clear_ids.unlink()
            counter = 1
            if rec.deduction_period <= 0:
                raise ValidationError(_("The deduction period must be more than zero!"))
            period = rec.deduction_period
            while period > 0:
                rec.amount = rec.loan_amount / rec.deduction_period
                rem = rec.loan_amount - float(rec.amount)
                rec.remain_loan_amount = rem
                date = self.action_depreciation_date(rec.ded_start_date, counter)
                print(date, '/////////////////////////////')
                if date:
                    new_line = self.env['loan.car.clearance.info'].create({
                        'amount': rec.amount,
                        'date': date,
                        'car_clear_id': rec.id,
                    })
                    counter += 1
                    period -= 1

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        if vals.get('doc_num', 'New') == 'New':
            vals['doc_num'] = self.env['ir.sequence'].next_by_code(
                'loan.clearance.seq') or 'New'
            result = super(LoanCarClearance, self).create(vals)
            return result


class LoanCarClearanceInfo(models.Model):
    _name = 'loan.car.clearance.info'

    car_clear_id = fields.Many2one('loan.car.clearance', string='Deduction Details')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    paid = fields.Boolean(string='Paid')


class CarMonthlyFees(models.Model):
    _name = 'car.monthly.fees'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'calculate car monthly fees'

    doc_num = fields.Char(string='Doc No', )
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    car_fees_ids = fields.One2many('car.monthly.fees.info', 'car_fees_id', string='car monthly fees information')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Driver / Requester'),
                                        ('approve', 'Approve by services supervisor'),
                                        ('approve2', 'Approve by Admin Manager'),
                                        ('done', 'Approve by GM / Executive Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_approve2(self):
        return self.write({'state': 'approve2'})

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'car.monthly.seq') or 'New'
        return super(CarMonthlyFees, self).create(vals)


class CarMonthlyFeesInfo(models.Model):
    _name = 'car.monthly.fees.info'

    car_fees_id = fields.Many2one('car.monthly.fees', string='car monthly fees information')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    total_contract = fields.Float(string='Total Amount', compute='total_contract_for_spec_car')
    car_warning = fields.Many2one('cars.warning')
    loan_no = fields.Many2one('loan.car')
    warning_deduction = fields.Float(string='Warning Deduction', compute='total_warning_for_spec_car')
    Loans_deduction = fields.Float(string='Loans Deduction', compute='total_loan_for_spec_car')
    fuel_deduction = fields.Float(string='Fuel Deduction', compute='total_fuel_for_spec_car')
    other_deduction = fields.Float(string='Other Deductions', )
    other_addition = fields.Float(string='Other Additions', )
    total_to_pay = fields.Float(string='Total to pay', compute='compute_total_to_pay')

    @api.onchange('car_no')
    def total_contract_for_spec_car(self):
        for rec in self:
            total = 0.0
            total_rec = self.env['car.contract'].search(
                [('state', '=', 'confirm'), ('car_no', '=', rec.car_no.id), ('date', '>=', rec.car_fees_id.date_from),
                 ('date', '<=', rec.car_fees_id.date_to)])
            if total_rec:
                for contract in total_rec:
                    total += contract.monthly_fees
            rec.total_contract = total

    @api.onchange('car_no')
    def total_warning_for_spec_car(self):
        for rec in self:
            total = 0.0
            total_rec = self.env['cars.warning'].search(
                [('state', '=', 'confirm'), ('car_no', '=', rec.car_no.id), ('date', '>=', rec.car_fees_id.date_from),
                 ('date', '<=', rec.car_fees_id.date_to)])
            if total_rec:
                for warning in total_rec:
                    total += warning.total_monthly_amount
            rec.warning_deduction = total

    @api.onchange('car_no')
    def total_fuel_for_spec_car(self):
        for rec in self:
            total = 0.0
            total_rec = self.env['car.fuel'].search(
                [('state', '=', 'confirm'), ('car_no', '=', rec.car_no.id),
                 ('date', '>=', rec.car_fees_id.date_from),
                 ('date', '<=', rec.car_fees_id.date_to)])
            if total_rec:
                for fuel in total_rec:
                    total += fuel.total_normal_fuel
            rec.fuel_deduction = total

    @api.onchange('car_no')
    def total_loan_for_spec_car(self):
        self.Loans_deduction = 0.0
        total = 0.0
        for rec in self:
            total_rec = self.env['loan.car.info'].search(
                [('loan_car_id.car_no', '=', rec.car_no.id), ('loan_car_id.state', '=', 'confirm'),
                 ('date', '>=', rec.car_fees_id.date_from), ('date', '<=', rec.car_fees_id.date_to)])
            print(total_rec, 'total_rec')
            if total_rec:
                for loan in total_rec:
                    total += loan.amount
                    print('totallllllllllllllllll', total)
            rec.Loans_deduction = total

    @api.onchange('total_amount', 'warning_deduction', 'Loans_deduction', 'fuel_deduction', 'other_deduction',
                  'other_addition')
    def compute_total_to_pay(self):
        for rec in self:
            rec.total_to_pay = rec.total_contract - rec.Loans_deduction - rec.warning_deduction - rec.fuel_deduction - \
                               rec.other_deduction + rec.other_addition


class CarContract(models.Model):
    _name = 'car.contract'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'car contract'

    doc_num = fields.Char(string='Doc No', copy=False)
    date = fields.Date(string='Date')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    line = fields.Many2one('adding.worker.to.transport.line', string='transportation destination',
                           domain="[('line_name', '!=', False)]", )
    driver_name = fields.Many2one('hr.employee', string='Driver Name / Requester')
    monthly_fees = fields.Float(string='Monthly Fees')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('done', 'Approve by Admin Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_done(self):
        # self.change_state()
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'car.contract.seq') or 'New'
        return super(CarContract, self).create(vals)


class CarFuelDeduction(models.Model):
    _name = 'car.fuel'
    _rec_name = 'doc_num'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'car fuel'

    doc_num = fields.Char(string='Doc No', copy=False)

    date = fields.Date(string='Date')
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    line = fields.Many2one('transportation.line.request', string='transportation destination', )
    driver_name = fields.Char(string='Driver Name', related='car_no.employee_id.name', )
    normal_fuel_qty = fields.Float(string='Normal Fuel QTY', store=True)
    total_normal_fuel = fields.Float(string='Total Normal Fuel', compute='_total_normal', store=True)
    normal_fuel_price = fields.Float(string='Normal Fuel Price', store=True)
    fuel_ids = fields.One2many('car.fuel.info', 'fuel_id', string='Fuel Details')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm by Services Employee'),
                                        ('approve', 'Approve by Services Supervisor'),
                                        ('done', 'Approve by Administration Manager'),
                                        ('cancel', 'Cancelled'),
                                        ],
                             readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.onchange('normal_fuel_qty', 'normal_fuel_price')
    def _total_normal(self):
        for rec in self:
            rec.total_normal_fuel = rec.normal_fuel_qty * rec.normal_fuel_price

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_approve(self):
        return self.write({'state': 'approve'})

    def action_done(self):
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['doc_num'] = self.env['ir.sequence'].next_by_code(
            'car.fuel.seq') or 'New'
        return super(CarFuelDeduction, self).create(vals)


class CarFuelDeductionInfo(models.Model):
    _name = 'car.fuel.info'

    fuel_id = fields.Many2one('car.fuel', )
    car_no = fields.Many2one('fleet.vehicle', string="Car Number", domain="[('car_noe', '!=', False)]", required=True)
    fuel_date = fields.Date(string='date')
    amount = fields.Float(string='amount')
