SELECT COUNT(*) AS "November 2013 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-10-31"
    AND from_unixtime(timestamp) < "2013-12-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "November 2013 without Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-10-31"
    AND from_unixtime(timestamp) < "2013-12-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "December 2013 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-11-30"
    AND from_unixtime(timestamp) < "2014-01-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "December 2013 without Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-11-30"
    AND from_unixtime(timestamp) < "2014-01-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "January 2014 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-12-31"
    AND from_unixtime(timestamp) < "2014-02-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "January 2014 without Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2013-12-31"
    AND from_unixtime(timestamp) < "2014-02-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "February 2014 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-01-31"
    AND from_unixtime(timestamp) < "2014-03-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "February 2014 without Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-01-31"
    AND from_unixtime(timestamp) < "2014-03-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "March 2014 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-02-28"
    AND from_unixtime(timestamp) < "2014-04-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "March 2014 with Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-02-28"
    AND from_unixtime(timestamp) < "2014-04-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "April 2014 with Backouts" FROM (SELECT push_id
    FROM Pushes p1
    WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-03-31"
    AND from_unixtime(timestamp) < "2014-05-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND (p2.changeset_message LIKE "Merge%" OR p2.changeset_message REGEXP "^.*[b,B]ackout.*|^.*[b,B]acked out.*|^.*[b,B]ack out.*"))
GROUP BY push_id WITH ROLLUP) x;

SELECT COUNT(*) AS "April 2014 without Backouts" FROM (SELECT push_id
FROM Pushes p1
WHERE branch_name='FX-Team'
    AND from_unixtime(timestamp) > "2014-03-31"
    AND from_unixtime(timestamp) < "2014-05-01"
    AND  NOT EXISTS(
        SELECT * FROM Pushes p2
        WHERE p2.push_id = p1.push_id
            AND p2.changeset_message LIKE "Merge%")
GROUP BY push_id WITH ROLLUP) x;