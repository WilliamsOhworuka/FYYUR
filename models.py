from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable = False)
    image_link = db.Column(db.String(500), 
    default = '''https://images.unsplash.com/photo-1523730205978-59fd1b2965e3?ixlib=rb-1.2.1
&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=691&q=80''')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable = False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable = False)
    image_link = db.Column(db.String(500), default = '''https://images.unsplash.com/photo-1470063819038-
    51ab7ad86ab6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80''')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable = False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist')

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    start_time = db.Column(db.DateTime, nullable=False)