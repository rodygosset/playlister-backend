apt-get update
apt-get install -y apt-utils
apt-get install -y postgresql postgresql-contrib
apt-get install -y systemctl
systemctl start postgresql.service
pg_ctlcluster 13 main start
apt-get install sudo -y
sudo -i -u postgres psql -c "CREATE ROLE root SUPERUSER"
sudo -i -u postgres psql -c "ALTER ROLE root WITH login"
sudo -i -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'playlister';"