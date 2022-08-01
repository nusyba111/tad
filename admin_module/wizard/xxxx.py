# import datetime
#
# year = 2016
# first_day_of_year = datetime.date.min.replace(year=year)
# last_day_of_year = datetime.date.max.replace(year=year)
# print(first_day_of_year, last_day_of_year)

# import calendar
# from datetime import datetime
#
# from dateutil.relativedelta import relativedelta
#
# from odoo import fields
# from datetime import datetime
#
# date_start_val = '2015-07-01'  # start date (inclusive)
# date_end_val = '2015-10-1'  # end date (inclusive)
#
# date_start = datetime.strptime(date_start_val, '%Y-%m-%d').date()
# date_end = datetime.strptime(date_end_val, '%Y-%m-%d').date()
#
# # a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# num_months = (date_end.year - date_start.year) * 12 + (date_end.month - date_start.month) * 30 + (
#         date_end.month - date_start.month)
# print('num of months', num_months)
# i = 0
# col = 0
# while i != num_months + 1:
#     date = date_start + relativedelta(months=i)
#     month_no = str(date.strftime("%m"))
#     col += 1
#     i += 1
#
#     print('month no', month_no)
#     month_name = calendar.month_name[int(month_no)]
#     print('month name', month_name)

#
# import datetime
# import numpy as np
#
# start = datetime.date(2022, 3, 1)
# end = datetime.date(2022, 3, 31)
#
# days = np.busday_count(start, end)
# print('Number of business days is:', days)

from datetime import date, timedelta

start = date(2022, 3, 1)
end = date(2022, 3, 31)

# get list of all days
all_days = (start + timedelta(x + 1) for x in range((end - start).days))

# filter business days
# weekday from 0 to 4. 0 is monday adn 4 is friday
# increase counter in each iteration if it is a weekday
count = sum(1 for day in all_days if day.weekday() < 6)
print('Number of business days is:', count)
