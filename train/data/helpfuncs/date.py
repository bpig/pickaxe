import datetime

def strtodatetime(datestr,format="%Y%m%d"):
    return datetime.datetime.strptime(datestr,format)

def datetostr(date):
    return date.strftime('%Y%m%d')

def datediff(beginDate,endDate,format="%Y%m%d"):
    bd=strtodatetime(beginDate,format)
    ed=strtodatetime(endDate,format)
    delta = ed - bd
    return delta.days
