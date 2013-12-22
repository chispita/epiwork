#!/bin/bash
set -e


export PGPASSWORD=iefpi12irbg
#cat /home/ggm/scripts/dump_intake_2_countries.sql | psql > /dev/null
#cat /home/ggm/scripts/dump_weekly_2_countries.sql | psql > /dev/null

#cat /home/bifi/apps/epiwork-website/scripts/dump_intake.sql | psql 
#cat /home/bifi/apps/epiwork-website/scripts/dump_weekly.sql | psql 

#cat /home/bifi/apps/epiwork-website/scripts/dump_intake.sql | psql > /dev/null
#cat /home/bifi/apps/epiwork-website/scripts/dump_weekly.sql | psql > /dev/null
cat /home/bifi/apps/epiwork-website/scripts/dump_intake.sql | psql -h localhost -p 5432 -U admin epiwork > /dev/null
cat /home/bifi/apps/epiwork-website/scripts/dump_weekly.sql | psql -h localhost -p 5432 -U admin epiwork > /dev/null

pg_dump -h localhost -p 5432 -U admin -t epidb_results_intake -t epidb_results_weekly --clean epiwork > /home/bifi/apps/epiwork-website/data/epidb_results.sql
#pg_dump -t epidb_results_intake -t epidb_results_weekly --clean > /home/bifi/apps/epiwork-website/data/epidb_results.sql
grep -v 'ALTER TABLE public.*OWNER TO' /home/bifi/apps/epiwork-website/data/epidb_results.sql > /home/bifi/apps/epiwork-website/data/epidb_results.sql.tmp
mv /home/bifi/apps/epiwork-website/data/epidb_results.sql.tmp /home/bifi/apps/epiwork-website/data/epidb_results.sql

#scp /home/bifi/apps/epiwork-website/data/epidb_results.sql gripenetes@85.90.70.27: >/dev/null
#ssh gripenetes@85.90.70.27 'cat epidb_results.sql | psql' > /dev/null
scp /home/bifi/apps/epiwork-website/data/epidb_results.sql gripenets@epidb.influenzanet.eu: 
ssh gripenets@epidb.influenzanet.eu 'cat epidb_results.sql | psql' 
ssh gripenets@epidb.influenzanet.eu 'echo "GRANT SELECT ON epidb_results_intake, epidb_results_weekly TO epidb" | psql' > /dev/null
