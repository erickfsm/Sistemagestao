import os
from app import create_app

os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

app = create_app()

if __name__ == '__main__':

   app.run(debug=True, host='0.0.0.0', port=5)