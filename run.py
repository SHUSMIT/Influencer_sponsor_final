# /run.py

from app import app_creator, database_creator

# 1. Create the 'app' object so Gunicorn can import it
app = app_creator()

# 2. Create the database tables
database_creator(app)

# 3. This part is now just for running locally
if __name__ == "__main__":
    app.run(debug=True)
