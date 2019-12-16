#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from sqlalchemy import or_, func
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Show, Artist
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
migrate = Migrate(app, db) 

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Get all venues 
  locations = Venue.query.distinct(Venue.city, Venue.state)
  venues = Venue.query.with_entities(Venue.id, Venue.name, Venue.city, Venue.state)
  data = [
    {
      "city":location.city,
      "state": location.state,
      "venues": [
        {
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows" : Show.query.filter_by(venue_id=venue.id)
          .filter(Show.start_time>datetime.today()).count()
        } for venue in venues if venue.city == location.city and venue.state == location.state
      ]
    } for location in locations
  ]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Search venues by name and location 
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(or_(Venue.name.ilike(f'%{search_term}%'), 
  func.concat(Venue.city, ', ', Venue.state).ilike(f'{search_term}%'))).all()
  
  response = {
    "count": len(venues),
    "data": [
      {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id)
        .filter(Show.start_time >= datetime.today()).count()
      } for venue in venues
    ]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # get a particular venue by its id contoller 
  venue = Venue.query.get(venue_id)
  shows = Show.query.with_entities(Show.start_time,Artist.name,
  Artist.id,Artist.image_link).join(Artist).filter(Show.venue_id == venue.id).all()
  keys = ('start_time', 'artist_name', 'artist_id', 'artist_image_link')
  past_shows = []
  upcoming_shows = []

  for show in shows:
    show_data = dict(zip(keys,show))
    past = show_data['start_time'] < datetime.today()
    show_data['start_time'] = format_datetime(str(show_data['start_time']))
    if past:
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # renders create a new venue form
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # create a new venue 
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  website = request.form['website']
  image_link = request.form['image_link']
  seeking_talent = True if request.form['seeking_talent'] == 'True' else False
  seeking_description = request.form['seeking_description']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']

  try:
    venue = Venue(name=name,
                  city=city,
                  state=state,
                  address=address,
                  phone=phone,
                  website=website,
                  image_link=image_link,
                  seeking_talent=seeking_talent,
                  seeking_description=seeking_description,
                  genres=genres,
                  facebook_link=facebook_link
                  )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # delete a particular venue
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Get all artiste
  artists = Artist.query.all()
  data = [
    {
      "id": artist.id,
      "name": artist.name
    } for artist in artists
  ]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search artist by name and location
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(or_(Artist.name.ilike(f'%{search_term}%'), 
  func.concat(Artist.city, ', ', Artist.state).ilike(f'{search_term}%'))).all()

  response = {
    "count": len(artists),
    "data": [
      {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id)
        .filter(Show.start_time >= datetime.today()).count()
      } for artist in artists
    ]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # get artist by id 
  artist = Artist.query.get(artist_id)
  shows = Show.query.with_entities(Show.start_time,Venue.name,
  Venue.id,Venue.image_link).join(Venue).filter(Show.artist_id == artist.id).all()
  keys = ('start_time', 'venue_name', 'venue_id', 'venue_image_link')
  past_shows = []
  upcoming_shows = []

  for show in shows:
    show_data = dict(zip(keys,show))
    past = show_data['start_time'] < datetime.today()
    show_data['start_time'] = format_datetime(str(show_data['start_time']))
    if past:
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  print(artist.genres)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # get edit artiste form
  artist = Artist.query.get(artist_id)
  form = ArtistForm(genres = artist.genres, seeking_venue = artist.seeking_venue,
   seeking_description = artist.seeking_description)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # edit a particular aartist information
  seeking_description = request.form['seeking_description']
  seeking_venue = request.form['seeking_venue']
  artist = Artist.query.get(artist_id)
  error = False
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    artist.seeking_venue = True if seeking_venue == 'True' else False
    artist.seeking_description = seeking_description if seeking_description else None
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
    error = False
  except:
    error = True
    flash('An error occurred. Artist ' + artist.name + ' info could not be edited.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error: 
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # get edit venue form
  venue = Venue.query.get(venue_id)
  form = VenueForm(genres = venue.genres, seeking_talent = venue.seeking_talent,
   seeking_description = venue.seeking_description)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # edit a venue's infromation
  seeking_description = request.form['seeking_description']
  seeking_talent = request.form['seeking_talent']
  venue = Venue.query.get(venue_id)
  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = True if seeking_talent == 'True' else False
    venue.seeking_description = seeking_description if seeking_description else None
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
    error = False
  except:
    error = True
    flash('An error occurred. Artist ' + venue.name + ' info could not be edited.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # return create new artiste form
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Create new artiste 
  seeking_venue =  request.form['seeking_venue']
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website = request.form['website']
  image_link = request.form['image_link']
  seeking_venue = True if seeking_venue == 'True' else False
  seeking_description = request.form['seeking_description']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']

  try:
    artist = Artist(name=name,
                    city=city,
                    state=state,
                    phone=phone,
                    website=website,
                    image_link=image_link,
                    seeking_venue=seeking_venue,
                    seeking_description=seeking_description,
                    genres=genres,
                    facebook_link=facebook_link
                    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # get all shows
  shows = Show.query.with_entities(Show.artist_id, Venue.name, Show.start_time,
  Show.venue_id, Artist.name, Artist.image_link).join(Artist).join(Venue).all()
  keys = ('artist_id','venue_name','start_time', 'venue_id', 'artist_name', 'artist_image_link')
  data = []

  for show in shows:
    show_dict = dict(zip(keys, show))
    show_dict['start_time'] = format_datetime(str(show_dict['start_time']))
    data.append(show_dict)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # create new artiste
  venue_id = request.form['venue_id']
  artist_id = request.form['artist_id']
  start_time = request.form['start_time']

  try:
    show = Show(venue_id=venue_id,
                artist_id=artist_id,
                start_time=start_time
                )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
