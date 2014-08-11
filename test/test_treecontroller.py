import json

import responses

from app import tree_controller

treestatus_response = {
  "logs": [
    {
      "reason": "",
      "tags": "",
      "action": "open",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-09T10:42:37"
    },
    {
      "reason": "Infra issues",
      "tags": [
        "infra"
      ],
      "action": "closed",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-09T09:42:06"
    },
    {
      "reason": "",
      "tags": "",
      "action": "open",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-08T22:30:03"
    },
    {
      "reason": "Too many leaks, not enough fingers",
      "tags": [
        "checkin-test"
      ],
      "action": "closed",
      "tree": "mozilla-inbound",
      "who": "ryanvm@gmail.com",
      "when": "2014-08-08T20:24:20"
    },
    {
      "reason": "",
      "tags": [],
      "action": "open",
      "tree": "mozilla-inbound",
      "who": "wkocher@mozilla.com",
      "when": "2014-08-08T14:39:47"
    },
  ]
}

def test_we_can_get_tree_closure_status_and_values():
    responses.add(responses.GET, 'https://treestatus.mozilla.org/mozilla-inbound/logs?format=json&all=1',
    body=json.dumps(treestatus_response), status=200,
    content_type='application/json', match_querystring=True)

    month, dates, status, status_reason = tree_controller.calculate_closures("mozilla-inbound")

    assert status == 'open'
    assert status_reason == ''

