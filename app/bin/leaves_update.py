from datetime import datetime , time
from __future__ import division
import calendar

def add_months(sourcedate,months):
     month = sourcedate.month - 1 + months
     year = sourcedate.year + month // 12
     month = month % 12 + 1
     day = min(sourcedate.day,calendar.monthrange(year,month)[1])
     return datetime(year,month,day)


def update_general_leaves(date_of_joining ,leaves_remaining, first_year, fiscal_year,
                            probation_period, user , leaves_limit , leaves_availed,
                         probation_leaves_limit , current_time=None):
    if current_time == None:
        current_time = datetime.today()
        
    probation_ending_period = add_months(date_of_joining,probation_period)
    days_in_probation = (probation_ending_period - date_of_joining).days
    time_since_probation = (current_time - probation_ending_period).days
        
    if first_year:
        
        if (probation_ending_period >= current_time):
            print(time_since_probation)
            return leaves_remaining
            ##update in database
        elif current_time  <  fiscal_year :
            #IS not on probation 
            # Assumption first year rule applies from end of probation to start of new fisca year        
            days_in_year = 366 if calendar.isleap(fiscal_year.year) else 365
            remaining_days = days_in_year - days_in_probation
            leaves_per_day = (leaves_limit-probation_leaves_limit)/ remaining_days
            leaves_remaining = ((time_since_probation * leaves_per_day) + leaves_remaining) - leaves_availed
            print (time_since_probation)
            return leaves_remaining

    else:
        days =( current_time - fiscal_year).days 
        days_in_year = 366 if calendar.isleap(fiscal_year.year) else 365
        leaves_per_day = leaves_limit / days_in_year
        leaves_remaining = (days*leaves_per_day) + leaves_remaining
        return leaves_remaining



    return leaves_remaining

