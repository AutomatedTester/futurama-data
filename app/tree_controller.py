import datetime
import re

import requests
import bugsy


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

def backouts(tree, search_date):
    if tree.startswith('comm-'):
        return None
    total_pushes = requests.get("https://hg.mozilla.org/%s/json-pushes?full=1&startdate=%s" %
        ("integration/%s" % tree if tree != "mozilla-central" else tree, search_date), verify=True).json()
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

def calculate_closures(tree):
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
            if closed:
                # if closed the tag may have changed so let's pretend it was opened and then closed
                import copy
                opened = copy.copy(closed)
                closed = datetime.datetime.strptime(item['when'], "%Y-%m-%dT%H:%M:%S")
                closed_reason = item['tags'][0] if len(item['tags']) > 0 else 'no reason'
                delta = closed - opened

                dates = update_dates(closed, closed_reason, dates)

                year_month = "%s-%s" % (closed.date().year, closed.date().month if closed.date().month >= 10 else '0%s' % closed.date().month)

                month, delta = populate_month(year_month, month, delta, closed_reason, total)

                opened = None
            else:
                closed = datetime.datetime.strptime(item['when'], "%Y-%m-%dT%H:%M:%S")
                closed_reason = item['tags'][0] if len(item['tags']) > 0 else 'no reason'

        elif item['action'] == 'open' or item['action'] == 'approval required':
            if not closed:
                continue
            opened = datetime.datetime.strptime(item['when'], "%Y-%m-%dT%H:%M:%S")
            delta = opened - closed


            dates = update_dates(closed, closed_reason, dates)

            year_month = "%s-%s" % (closed.date().year, closed.date().month if closed.date().month >= 10 else '0%s' % closed.date().month)

            month, delta = populate_month(year_month, month, delta, closed_reason, total)

            closed = None
            closed_reason = None
        elif item['action'] == 'added':
            Added = item['when']
    print ("Total is %s" % total)
    return month, dates, status, status_reason

def populate_month(year_month, month, delta, closed_reason, total):
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

    return month, delta

def update_dates(closed_date, closed_reason, dates):
    delta = datetime.timedelta(0)
    if closed_date.date().isoformat() in dates:
        try:
            dates[closed_date.date().isoformat()]['total'] = dates[closed_date.date().isoformat()]['total'] + delta
            dates[closed_date.date().isoformat()][closed_reason] = dates[closed_date.date().isoformat()][closed_reason] + delta
        except:
            dates[closed_date.date().isoformat()][closed_reason] = delta
    else:
        dates[closed_date.date().isoformat()] = {'total': delta, closed_reason: delta}
    return dates


def intermittent_opened_count_last_week():
    tday = datetime.date.today()
    tday_minus_7 = tday - datetime.timedelta(days=7)
    today = '%s-%s-%s' %(tday.year, tday.month if tday.month >= 10 else '0%s' % tday.month, tday.day)
    seven_days_ago = '%s-%s-%s' %(tday_minus_7.year, tday_minus_7.month if tday_minus_7.month >= 10 else '0%s' % tday_minus_7.month, tday_minus_7.day)
    bugzilla = bugsy.Bugsy()
    bugs = bugzilla.search_for\
                   .keywords("intermittent-failure")\
                   .change_history_fields(['[Bug creation]'])\
                   .timeframe(seven_days_ago, today)\
                   .search()

    for bug in bugs:
        if bug.product == 'Thunderbird':
            bugs.remove(bug)
    return len(bugs)

def _intermittent_bugs(seven_days_ago, today):
    bugzilla = bugsy.Bugsy()
    return bugzilla.search_for\
                   .keywords("intermittent-failure")\
                   .change_history_fields(['bug_status'], 'Resolved')\
                   .timeframe(seven_days_ago, today)\
                   .search()

def _seven_days_ago():
    tday = datetime.date.today()
    tday_minus_7 = tday - datetime.timedelta(days=7)
    today = '%s-%s-%s' %(tday.year, tday.month if tday.month >= 10 else '0%s' % tday.month, tday.day)
    seven_days_ago = '%s-%s-%s' %(tday_minus_7.year, tday_minus_7.month if tday_minus_7.month >= 10 else '0%s' % tday_minus_7.month, tday_minus_7.day)

    return seven_days_ago, today

def intermittents_closed_breakdown():

    seven_days_ago, today = _seven_days_ago()

    bugs = _intermittent_bugs(seven_days_ago, today)

    result= {}
    for bug in bugs:
        reason = ''
        if bug.resolution == '':
            reason = 'REOPENED'
        else:
            reason = bug.resolution

        try:
            result[reason] = result[bug.resolution] + 1
        except:
            result[reason] = 1

    return result

def intermittent_count_closed_last_week():

    seven_days_ago, today = _seven_days_ago()

    bugs = _intermittent_bugs(seven_days_ago, today)

    for bug in bugs:
        if bug.product == 'Thunderbird' or bug.resolution == '':
            bugs.remove(bug)

    return len(bugs)

def checkin_needed_count():
    bugzilla = bugsy.Bugsy()
    bugs = bugzilla.search_for\
                   .keywords("checkin-needed")\
                   .search()

    return len(bugs)

def backouts_list(tree, search_date):
    # Get the pushlog as a json blob
    pushlog = requests.get("https://hg.mozilla.org/%s/json-pushes?full=1&startdate=%s" %
        ("integration/%s" % tree if tree != "mozilla-central" else tree, search_date)).json()

    backed = 0

    backouts_list = {}
    backouts_list = createBackoutList(backouts_list)

    # Remove 'merge' changesets from the pushlog
    pushlog = purgeMerges(pushlog)
    backouts_list = getBackouts(backouts_list, pushlog)

    return {"total": len(pushlog),
            "backouts_list": backouts_list,
            "startdate": search_date}

# Iterate through a pushlog and remove any 'merge' changesets
def purgeMerges(aPushlog):
	keys_to_pop = []
	regex = re.compile('^.*[M,m]erge .* to .*')

	for p in aPushlog:
		for c in range(len(aPushlog[p]['changesets'])):
			if regex.match(aPushlog[p]['changesets'][c]['desc']):
				keys_to_pop.append(p)

	for key in keys_to_pop:
		aPushlog.pop(key, None)

	return aPushlog

def createBackoutList(aBackouts):
	# List of possible folders from hg.mozilla.org/mozilla-central
	# [this should be dynamically generated in the future]
	folders = ["accessibile",
			   "addon-sdk",
			   "b2g",
			   "browser",
			   "build",
			   "caps",
			   "chrome",
			   "config",
			   "content",
			   "db sqlite3",
			   "docshell",
			   "dom",
			   "editor",
               "embedding",
               "extensions",
               "gfx",
               "hal",
               "image",
               "intl",
               "ipc",
               "js",
               "layout",
               "media",
               "memory",
               "mfbt",
               "mobile",
               "modules",
               "mozglue",
               "netwerk",
               "nsprpub",
               "other-licenses",
               "parser",
               "probes",
               "profile",
               "python",
               "rdf",
               "security",
               "services",
               "startupcache",
               "storage",
               "testing",
               "toolkit",
               "tools",
               "uriloader",
               "view",
               "webapprt",
               "widget",
               "xpcom",
               "xpfe",
               "xulrunner"]

	for f in folders:
		aBackouts[f] = 0

	return aBackouts

def getBackouts(aBackouts, aPushlog):
	regex = [re.compile('^.*[b,B]ackout.*'),
             re.compile('^.*[b,B]acked out.*'),
             re.compile('^.*[b,B]ack out.*')]

	for p in aPushlog: # p represents one push in the pushlog
		for c in range(len(aPushlog[p]['changesets'])):
			if (regex[0].match(aPushlog[p]['changesets'][c]['desc']) or
                regex[1].match(aPushlog[p]['changesets'][c]['desc']) or
                regex[2].match(aPushlog[p]['changesets'][c]['desc'])):

				aBackouts = countBackoutsByFolder(aBackouts, aPushlog[p]['changesets'][c])

	return aBackouts

def countBackoutsByFolder(aBackouts, aChangeset):
	# Iterate through each file indicated in the backout
	for f in range(len(aChangeset['files'])):
		for k in aBackouts.keys():
			regex = re.compile('^' + k + '.*')
			if regex.match(aChangeset['files'][f]):
				aBackouts[k] += 1

	return aBackouts
