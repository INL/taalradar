## Installatie
https://docs.pybossa.com/installation/guide/

Installeren op gebruiker met lagere privileges, zoals www.

Voer de volgende regels uit (of script `pybossa-source-requirements.sh`):

```
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


### Setup database

```
sudo su postgres
createuser -d -P pybossa # Eventueel nee op alle volgende vragen.
# Stel wachtwoord 'tester' in
createdb pybossa -O pybossa
exit # exit postgresql user
python cli.py db_create # populate database with tables
```

### Draaien als losse processen (niet aanbevolen)
------
```

Now run processes in separate terminals:

```
redis-server contrib/sentinel.conf --sentinel
```

```
# Run rqscheduler
rqscheduler --host IP-of-your-redis-master-node
```

```
# Run worker
python app_context_rqworker.py scheduled_jobs super high medium low email maintenance
```

```
# Run web server
python run.py # Run web server
```
-----

Webserver is nu beschikbaar op http://localhost:5000


## Installatie als background daemon
Volgens deze beschrijving: https://docs.pybossa.com/installation/deployment/


Installeer nginx via pakketbeheer en uwsgi via pip, terwijl je in de virtual environment zit:
```
sudo apt-get install nginx
source env/bin/activate
pip install -u uwsgi
```

### Nginx config

```
# Copy config file to available sites
sudo cp contrib/nginx/pybossa /etc/nginx/sites-available/.
```
Pas in het gekopieerde configuratiebestand op 3 plaatsen de paden aan.
Hier kan ook de poort waarop de server draait worden ingesteld.

```
#Remove default site
sudo rm /etc/nginx/sites-enabled/default
# Enable pybossa site:
sudo ln -s /etc/nginx/sites-available/pybossa /etc/nginx/sites-enabled/pybossa
sudo service nginx restart
```

### Uwsgi config
Kopieer configuratiebestand van contrib-directory naar hoofddirectory van PyBossa.
```
cp contrib/pybossa.ini.template pybossa.ini
```

Pas in `pybossa.ini` op 2 plaatsen de paden aan.

### Supervisor
`Supervisor` maakt van Pybossa een daemon. Voer de volgende regels uit vanaf de git-map van PyBossa (of script `setup-supervisor.sh`:
```
sudo apt-get install supervisor
sudo service redis-server stop
sudo killall redis-server
sudo rm /etc/init.d/redis-server
sudo cp contrib/supervisor/redis-server.conf /etc/supervisor/conf.d/
sudo cp contrib/supervisor/redis-sentinel.conf /etc/supervisor/conf.d/
sudo cp contrib/redis-supervisor/redis.conf /etc/redis/
sudo cp contrib/redis-supervisor/sentinel.conf /etc/redis/
sudo chown redis:redis /etc/redis/redis.conf
sudo chown redis:redis /etc/redis/sentinel.conf
sudo service supervisor stop
sudo service supervisor start
```

To verify the installation, you can list all redis processes, and you should see a redis-server at port 6379 and redis-sentinel at port 26379:

```
ps aux | grep redis
```

Als het niet werkt, en je ziet geen loggegevens in /var/log/supervisor/supervisord.log, kun je ook handmatig supervisor starten en de output bekijken:
```
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
```

Kopieer configuratiebestanden van RQ:

```
sudo cp contrib/supervisor/rq-scheduler.conf.template /etc/supervisor/conf.d/rq-scheduler.conf
sudo cp contrib/supervisor/rq-worker.conf.template /etc/supervisor/conf.d/rq-worker.conf
```

Pas in beide bestanden de twee paden en gebruiker aan. Herstart vervolgens supervisor:
```
sudo service supervisor stop
sudo service supervisor start
```

Verify that the service is running. You should see a rqworker and rqscheduler instance in the console:
```
ps aux | grep rq
```

### Start PyBossa als service
In het bestand `settings_local.py` staat het volgende:
```
# HOST = '0.0.0.0'
# PORT = 5000
```
Dit kun je negeren, door het starten als daemon bepaalt nginx de host en poort.

Voor productie, moet hier het volgende worden ingesteld:
```
SERVER_NAME = mypybossa.com
PORT = 80
```


Kopieer config file van PyBossa voor supervisor.
```
sudo cp contrib/supervisor/pybossa.conf.template /etc/supervisor/conf.d/pybossa.conf
```
en pas paden en gebruiker aan.

Restart supervisor:
```
sudo service supervisor stop
sudo service supervisor start
```

PyBossa zou nu beschikbaar moeten zijn op `localhost`, op de poort aangegeven in `/etc/nginx/sites-available/pybossa`

## Configuratie
Locatie van lokale settings kan worden ingesteld met environment variable: export PYBOSSA_SETTINGS=/my/config/file/somewhere
BRAND en TITLE instellen in pybossa/settings_local.py
LOGO instellen op logo-bestand. Bestand met deze naam plaatsen in pybossa/pybossa/themes/default/static/img
Thema instellen? Vertaling naar Nederlands aanmaken?

## Computation script
From the task presenter Javascript/html page, it may be convenient to call a server-side Python script, which performs certain computations.
The Python script (which runs a server), can be called in the Javascript code via a JQuery AJAX get request.

A Python script can be run as server using the SimpleHTTPServer class, running on a different port, eg. 8080. However, the PyBossa Javascript can only do a get request to a site on the same port, due to the same origin policy. Therefore, nginx should reverse proxy the script on the other port to a subdirectory of the main PyBossa port.

Add in `/etc/nginx/sites-available/pybossa`:

```
location /computation/ {
        proxy_pass http://localhost:8080/;
}
```
