from datetime import datetime , time

import calendar

def add_months(sourcedate,months):
     month = sourcedate.month - 1 + months
     year = sourcedate.year + month // 12
     month = month % 12 + 1
     day = min(sourcedate.day,calendar.monthrange(year,month)[1])
     return datetime.date(year,month,day)


def update_general_leaves(date_of_joining, last_updated ,leaves_remaining ,probation_period, user , leaves_limit , leaves_availed):
	
	current_time = datetime.today()
	if (probation_period == 1):
		return leaves_remaining
	if last_updated == date_of_joining:
		date_for_calculation = add_months(date_of_joining,probation_period)
	else:
		date_for_calculation = last_updated


	days = (current_time - date_for_calculation).days

	days_in_year = 366 if calendar.isleap(current_time.year) else 365
	leaves_per_day = leaves_limit / days_in_year
	leaves_remaining = (days*leaves_per_day) + leaves_remaining

	return leaves_remaining






















