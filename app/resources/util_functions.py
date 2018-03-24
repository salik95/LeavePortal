from dateutil.relativedelta import relativedelta
from datetime import datetime , time , timedelta
import calendar

def add_months(sourcedate,months):
     month = sourcedate.month - 1 + months
     year = sourcedate.year + month // 12
     month = month % 12 + 1
     day = min(sourcedate.day,calendar.monthrange(year,month)[1])
     return datetime(year,month,day)

    
def is_first_year(fiscal_year , doj, probation_period ):
    
    today = datetime.now().date()
    doj  = datetime.strptime(doj , '%Y-%m-%d')
    fiscal_year = datetime.strptime(fiscal_year , '%Y-%m-%d')
    perminent_date = (add_months(doj , probation_period)).date()
    sofy = (fiscal_year - relativedelta(years=1)).date()
    dsofy = abs((today-sofy).days)
    dsope = abs((today - perminent_date).days)
    return 1 if dsofy > dsope else 0



'''
is_first_year(today=datetime(2018,7,1) ,\
                 fiscal_year=datetime(2018,7,1) ,\
                  doj=datetime(2018,5,1) ,\
                   probation_period=3 )'''