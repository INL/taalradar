# Install git
sudo apt-get install git-core
# Install PostgreSQL
sudo apt-get install postgresql postgresql-server-dev-all libpq-dev python-psycopg2 libsasl2-dev libldap2-dev libssl-dev
# Install Virtualenv (recommended)
sudo apt-get install python-virtualenv
# Install Python requirements
sudo apt-get install python-dev build-essential libjpeg-dev libssl-dev libffi-dev
sudo apt-get install dbus libdbus-1-dev libdbus-glib-1-dev libldap2-dev libsasl2-dev
#Get source code and install python packages in virtualenv with pip:
cd ~/git
# get the source code
git clone --recursive https://github.com/Scifabric/pybossa
# Access the source code folder
cd pybossa
virtualenv env
# Activate the virtual environment
source env/bin/activate
# Upgrade pip to latest version
pip install -U pip
# Install the required libraries
pip install -r requirements.txt
#Copy settings file to right location;
cp settings_local.py.tmpl settings_local.py
# now edit ...
#vim settings_local.py
cp alembic.ini.template alembic.ini
# Install redis server
sudo apt-get install redis-server redis-sentinel
