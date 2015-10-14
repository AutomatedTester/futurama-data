import json

import responses

from app import tree_controller

treestatus_response = {
  "result": [
    {
      "reason": "",
      "tags": "",
      "status": "open",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-09T10:42:37+00:00"
    },
    {
      "reason": "Infra issues",
      "tags": [
        "infra"
      ],
      "status": "closed",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-09T09:42:06"
    },
    {
      "reason": "",
      "tags": "",
      "status": "open",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-08T22:30:03"
    },
    {
      "reason": "Too many leaks, not enough fingers",
      "tags": [
        "checkin-test"
      ],
      "status": "closed",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-08T20:24:20"
    },
    {
      "reason": "",
      "tags": [],
      "status": "open",
      "tree": "mozilla-inbound",
      "who": "wkocher@mozilla.com",
      "when": "2014-08-08T14:39:47"
    },
  ]
}

@responses.activate
def test_we_can_get_tree_closure_status_and_values():
    responses.add(responses.GET, 'https://api.pub.build.mozilla.org/treestatus/trees/mozilla-inbound/logs?all=1',
                  body=json.dumps(treestatus_response), status=200,
                  content_type='application/json', match_querystring=True)
    month, dates, status, status_reason = tree_controller.calculate_closures("mozilla-inbound")

    assert status == 'open'
    assert status_reason == ''
