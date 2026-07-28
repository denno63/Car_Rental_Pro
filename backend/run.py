from app import create_app, db

app = create_app()

# Create tables if they don't exist
@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )