# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('ENV') == 'staging':
	DATABASE_NAME = 'hoh'
else:
	DATABASE_NAME = 'hoh_stable'


# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://quanrio:quanrio$$@adils.me/%s' % DATABASE_NAME

SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"



UPLOAD_FOLDER = 'app/resources/bulk/'
PDF_URL = 'app/resources/pdfs/'

ALLOWED_EXTENSIONS = set(['csv'])
