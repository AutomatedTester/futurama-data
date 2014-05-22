import datetime
from datetime import timedelta
import re

from flask import render_template, request
from app import app
import requests

HISTORIC = {
    "mozilla-inbound": {
        "total": [1193, 997, 1043, 1126, 1202, 1060],
        "backouts": [174, 147, 162, 186, 180, 189]
    },
    "mozilla-central": {
        "total": [],
        "backouts": []
    },
    "fx-team": {
        "total": [403, 357, 542, 584, 628, 464],
        "backouts": [81, 60, 93, 110, 95, 60]
    }
}

@app.route('/')
@app.route('/index')
def index():
    tree = request.args.get('tree', 'mozilla-inbound')
    closure_months, closure_dates = main(tree)
    x = []
    y = {'no reason': [],
         'checkin-test': [],
         'checkin-compilation': [],
         'infra': [],
         'other': [],
         'planned': [],
         'backlog': [],
         'checkin-test': []}

    c_data = [(datetime.datetime.strptime(k, "%Y-%m"), closure_months[k]) for k in sorted(closure_months.keys())[-12:]]
    x = ["%s-%s" % (date.year, date.month if date.month > 9 else "0%s" % date.month) for (date, value) in c_data]
    for data in c_data:
        # We need to make a sparse array so we can have the 2 arrays the same length when plotting
        not_filled = [k for k in y.keys() if k not in data[1].keys()]
        for nf in not_filled:
            y[nf].append(0)
        #show me the data
        for _x in data[1].keys():
            y[_x].append(data[1][_x].total_seconds() / 3600)

    wek = datetime.datetime.now() - timedelta(7)
    week = "%s-%s-%s" % (wek.year,
        wek.month if wek.month > 9 else "0%s" % wek.month,
        wek.day if wek.day > 9 else "0%s" % wek.day)
    backouts_since_week = backouts(tree, week)
    tody = datetime.datetime.now()

    backed = 0
    today_pushes = 0
    backoutln = re.compile('^.*[b,B]ackout.*')
    backoutln2 = re.compile('^.*[b,B]acked out.*')
    backoutln3 = re.compile('^.*[b,B]ack out.*')
    for resp in backouts_since_week['pushes']:

        if (datetime.date.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])) == datetime.date.today()):
            today_pushes += 1
            for chnge in range(len(backouts_since_week['pushes'][resp]['changesets'])):
                if (backoutln.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc']) or
                    backoutln2.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc']) or
                    backoutln3.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc'])):

                    if (datetime.date.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])) == datetime.date.today()):
                        backed += 1
                        break

    today = "%s-%s-%s" % (tody.year,
        tody.month if tody.month > 9 else "0%s" % tody.month,
        tody.day if tody.day > 9 else "0%s" % tody.day)

    # Temporary hack until I can get data from a proper source
    temp_list = x[-7:]
    HISTORIC[tree]["dates"] = temp_list[0:6]

    HISTORIC[tree]["ratio"] = [float(HISTORIC[tree]["backouts"][it])/float(HISTORIC[tree]["total"][it]) * 100 for it in xrange(len(HISTORIC[tree]["total"]))]
    return render_template("index.html", total={"x": x, "y": y},
        backouts=backouts_since_week, today={"total": today_pushes, "backouts": backed, "search_date": today},
        tree=tree, historic=HISTORIC[tree])



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

    return month, dates

def backouts(tree, search_date):
    total_pushes = requests.get("https://hg.mozilla.org/%s/json-pushes?full=1&startdate=%s" %
        ("integration/%s" % tree if tree != "mozilla-central" else tree, search_date)).json()
    backed = 0
    backoutln = re.compile('^.*[b,B]ackout.*')
    backoutln2 = re.compile('^.*[b,B]acked out.*')
    backoutln3 = re.compile('^.*[b,B]ack out.*')
    merges = re.compile('^.*[M,m]erge .* to .*')
    keys_to_pop = []
    for resp in total_pushes:
        for chnge in range(len(total_pushes[resp]['changesets'])):
            if merges.match(total_pushes[resp]['changesets'][chnge]['desc']):
                keys_to_pop.append(resp)

    for key in keys_to_pop:
        total_pushes.pop(key, None)

    for resp in total_pushes:
        for chnge in range(len(total_pushes[resp]['changesets'])):
            if (backoutln.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln2.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln3.match(total_pushes[resp]['changesets'][chnge]['desc'])):
                backed += 1
                break


    return {"total": len(total_pushes),
            "backouts": backed,
            "startdate": search_date,
            "pushes": total_pushes}
