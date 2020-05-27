# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.venue_id}, {self.artist_id}, {self.start_time}>'


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    genres = db.Column(db.ARRAY(db.String(50)), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref=db.backref('venue', lazy=True), primaryjoin=id == Show.venue_id)

    def __repr__(self):
        return f'<Venue {self.id}, {self.name}, {self.genres}, {self.city}, {self.state}, {self.address}' \
               f', {self.phone}, {self.website}, {self.facebook_link}, {self.image_link},' \
               f' {self.seeking_talent}, {self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    genres = db.Column(db.ARRAY(db.String(50)), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref=db.backref('artist', lazy=True), primaryjoin=id == Show.artist_id)

    def __repr__(self):
        return f'<Artist {self.id}, {self.name}>'


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    # return babel.dates.format_datetime(date, format)
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    shows = lambda v: Venue.query \
        .with_entities(Venue.id.label('id'),
                       Venue.name.label('name'),
                       Venue,
                       Show.query
                       .with_entities(db.func.count(1))
                       .filter(Show.venue_id == Venue.id, Show.start_time >= datetime.now())
                       .label('num_upcoming_shows')) \
        .filter(Venue.state == v.state, Venue.city == v.city)

    data = [
        {
            "state": venue.state,
            "city": venue.city,
            "venues": shows(venue)
        }
        for venue in Venue.query.distinct(Venue.state, Venue.city)]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    data = Venue.query \
        .with_entities(Venue.id.label('id'),
                       Venue.name.label('name'),
                       Show.query
                       .with_entities(db.func.count(1))
                       .filter(Show.venue_id == Venue.id, Show.start_time >= datetime.now())
                       .label('num_upcoming_shows')) \
        .filter(Venue.name.ilike("%{}%".format(search_term)))

    response = {
        "count": data.count(),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id).__dict__

    past_shows = db.session \
        .query(Show).join(Artist).join(Venue) \
        .with_entities(Show.venue_id.label('venue_id'),
                       Show.artist_id.label('artist_id'),
                       Show.start_time.label('start_time'),
                       Artist.name.label('artist_name'),
                       Artist.image_link.label('artist_image_link')) \
        .filter(Show.venue_id == venue_id, Show.start_time < datetime.now())
    past_shows_count = past_shows.count()
    upcoming_shows = db.session \
        .query(Show).join(Artist).join(Venue) \
        .with_entities(Show.venue_id.label('venue_id'),
                       Show.artist_id.label('artist_id'),
                       Show.start_time.label('start_time'),
                       Artist.name.label('artist_name'),
                       Artist.image_link.label('artist_image_link')) \
        .filter(Show.venue_id == venue_id, Show.start_time >= datetime.now())
    upcoming_shows_count = upcoming_shows.count()

    data['past_shows'] = past_shows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = upcoming_shows_count

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue(name=request.form.get('name'),
                      genres=request.form.getlist('genres'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      address=request.form.get('address'),
                      phone=request.form.get('phone'),
                      website=request.form.get('website'),
                      facebook_link=request.form.get('facebook_link'),
                      image_link=request.form.get('image_link'),
                      seeking_talent=request.form.get('seeking_talent') is not None,
                      seeking_description=request.form.get('seeking_description'))
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    data = Artist.query \
        .with_entities(Artist.id.label('id'),
                       Artist.name.label('name'),
                       Show.query
                       .with_entities(db.func.count(1))
                       .filter(Show.artist_id == Artist.id, Show.start_time >= datetime.now())
                       .label('num_upcoming_shows')) \
        .filter(Artist.name.ilike("%{}%".format(search_term)))

    response = {
        "count": data.count(),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id).__dict__

    past_shows = db.session \
        .query(Show).join(Artist).join(Venue) \
        .with_entities(Venue.name.label('venue_name'),
                       Venue.image_link.label('venue_image_link'),
                       Show.venue_id.label('venue_id'),
                       Show.artist_id.label('artist_id'),
                       Show.start_time.label('start_time')) \
        .filter(Show.artist_id == artist_id, Show.start_time < datetime.now())
    past_shows_count = past_shows.count()
    upcoming_shows = db.session \
        .query(Show).join(Artist).join(Venue) \
        .with_entities(Venue.name.label('venue_name'),
                       Venue.image_link.label('venue_image_link'),
                       Show.venue_id.label('venue_id'),
                       Show.artist_id.label('artist_id'),
                       Show.start_time.label('start_time')) \
        .filter(Show.artist_id == artist_id, Show.start_time >= datetime.now())
    upcoming_shows_count = upcoming_shows.count()

    data['past_shows'] = past_shows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = upcoming_shows_count

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.genres = request.form.getlist('genres')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_venue = request.form.get('seeking_venue') is not None
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.genres = request.form.getlist('genres')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = request.form.get('seeking_talent') is not None
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be listed.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist = Artist(name=request.form.get('name'),
                        genres=request.form.getlist('genres'),
                        city=request.form.get('city'),
                        state=request.form.get('state'),
                        phone=request.form.get('phone'),
                        website=request.form.get('website'),
                        image_link=request.form.get('image_link'),
                        facebook_link=request.form.get('facebook_link'),
                        seeking_venue=request.form.get('seeking_venue') is not None,
                        seeking_description=request.form.get('seeking_description'))
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = db.session.query(
        Show
    ).join(
        Artist
    ).join(
        Venue
    ).with_entities(
        Show.venue_id.label('venue_id'),
        Show.artist_id.label('artist_id'),
        Show.start_time.label('start_time'),
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link')
    ).all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(artist_id=request.form.get('artist_id'),
                    venue_id=request.form.get('venue_id'),
                    start_time=request.form.get('start_time'))
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
