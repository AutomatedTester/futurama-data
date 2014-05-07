import datetime
from datetime import timedelta
import re

from flask import render_template
from app import app
import requests

#import treestatus_stats

@app.route('/')
@app.route('/index')
def index():
    closure_months, closure_dates = main("mozilla-inbound")
    x = []
    y = {'no reason': [],
         'checkin-test': [],
         'checkin-compilation': [],
         'infra': [],
         'other': [],
         'planned': [],
         'backlog': [],
         'checkin-test': []}

    c_data = [(datetime.datetime.strptime(k, "%Y-%m"), closure_months[k]) for k in sorted(closure_months.keys())]
    x = ["%s-%s" % (date.year, date.month if date.month > 9 else "0%s" % date.month) for (date, value) in c_data]
    print x
    for data in c_data:
        # We need to make a sparse array so we can have the 2 arrays the same length when plotting
        not_filled = [k for k in y.keys() if k not in data[1].keys()]
        for nf in not_filled:
            y[nf].append(0)
        #show me the data
        for _x in data[1].keys():
            y[_x].append(data[1][_x].total_seconds() / 3600)

    yesday = datetime.datetime.now() - timedelta(1)
    yesterday = "%s-%s-%s" % (yesday.year, yesday.month if yesday.month > 9 else "0%s" % yesday.month, yesday.day if yesday.day > 9 else "0%s" % yesday.day)
    backouts_since_yesterday = backouts(yesterday)
    tody = datetime.datetime.now()
    today = "%s-%s-%s" % (tody.year, tody.month if tody.month > 9 else "0%s" % tody.month, tody.day if tody.day > 9 else "0%s" % tody.day)
    backouts_today = backouts(today)

    return render_template("index.html", total={"x": x, "y": y}, backouts=backouts_since_yesterday, today=backouts_today)



def main(tree):
    response = requests.get('https://treestatus.mozilla.org/%s/logs?format=json&all=1' % tree, verify=False)
    results = response.json()
    delta = datetime.timedelta(0)
    closed = None
    closed_reason = None
    dates = {}
    month = {}

    Added = None
    for item in reversed(results['logs']):
        if item['action'] == 'closed':
            if closed is not None:
                continue
            closed = datetime.datetime.strptime(item['when'], "%Y-%m-%dT%H:%M:%S")
            closed_reason = item['tags'][0] if len(item['tags']) > 0 else 'no reason'
        elif item['action'] == 'open' or item['action'] == 'approval require':
            if closed is None:
                continue
            opened = datetime.datetime.strptime(item['when'], "%Y-%m-%dT%H:%M:%S")
            delta = opened - closed

            if closed.date().isoformat() in dates:
                try:
                    dates[closed.date().isoformat()][closed_reason] = dates[closed.date().isoformat()][closed_reason] + delta
                except:
                    dates[closed.date().isoformat()][closed_reason] = delta
            else:
                dates[closed.date().isoformat()] = {closed_reason: delta}

            year_month = "%s-%s" % (closed.date().year, closed.date().month if closed.date().month >= 10 else '0%s' % closed.date().month)

            if year_month not in ['2012-06', '2012-07']:
                if year_month in month:
                    try:
                        month[year_month][closed_reason] = month[year_month][closed_reason] + delta
                    except:
                        month[year_month][closed_reason] = delta
                else:
                    month[year_month] = { closed_reason: delta}

            closed = None
            closed_reason = None
        elif item['action'] == 'added':
            Added = item['when']
            print "Added on :%s" % item['when']

    return month, dates

def backouts(search_date):
    total_pushes = requests.get("https://hg.mozilla.org/integration/mozilla-inbound/json-pushes?full=1&startdate=%s" % search_date).json()
    backed = 0
    backoutln = re.compile('^.*[b,B]ackout.*')
    backoutln2 = re.compile('^.*[b,B]acked out.*')
    backoutln3 = re.compile('^.*[b,B]ack out.*')
    for resp in total_pushes:
        for chnge in range(len(total_pushes[resp]['changesets'])):
            if (backoutln.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln2.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln3.match(total_pushes[resp]['changesets'][chnge]['desc'])):
                backed += 1


    return {"total": len(total_pushes), "backouts": backed, "startdate": search_date}
