from dateutil.relativedelta import relativedelta
from datetime import datetime , time , timedelta
import calendar

def add_months(sourcedate,months):
     sourcedate = datetime.strptime(sourcedate, '%Y-%m-%d')
     month = sourcedate.month - 1 + months
     year = sourcedate.year + month // 12
     month = month % 12 + 1
     day = min(sourcedate.day,calendar.monthrange(year,month)[1])
     return datetime(year,month,day)

    
def is_first_year(fiscal_year , doj, probation_period ):
    
    today = datetime.now().date()
    fiscal_year = datetime.strptime(fiscal_year , '%b %m, %Y')
    perminent_date = (add_months(doj , probation_period)).date()
    sofy = (fiscal_year - relativedelta(years=1)).date()
    dsofy = abs((today-sofy).days)
    dsope = abs((today - perminent_date).days)
    return 1 if dsofy > dsope else 0


