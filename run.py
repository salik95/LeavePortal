# Run a test server.
from app import app
from app.resources.notifications import notify
notify('arsalanjaved2010@gmail.com')
#app.run(port=8080, debug=True)
