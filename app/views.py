import datetime
from datetime import timedelta
import re

from flask import Markup, render_template, request
from app import app

import tree_controller

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    tree = request.args.get('tree', 'mozilla-inbound')
    closure_months, closure_dates, status, status_reason = tree_controller.calculate_closures(tree)
    uptime = tree_controller.get_uptime_stats(closure_months)
    x, y = tree_controller.graph_data_for_uptime(closure_months)
    intermittent_count_last_week = tree_controller.intermittent_opened_count_last_week()
    intermittent_count_closed_last_week = tree_controller.intermittent_count_closed_last_week()


    wek = datetime.datetime.now() - timedelta(7)
    week = "%s-%s-%s" % (wek.year,
        wek.month if wek.month > 9 else "0%s" % wek.month,
        wek.day if wek.day > 9 else "0%s" % wek.day)

    backouts_since_week = tree_controller.backouts(tree, week)
    tody = datetime.datetime.now()

    backed = 0
    today_pushes = 0
    backoutln = re.compile('^.*[b,B]ackout.*')
    backoutln2 = re.compile('^.*[b,B]acked out.*')
    backoutln3 = re.compile('^.*[b,B]ack out.*')
    backout_hours = [0] * 24
    pushes_hours = [0] * 24

    if backouts_since_week is not None:
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
        tree=tree, status={"status": status, "status_reason":status_reason}, uptime=uptime, intermittent_count_last_week=intermittent_count_last_week,
        intermittent_count_closed_last_week=intermittent_count_closed_last_week)

# Backouts Dashboard
@app.route('/backouts.html')
def backouts():
	tree = request.args.get('tree', 'mozilla-central')
	period = request.args.get('w', 4)
	now = datetime.datetime.now()
	backouts_list = []
	
	for i in range(1,int(period)):
		timespan = now - timedelta(i*7)
		y = timespan.year
		m = timespan.month if timespan.month > 9 else "0%s" % timespan.month
		d = timespan.day if timespan.day > 9 else "0%s" % timespan.day
		delta = "%s-%s-%s" % (y, m, d)
		backouts_list.append(tree_controller.backouts_list(tree, delta))
		
	backout_markup = getBackoutMarkup(backouts_list, tree)
	return render_template("backouts.html", backout_markup=backout_markup)

def checkForBackouts(aPushlog):
    # total number of pushes in the log for today
    today_pushes = 0 
	
    # Regular expressions to search for backouts
    regex_backouts = [re.compile('^.*[b,B]ackout.*'),
                      re.compile('^.*[b,B]acked out.*'),
		      re.compile('^.*[b,B]ack out.*')]
                      
    # List of backouts by folder
    backouts_by_folder = {}
    
    if aPushlog is not None: 
	
	# Iterate through each of the pushes
	for resp in aPushlog['pushes']:
	    timestamp = int(aPushlog['pushes'][resp]['date'])
	    pushDate = datetime.date.fromtimestamp(timestamp)
	    	    
	    # Check if the push is from today
	    if (pushDate == datetime.date.today()):
		today_pushes += 1

		# Iterate through the changesets and check if any are a backout
		for chnge in range(len(aPushlog['pushes'][resp]['changesets'])):
		    changeset = aPushlog['pushes'][resp]['changesets'][chnge]
		    print changeset['desc']
                    if (regex_backouts[0].match(changeset['desc']) or
                        regex_backouts[1].match(changeset['desc']) or
                        regex_backouts[2].match(changeset['desc'])):
			print "XXX BACKOUT FOUND! XXX"

                        if (pushDate == datetime.date.today()):
                            backed += 1
                            backouts_by_folder = countBackoutsByFolder(backouts_by_folder, changeset)  
                        
                            break
    
    return backouts_by_folder		

def countBackoutsByFolder(backouts_by_folder, changeset):
    # List of possible folders from hg.mozilla.org/mozilla-central [this should be dynamically generated in the future]
    folders = ["accessibile", "addon-sdk", "b2g", "browser", "build", "caps", "chrome", "config", "content", "db sqlite3", "docshell", "dom", "editor",
               "embedding", "extensions", "gfx", "hal", "image", "intl", "ipc", "js", "layout", "media", "memory", "mfbt", "mobile", "modules", "mozglue",
               "netwerk", "nsprpub", "other-licenses", "parser", "probes", "profile", "python", "rdf", "security", "services", "startupcache", "storage", 
               "testing", "toolkit", "tools", "uriloader", "view", "webapprt", "widget", "xpcom", "xpfe", "xulrunner"]
               	
    for fo in folders:
        backouts_by_folder[fo] = 0

        # Regular expression to search for file folder
        searchString = re.compile('^' + fo + '.*')
			  
        # Iterate through each file indicated in the backout
        for f in range(len(changeset['files'])):
		
            # Check if the folder is found in the file path
            if (searchString.match(changeset['files'][f])):
				
                # Increase the backout count for that folder
                backouts_by_folder[fo] += 1
                
    return backouts_by_folder
	
def getBackoutMarkup(aBackoutsList, aTree):

	html = "<table style='border:1px solid #000000; font-family:Arial'>"
	
	# Table Headings
	html += "<tr>"
	html += "<th>&nbsp;</th>"
	for b in aBackoutsList:
		html += "<th>" + b['startdate'] + "</th>"
	html += "</tr>"
	
	components = aBackoutsList[0]['backouts_list'].keys()
	
	i = 0
	for c in sorted(components):
		if ((i%2) == 0):
			html += "<tr style='background:#bbd9f7'>"
		else:
			html += "<tr style='background:#f9f9c5'>"
		html += "<td>" + c + "</td>"
		for b in aBackoutsList:
			for k, v in sorted(b['backouts_list'].iteritems()):
				if (c == k):
					html += "<td>" + str(v) + "</td>"
			
		html += "</tr>"
		i += 1
	
	html += "</table>"
    
	return Markup(html)
