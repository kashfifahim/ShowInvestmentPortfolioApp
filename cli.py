import click
from flask import Flask
from flask.cli import with_appcontext
from app import db  # Import your db object from the app module

# Create a Flask app context for the CLI commands
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'  # Replace with your database URI
from app import db 
# Define a CLI group for database commands
db_cli = AppGroup('db')

# Define a CLI command to initialize the database
@db_cli.command('init')
def init_db():
    with app.app_context():
        db.create_all()
        click.echo("Initialized the database.")

# Add the database CLI group to the Flask app
app.cli.add_command(db_cli)

if __name__ == '__main__':
    app.run()