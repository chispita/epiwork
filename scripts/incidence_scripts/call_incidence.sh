#!/bin/sh

dbname="epiwork"
username="admin"
psql $dbname $username << EOF

copy (select * from pollster_ili_incidence('2012-09-01', '2012-11-16')) TO STDOUT WITH CSV HEADER;
EOF
