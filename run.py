from app import create_app
#from app.extensions import db
from app.extensions import extensiones

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
