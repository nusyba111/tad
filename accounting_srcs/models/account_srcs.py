from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class AccountSrcs(models.Model):
    _inherit = "account.move"
    
    state = fields.Selection([
        ('draft', 'Draft'),('finance_direct','Finance Director '),
        ('secratry_general','Secretary General  '),
        ('posted','Posted'),('cancel','cancelled'),
    ],default='draft', string='state')

    def approve_finance(self):
        self.state = "finance_direct"

    def approve_secratry(self):
        self.state = "secratry_general"

    def _post(self, soft=True):
        res = super(AccountSrcs, self)._post(soft=True)
        print('____________res',res)
        for record in self:
            if record.move_type == 'in_invoice':

                for rec in record.invoice_line_ids:
                    changed_deffernce = abs(rec.credit - rec.debit)
                    fixed_deffernce = abs(rec.credit - rec.debit)
                    amount = 0
                    rec.amount_from_conversion = 0
                    budget_line = self.env['crossovered.budget.lines'].search([('date_from','<=',rec.date),('date_to','>=',rec.date),('location_id','=',rec.location_id.id),
                                        ('analytic_activity_id','=',rec.activity_id.id),('analytic_account_id','=',rec.analytic_account_id.id),
                                        ('general_budget_id.account_ids','in', rec.account_id.id),])
                    print('_____________________budget line',budget_line)
                    if budget_line:
                        for line in budget_line:
                            currency_conversion = self.env['currency.conversion'].search([('date','<=',rec.date),('budget_id','=',line.crossovered_budget_id.id),('branch_id','=',rec.branch_id_line.id),('remain_amount','!=',0),('state','=','confirm')], order='date asc')                    
                            if currency_conversion:
                                for conversion in currency_conversion :
                                    amount_company_currency = conversion.remain_amount / conversion.rate
                                    if amount != fixed_deffernce:
                                        if changed_deffernce > amount_company_currency and conversion == currency_conversion.search([])[-1]:
                                            print('____________lesssss',changed_deffernce)
                                            raise ValidationError(_('Conversion is less than the Expensses you have to make currency conversion .'))
                                        if changed_deffernce >= amount_company_currency:
                                            print('amount',amount,'\n')
                                            changed_deffernce -= amount_company_currency
                                            conversion.remain_amount = 0
                                            amount += amount_company_currency 
                                            print('wfgegokehk;ekh',conversion.id)
                                            print('amount__________',amount,'\n')
                                            print('amount_from_conversion____________',rec.amount_from_conversion,'\n')
                                            rec.amount_from_conversion += amount_company_currency * conversion.rate
                                            print('amount_company_currency',amount_company_currency,'\n')
                                            print('deff00000000000000000000',changed_deffernce,'\n','\n', 'amount from conversin ',rec.amount_from_conversion,'\n','remain amount',conversion.remain_amount)
                                        
                                        if changed_deffernce < amount_company_currency:
                                            print('amount here_22222222222222_________',amount,'\n')
                                            rec.amount_from_conversion += changed_deffernce * conversion.rate
                                            amount += changed_deffernce 
                                            print('___________________________deffernce',changed_deffernce)
                                            print('___________________________amount_company_currency',amount_company_currency)
                                            changed_deffernce = amount_company_currency - changed_deffernce
                                            print('___________________________deffernce',changed_deffernce)
                                            conversion.remain_amount = changed_deffernce * conversion.rate
                                            
                                            print('amount here333333333333__________',amount,'\n')
                                            print('amount_from_conversion',rec.amount_from_conversion,'\n')
                                            print('deff00000000000000000000',changed_deffernce,'\n','\n','amount from conversin ',rec.amount_from_conversion,'\n','remain amount',conversion.remain_amount)

                            else:
                                raise ValidationError(_('You have to make currency conversion to cover Expensses.'))
                    else:
                        raise ValidationError(_('No budget line found for this move .'))

        return res
        
class SrcChartofAccount(models.Model):
    _inherit = "account.account" 

    account = fields.Boolean('Account') 
    project = fields.Boolean('Project') 
    activity = fields.Boolean('Activity')
    donor = fields.Boolean('Donor')
    location = fields.Boolean('Location')


class SrcBudgte(models.Model):
    _inherit = "crossovered.budget"

    currency_conversion_ids = fields.One2many('currency.conversion', 'budget_id', string='Currency Conversion')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Finance Officer'),
        ('finance_manager','Finance Manager '),
        ('cancel', 'Cancelled'),
        ('validate', 'Validated'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    budget_type = fields.Selection([
        ('core', 'Core'),('project','Project'),
    ],default='core', required=True, string='Budget Type')

    donor_id = fields.Many2one('res.partner', string='Donor')
    currency_id = fields.Many2one('res.currency', string='Currency')
    site = fields.Char('Site')
    situation = fields.Char('Situation')
    goal = fields.Char('Goal')
    project_id = fields.Many2one('account.analytic.account',string='Project', required=True, domain="[('type','=','project')]")
    site_boolean = fields.Boolean(related="donor_id.site")
    situation_boolean = fields.Boolean(related="donor_id.situation")
    goal_boolean = fields.Boolean(related="donor_id.goal")
    unit_of_measure_boolean = fields.Boolean(related="donor_id.unit_m")
    unit_cost_boolean = fields.Boolean(related="donor_id.unit_cost")
    frequency_boolean = fields.Boolean(related="donor_id.frequent")
    quantity_boolean = fields.Boolean(related="donor_id.quantity")
    conversion_count = fields.Float(compute="compute_conversion_count")

    def confirm_manager(self):
        self.state = 'finance_manager'

    def get_currnecy_conversion(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Currency Conversions'),
            'view_mode': 'tree,form',
            'res_model': 'currency.conversion',
            'domain': [('budget_id', '=', self.id)],
            'context': "{'create': False}"
        } 

    def compute_conversion_count(self):
        for record in self:
            record.conversion_count = self.env['currency.conversion'].search_count([('budget_id', '=', self.id)])

class SrcBudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    currency_budget_line = fields.Many2one('res.currency', related='crossovered_budget_id.currency_id')
    analytic_account_id = fields.Many2one('account.analytic.account',related="crossovered_budget_id.project_id")
    analytic_activity_id = fields.Many2one('account.analytic.account', 'Output/Activity')
    location_id = fields.Many2one('account.analytic.account', string='Location', domain="[('type','=','location')]")
    description = fields.Char(related='analytic_activity_id.description')
    unit_of_measure = fields.Many2one('uom.uom', string='UOM')
    quantity = fields.Float('Quantity')
    frequency = fields.Float('Frequency')
    unit_cost = fields.Float('Unit Cost')
    practical_amount_bu_currency = fields.Monetary(compute='_compute_practical_budget_currency', currency_field='currency_budget_line',string='Practical Amount(Budget Currency)')
    balance_SDG = fields.Monetary(compute='_compute_balance_SDG', string='Balance SDG',currency_field='currency_id')
    balance_budget_currency = fields.Monetary(compute='_compute_balance_budegt_currency', string='Balance budget currency',currency_field='currency_budget_line')
    total_budget = fields.Monetary(compute='_compute_total_budget', string='Total budget (Budget Currency)',currency_field='currency_budget_line',store=True, readonly=False)
    planned_amount = fields.Monetary(string='Total budget ',currency_field='currency_id',store=True)
    # rate = fields.Float(related='currency_budget_line.rate',digits=(12,6))
    
    
    @api.depends('unit_of_measure','quantity','frequency','unit_cost')
    def _compute_total_budget(self):
        for rec in self:
            if rec.unit_of_measure and rec.quantity and rec.frequency and rec.unit_cost:
                rec.total_budget = rec.quantity * rec.frequency * rec.unit_cost
                print('__________________________________________','\n',rec.currency_budget_line.rate)
    
    @api.onchange('total_budget','currency_budget_line')
    def _onchange_planned_amount(self):
        if self.currency_budget_line:
            if self.currency_budget_line == self.company_id.currency_id.id:
                print('__________________________________________','\n',self.currency_budget_line)
                self.planned_amount = self.total_budget
            else:
                self.planned_amount = self.total_budget / self.currency_budget_line.rate
                print('__________________________________________','\n',self.planned_amount)
        else:
            self.planned_amount = 0
            
    
    def _compute_practical_amount(self):
        res = super(SrcBudgetLine, self)._compute_practical_amount()
        for record in self:
            date_to = record.date_to
            date_from = record.date_from
            if record.analytic_account_id and record.analytic_activity_id and record.crossovered_budget_id.donor_id and record.location_id :
                aml_obj = self.env['account.move.line']
                domain = []
                
                for line in record.general_budget_id.account_ids:
                    if line.internal_group == 'expense': 
                   
                        domain = [('account_id', 'in',
                                record.general_budget_id.account_ids.ids),
                                ('date', '>=', date_from),
                                ('date', '<=', date_to),
                                ('move_id.state', '=', 'posted'),
                                ('analytic_account_id','=',record.analytic_account_id.id),
                                ('activity_id','=',record.analytic_activity_id.id),
                                ('location_id','=',record.location_id.id),
                                # ('partner_id','=',record.crossovered_budget_id.donor_id.id),
                                ]
                    # elif line.internal_group == 'income':
                    #     # aml_obj = self.env['account.move.line']
                    #     domain = [('account_id', 'in',
                    #             record.general_budget_id.account_ids.ids),
                    #             ('date', '>=', date_from),
                    #             ('date', '<=', date_to),
                    #             ('move_id.state', '=', 'posted'),
                    #             ('analytic_account_id','=',record.analytic_account_id.id),
                    #             ('activity_id','=',record.analytic_activity_id.id),
                    #             ('location_id','=',record.location_id.id),
                    #             ('partner_id','=',record.crossovered_budget_id.donor_id.id),
                    #             ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

                self.env.cr.execute(select, where_clause_params)
                record.practical_amount = self.env.cr.fetchone()[0] or 0.0
        print('========',record.practical_amount)
        return res
    
    def _compute_practical_budget_currency(self):
        for res in self:
            if res.practical_amount != 0:
                # if res.currency_budget_line != res.currency_id:
                date_to = res.date_to
                date_from = res.date_from
                # move_line = self.env['account.move.line'].search([('account_id', 'in',
                #     res.general_budget_id.account_ids.ids),
                #     ('date', '>=', date_from),
                #     ('date', '<=', date_to),
                #     ('move_id.state', '=', 'posted'),
                #     ('analytic_account_id','=',res.analytic_account_id.id),
                #     ('activity_id','=',res.analytic_activity_id.id),
                #     ('location_id','=',res.location_id.id),
                #     ('partner_id','=',res.crossovered_budget_id.donor_id.id),])

                move_line_exp = self.env['account.move.line'].search([('account_id', 'in',
                    res.general_budget_id.account_ids.ids),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('move_id.state', '=', 'posted'),
                    ('analytic_account_id','=',res.analytic_account_id.id),
                    ('activity_id','=',res.analytic_activity_id.id),
                    ('location_id','=',res.location_id.id),
                    # ('partner_id','=',res.crossovered_budget_id.donor_id.id),
                    ])
                amount = 0
                if move_line_exp:
                    for exp in move_line_exp:
                        # if res.general_budget_id.account_ids.internal_group == 'expense':                        
                        if exp.move_id.move_type == 'in_invoice':
                            amount += exp.amount_from_conversion
                            res.practical_amount_bu_currency = -(amount)
                            print('__________________________practical',res.practical_amount_bu_currency,exp.move_id.move_type)
                # if move_line:
                #     for line in move_line:
                #         # elif res.general_budget_id.account_ids.internal_group == 'income':
                #         if line.move_id.move_type == 'out_invoice':
                #             if line.currency_id == res.currency_budget_line:
                #                 res.practical_amount_bu_currency += abs(line.amount_currency)
                #                 print('+++++++++++++++++++++practical',res.practical_amount_bu_currency)
                        
                #             else:
                #                 currency_obj = self.env['res.currency.rate'].search([('currency_id','=',res.currency_budget_line.id),('name','=',line.date)])
                #                 for currency in currency_obj:
                #                     res.practical_amount_bu_currency += line.credit * currency.company_rate
                #                     print('___+++++++++++++++++practical',res.practical_amount_bu_currency)
                # else:
                #     res.practical_amount_bu_currency = 0
                else:
                    res.practical_amount_bu_currency = res.practical_amount
            else:
                res.practical_amount_bu_currency = 0
        
    @api.depends('practical_amount_bu_currency','total_budget')
    def _compute_balance_budegt_currency(self):
        for rec in self:
            rec.balance_budget_currency = rec.total_budget - rec.practical_amount_bu_currency    

    @api.depends('practical_amount','planned_amount')
    def _compute_balance_SDG(self):
        for rec in self:
            rec.balance_SDG = rec.planned_amount - rec.practical_amount
        
    def action_open_budget_entries(self):
        if self.analytic_account_id and self.analytic_activity_id and self.crossovered_budget_id.donor_id and self.location_id:
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
            action['domain'] = [('account_id', 'in',
                                    self.general_budget_id.account_ids.ids),
                                ('activity_id','=', self.analytic_activity_id.id),
                                ('location_id','=', self.location_id.id),
                                ('analytic_account_id','=', self.analytic_account_id.id),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to)
                                ]
        return action
           
class srcAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
   
    name = fields.Char('Name')
    description = fields.Char('Description')
    code = fields.Char('Code')
    type = fields.Selection([
        ('project', 'Project'),('activity','Activity'),('location','Location')
    ], string='Type')
    
    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            if analytic.group_id and analytic.group_id.parent_id:
                name = '%s / %s / %s' % (analytic.group_id.parent_id.name, analytic.group_id.name, analytic.name)
            elif analytic.group_id and not analytic.group_id.parent_id:
                name = '%s / %s ' % (analytic.group_id.name, analytic.name)
            elif not analytic.group_id:
                name = '%s' % (analytic.name)
            res.append((analytic.id,name))
            print('++++++++++',res[0])
        return res
    

class Donor(models.Model):    
    _inherit = "res.partner"

    donor_code = fields.Char('Donor Code')
    unit_m = fields.Boolean('Unit of Measure')
    quantity = fields.Boolean('Quantity')
    frequent = fields.Boolean('Frequency')
    unit_cost = fields.Boolean('unit cost')
    site = fields.Boolean('Site')
    situation = fields.Boolean('Situation')
    goal = fields.Boolean('Goal')


class SrcCurrency(models.Model):
    _inherit = 'res.currency'

    bank_id = fields.Many2one('res.bank', string='Bank')

class SrcAccountLine(models.Model):
    _inherit = "account.move.line"

    donor_bool = fields.Boolean(related="account_id.donor")
    activity_id = fields.Many2one('account.analytic.account', string='Activity',domain="[('type','=','activity')]")
    location_id = fields.Many2one('account.analytic.account', string='Location',domain="[('type','=','location')]")
    project = fields.Boolean(related="account_id.project")
    activity = fields.Boolean(related="account_id.activity")
    location = fields.Boolean(related="account_id.location")
    amount_from_conversion = fields.Float(default=0, string='Amount From Conversion')
    
                    
class Conversion(models.Model):
    _name = "currency.conversion"

    name = fields.Char(string='Name', required=True, default=lambda self: _('New'))
    source_bank = fields.Many2one('account.journal', string='Source Bank', required=True)
    dest_bank = fields.Many2one('account.journal', string='Destination Bank',required=True)
    budget_id = fields.Many2one('crossovered.budget', string='Budget')
    company_currency = fields.Many2one('res.currency', string='Currency', default= lambda self: self.env.company.currency_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency')
    date = fields.Date('Date', required=True)
    rate = fields.Float('Rate',related="currency_id.rate", digits=(12, 6), required=True)
    amount = fields.Monetary('Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),('confirm','confirmed')
    ],default="draft", string='status')
    internal_transfer_id = fields.Many2one('account.payment', string='Internal Transfer', readonly=True)
    remain_amount = fields.Monetary('Remain Amount')
    remain_amount_sdg = fields.Monetary('Remain Amount SDG', currency_field='company_currency')

    
    @api.onchange('budget_id')
    def _onchange_currency(self):
        for record in self:
            if record.budget_id:
                record.currency_id = record.budget_id.currency_id.id
            else:
                pass
        
    @api.onchange('amount')
    def _onchange_remain_amount(self):
        for rec in self:
            rec.remain_amount = rec.amount
            if rec.rate:
                rec.remain_amount_sdg = rec.amount / rec.rate
        
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('currency.conversion') or _('New')
        res = super(Conversion, self).create(vals)
        return res

    def confirm(self):
        for rec in self:
            if rec.currency_id:
                internal_transfer = self.env['account.payment'].create({
                    'is_internal_transfer':True,
                    'payment_type':'outbound',
                    'type_internal_transfer':'inernal',
                    'journal_id':rec.source_bank.id,
                    'destination_journal_id':rec.dest_bank.id,
                    'amount':rec.amount,
                    'date':rec.date,
                    'currency_id':rec.currency_id.id,
                    'ref':rec.name,
                })
                print("++++++++++++++++++++++++",internal_transfer)
                rec.internal_transfer_id = internal_transfer.id
                rec.state = "confirm"


class SrcsPayment(models.Model):
    _inherit = "account.payment"

    project_id = fields.Many2one('account.analytic.account',string="Project", domain="[('type','=','project')]")
    type_internal_transfer = fields.Selection([
        ('inernal', 'Internal Transfer'),
        ('branch', 'Transfer To Branch'),
    ], default='inernal', string='Internal Transfer Type')
    
    # Modify internal transfer receipt payment be in draft state not posted in case send to branch
    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        res = super(SrcsPayment, self)._create_paired_internal_transfer_payment()
        for payment in self:
            if payment.type_internal_transfer == 'branch':
                print('_____________________________branch',payment.type_internal_transfer)
                paired_payment = payment.copy({
                    'journal_id': payment.destination_journal_id.id,
                    'destination_journal_id': payment.journal_id.id,
                    'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                    'move_id': None,
                    'ref': payment.ref,
                    'paired_internal_transfer_payment_id': payment.id
                })
                payment.paired_internal_transfer_payment_id = paired_payment

                body = _('This payment has been created from <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (payment.id, payment.name)
                paired_payment.message_post(body=body)
                body = _('A second payment has been created: <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (paired_payment.id, paired_payment.name)
                payment.message_post(body=body)

                lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                    lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
        return res

    # # Modify indirecting account to be direct
    # def _prepare_move_line_default_vals(self, write_off_line_vals=None):
    #     res = super(SrcsPayment, self)._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
    #     res[0].update({'account_id': self.journal_id.default_account_id.id})
    #     print('__________________res account',res[0],'\n',res[1],'\n',res)
    #     return res

    