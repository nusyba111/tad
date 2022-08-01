# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CleanTools(models.Model):
    _name = 'clean.tools'
    _description = 'cleaning tools'
    _rec_name = 'tool'

    tool = fields.Char(string='Tool')
    # clean_id=fields.Char(string='')


class MealItem(models.Model):
    _name = 'meal.item'
    _description = 'meal item'
    _rec_name = 'meal_item'

    meal_item = fields.Char(string='Meal Item')


class HallName(models.Model):
    _name = 'hall.name'
    _rec_name = 'hall_name'

    hall_name = fields.Char(string='hall name')


class DestinationName(models.Model):
    _name = 'destination.name'
    _rec_name = 'destination_name'

    destination_name = fields.Char(string='From')


class TransportLine(models.Model):
    _name = 'line.name'
    _rec_name = 'name'

    name = fields.Char(string='line name')


class CarStatus(models.Model):
    _name = 'car.status'
    _rec_name = 'absent_reasons'

    absent_reasons = fields.Char(string='absent reasons')


class LoanReasons(models.Model):
    _name = 'loan.reasons'
    _rec_name = 'loan_reasons'

    loan_reasons = fields.Char(string='loan reasons')
