import datetime
from datetime import timedelta
import re

from flask import render_template, request
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
    checkin_needed_count = tree_controller.checkin_needed_count()


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
        tree=tree, status={"status": status, "status_reason":status_reason}, uptime=uptime, checkin_needed_count=checkin_needed_count)





