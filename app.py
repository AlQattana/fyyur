#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form, CsrfProtect
from sqlalchemy.orm import backref
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CsrfProtect(app)
moment = Moment(app)
app.config.from_object('config')

# [Done] TODO: connect to a local postgresql database

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # [Done] TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  all_venues_areas = db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()

  data = []

  for area in all_venues_areas:
    venues = db.session.query(Venue).filter_by(state=area.state).filter_by(city=area.city).all()
    venue_info = []
    for venue in venues:
      venue_info.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": venue.upcoming_shows_count
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venue_info
    })
  return render_template('pages/venues.html', areas=data)

#  Search for a Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # [Done] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search_results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(search_results),
    "data": []
  }

  for venue in search_results:
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.upcoming_shows_count
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  View a Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # [Done] TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  
  upcoming_shows = []
  past_shows = []
  shows = venue.shows

  for show in shows:
    show_info = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming): 
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create a Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # [Done] TODO: insert form data as a new Venue record in the db, instead
  # [Done] TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if form.validate_on_submit():
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']  
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']  
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      # [Done] TODO: on unsuccessful db insert, flash an error instead.   
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
      db.session.close()
    
  else:
    for error in form.errors:
      flash("Error: Check " + error + " then resubmit again.")
  return render_template('pages/home.html')

#  Delete a Venue
#  ----------------------------------------------------------------
# [Done] TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # [Done] TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # [Done] TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(search_results),
    "data": []
  }

  for artist in search_results:
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": artist.upcoming_shows_count,
      })
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # [Done] TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  past_shows = []
  upcoming_shows = []
  
  for show in shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  if artist: 
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description    
    form.image_link.data = artist.image_link

  # [Done] TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  if form.validate_on_submit():  
    artist = Artist.query.get(artist_id)

    try: 
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres')
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      artist.website_link = request.form['website_link']
      artist.seeking_venue = True if 'seeking_venue' in request.form else False 
      artist.seeking_description = request.form['seeking_description']

      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully updated!')
    except: 
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + 'could not be changed.')
      
    finally: 
      db.session.close()
      
    # [Done] TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
  else:
    for error in form.errors:
      flash("Error: Check " + error + " then resubmit again.")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  
  # [Done] TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  if form.validate_on_submit():  
    try: 
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      venue.website_link = request.form['website_link']
      venue.seeking_talent = True if 'seeking_talent' in request.form else False 
      venue.seeking_description = request.form['seeking_description']

      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully updated!')
    except: 
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be changed.')

    finally: 
      db.session.close()
    
    # [Done] TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
  else:
    for error in form.errors:
      flash("Error: Check " + error + " then resubmit again.")

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # [Done] TODO: insert form data as a new Venue record in the db, instead
  # [Done] TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if form.validate_on_submit():  
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = request.form.getlist('genres')
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']  
    
    try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully listed!')
    except Exception as e:
      db.session.rollback()
      # [Done] TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.' + str(e))
    finally:
      db.session.close()
  else:
    for error in form.errors:
      flash("Error: Check " + error + " then resubmit again.")

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # [Done] TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []

  for show in shows:
    if(show.upcoming):
      data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # [Done] TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  if form.validate_on_submit():
    try: 
      show = Show()
      show.artist_id = request.form['artist_id']
      show.venue_id = request.form['venue_id']
      show.start_time = request.form['start_time']

      db.session.add(show)
      db.session.commit()
      
      now = datetime.now()
      show.upcoming = (now < show.start_time)
      artist = Artist.query.get(show.artist_id)
      venue = Venue.query.get(show.venue_id)

      if(show.upcoming):
        artist.upcoming_shows_count += 1
        venue.upcoming_shows_count += 1
      else:
        artist.past_shows_count += 1
        venue.past_shows_count += 1  
      
      db.session.add(artist)    
      db.session.add(venue)
      db.session.commit()


      # on successful db insert, flash success
      flash('Show was successfully listed!')
    
    except: 
      db.session.rollback()
      # [Done] TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/    
      flash('An error occurred. Show could not be listed.')
      
    finally: 
      db.session.close()
  else:
    for error in form.errors:
      flash("Error: Check " + error + " then resubmit again.")
  
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
