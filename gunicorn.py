import os

install_dir = os.path.dirname(__file__)
command = f"{install_dir}/venv/bin/gunicorn"
pythonpath = install_dir
workers = 4
user = "appdashboard"
bind = f"unix:{install_dir}/sock"
pid = "/run/gunicorn/appdashboard-pid"
errorlog = "/var/log/appdashboard/error.log"
accesslog = "/var/log/appdashboard/access.log"
access_log_format = '%({X-Real-IP}i)s %({X-Forwarded-For}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "warning"
capture_output = True
