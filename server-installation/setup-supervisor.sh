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
