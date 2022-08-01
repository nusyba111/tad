import datetime
from datetime import datetime, date

months = (
    None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
    'December')
for y in range(1, 13):
    m = months[y]  #
    print(m)


# from odoo import fields
#
# start_year = fields.Date()
#
#
# # @api.model
# def year_selection(self):
#     year = start_year  # replace 2000 with your a start year
#     year_list = []
#     while year != 2030:  # replace 2030 with your end year
#         year_list.append((str(year), str(year)))
#         print(year_list, 'year_list')
#         year += 1
#     return year_list
#
#
# year = fields.Selection(
#     'year_selection',
#     string="Year",
#     default="2019",  # as a default value it would be 2019
# )
# print(year, year)
#
# #
# # def _get_year(self, cr, uid, ids, name, arg, context=None):
# #     values = self.read(cr, uid, ids, ['date'], context)
# #     res = dict(map(lambda x: (x['id'], x['date'] and x['date'][0:4] or False), values))
# #
# #     return res
# #
# #
# # _columns = {
# #     'year': fields.function(_get_year, type='char', readonly=True, string='Year'),
# #     'date': fields.date('Date'),
# # }
#
# # date_start_val = '2015-09-01'  # start date (inclusive)
# # date_start = datetime.strptime(date_start_val, '%Y-%m-%d').date()
# # # today = datetime.datetime.now()
# # thisYear = date_start.year
# # print(thisYear)
# # fday = thisYear.replace(day=1)
# # firstDay = datetime.datetime(thisYear, 1, 1)
# # firstDayStr = firstDay.strftime('%Y')
# # print(firstDayStr)
#
#
# # import calendar
# # from datetime import datetime
# #
# # from dateutil.relativedelta import relativedelta
# #
# # from odoo import fields
# # from datetime import datetime
# #
# # date_start_val = '2015-09-01'  # start date (inclusive)
# # date_end_val = '2017-10-1'  # end date (inclusive)
# #
# # date_start = datetime.strptime(date_start_val, '%Y-%m-%d').date()
# # date_end = datetime.strptime(date_end_val, '%Y-%m-%d').date()
# #
# # print(date_end.year)
# # # from_date = data['from_date']
# # date_start = fields.Date(string='From Date', )
# # date_end = fields.Date(string='To Date', )
#
# # start = datetime.strptime(date_start, '%Y-%m-%d')
# # end = datetime.strptime(date_end, '%Y-%m-%d')
# #
# # days = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
# # total_days = (date_end.day - date_start.day) + 1
# # first_weekday = date_start.weekday()
# # print('ssssssssssssssssssss', first_weekday)
# # day1 = days['fri']
# # day2 = days['sat']
# # target_weekday = days['fri']
# # if target_weekday == first_weekday:
# #     days_before = 0
# # elif target_weekday < first_weekday:
# #     days_before = 7 - first_weekday + target_weekday
# #     print('ddddddddddddddddddddd', days_before)
# # else:
# #     days_before = target_weekday - first_weekday
# #
# # weekday_count = total_days - days_before
# # if weekday_count > 0:
# #     weekday_count = weekday_count / 7 + (weekday_count % 7 and 1 or 0)
# # else:
# #     weekday_count = 0
# # day_count = total_days - weekday_count
# # print('vvvvvvvvvvvvvvvvvvvv', day_count)
# # # for rec in day_count:
# #     print(',,,,,,,,,,,,,,,,,,,,,,,,', rec)
#
# # a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# # # num_months = (date_end.year - date_start.year) * 12 + (
# # #         date_end.month - date_start.month)
# # num_days = (date_end.year - date_start.year) * 12 + (date_end.month - date_start.month) * 30 + (
# #         date_end.day - date_start.day)
# # print('num of months', num_days)
# # i = 0
# # col = 0
# # while i != num_days + 1:
# #     date = date_start + relativedelta(days=i)
# #     day_no = str(date.strftime("%d"))
# #     col += 1
# #     i += 1
# #
# #     print('day no', day_no)
# # month_name = calendar.month_name[int(month_no)]
# # print('month name', month_name)
# ################################################
# # num_years = (date_end.year - date_start.year)
# # print('num of years', num_years)
# # date = date_start + relativedelta(years=1)
# # day_no = str(date.strftime("%Y"))
# # print('day no', day_no)
# # i = 0
# # while i != num_years + 1:
#
# # i += 1
