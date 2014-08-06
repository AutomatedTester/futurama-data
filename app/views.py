import datetime
from datetime import timedelta
import re

from flask import render_template, request
from app import app
import requests


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    tree = request.args.get('tree', 'mozilla-inbound')
    closure_months, closure_dates, status, status_reason = main(tree)
    uptime = get_uptime_stats(closure_months)
    x, y = graph_data_for_uptime(closure_months)


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
    backout_hours = [0] * 24
    pushes_hours = [0] * 24

    #if backouts_since_week
    for resp in backouts_since_week['pushes']:
        if (datetime.date.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])) == datetime.date.today()):
            today_pushes += 1
            bhour = datetime.datetime.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])).hour
            pushes_hours[bhour] = pushes_hours[bhour] + 1
            for chnge in range(len(backouts_since_week['pushes'][resp]['changesets'])):
                if (backoutln.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc']) or
                    backoutln2.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc']) or
                    backoutln3.match(backouts_since_week['pushes'][resp]['changesets'][chnge]['desc'])):

                    if (datetime.date.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])) == datetime.date.today()):
                        backed += 1

                        # Lets also track what hour the backouts happened in
                        bhour = datetime.datetime.fromtimestamp(int(backouts_since_week['pushes'][resp]['date'])).hour
                        backout_hours[bhour] = backout_hours[bhour] + 1
                        break

    today = "%s-%s-%s" % (tody.year,
        tody.month if tody.month > 9 else "0%s" % tody.month,
        tody.day if tody.day > 9 else "0%s" % tody.day)

    return render_template("index.html", total={"x": x, "y": y}, backout_hours=backout_hours, pushes_hours=pushes_hours,
        backouts=backouts_since_week, today={"total": today_pushes, "backouts": backed, "search_date": today},
        tree=tree, status={"status": status, "status_reason":status_reason}, uptime=uptime)


def main(tree):
    response = requests.get('https://treestatus.mozilla.org/%s/logs?format=json&all=1' % tree, verify=False)
    results = response.json()
    delta = datetime.timedelta(0)
    closed = None
    closed_reason = None
    dates = {}
    month = {}
    total = datetime.timedelta(0)
    Added = None
    status = results['logs'][0]['action']
    status_reason = results['logs'][0]['reason']
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
                    dates[closed.date().isoformat()]['total'] = dates[closed.date().isoformat()]['total'] + delta
                    dates[closed.date().isoformat()][closed_reason] = dates[closed.date().isoformat()][closed_reason] + delta
                except:
                    dates[closed.date().isoformat()][closed_reason] = delta
            else:
                dates[closed.date().isoformat()] = {'total': delta, closed_reason: delta}

            year_month = "%s-%s" % (closed.date().year, closed.date().month if closed.date().month >= 10 else '0%s' % closed.date().month)

            if year_month not in ['2012-06', '2012-07']:
                if year_month in month:
                    month[year_month]['total'] = month[year_month]['total'] + delta
                    try:
                        month[year_month][closed_reason] = month[year_month][closed_reason] + delta
                    except:
                        month[year_month][closed_reason] = delta
                else:
                    month[year_month] = {'total': delta, closed_reason: delta}

                total += delta

            closed = None
            closed_reason = None
        elif item['action'] == 'added':
            Added = item['when']

    return month, dates, status, status_reason

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

    backout_hours = [0] * 24
    pushes_hours = [0] * 24

    for resp in total_pushes:
        # Lets also track what hour the push happened in
        bhour = datetime.datetime.fromtimestamp(int(total_pushes[resp]['date'])).hour
        pushes_hours[bhour] = pushes_hours[bhour] + 1
        for chnge in range(len(total_pushes[resp]['changesets'])):
            if (backoutln.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln2.match(total_pushes[resp]['changesets'][chnge]['desc']) or
                backoutln3.match(total_pushes[resp]['changesets'][chnge]['desc'])):
                backed += 1

                # Lets also track what hour the backouts happened in
                bhour = datetime.datetime.fromtimestamp(int(total_pushes[resp]['date'])).hour
                backout_hours[bhour] = backout_hours[bhour] + 1
                break

    return {"total": len(total_pushes),
            "backouts": backed,
            "startdate": search_date,
            "pushes": total_pushes,
            "backoutHours": backout_hours,
            "pushesHours": pushes_hours}

def get_uptime_stats(closure_months):
    from calendar import monthrange
    days_in_month = [monthrange(*[ int(y) for y in x.split('-')])[1] for x in sorted(closure_months.keys())[-12:]]
    total_hours = [closure_months[x]['total'].total_seconds() for x in sorted(closure_months.keys())[-12:]]
    count = 0
    result = []
    for days in days_in_month:
        total_secs = days * 24 * 60 * 60
        result.append(100 - ((total_hours[count]/total_secs) * 100))
        count = count + 1

    return result

def graph_data_for_uptime(closure_months):
    x = []
    y = {'no reason': [],
         'checkin-test': [],
         'checkin-compilation': [],
         'infra': [],
         'other': [],
         'planned': [],
         'backlog': [],
         'checkin-test': [],
         'total': []}

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

    return x, y
