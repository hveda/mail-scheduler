from flask_mail import Mail
from flask_migrate import Migrate
from flask_rq2 import RQ

mail = Mail()
migrate = Migrate()
rq = RQ()
