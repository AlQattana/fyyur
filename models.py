from app import db

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False) #db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(400))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)    
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # [Done] TODO: implement any missing fields, as a database migration using Flask-Migrate 

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), nullable=False) #db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(400))    
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)       

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'    

    # [Done] TODO: implement any missing fields, as a database migration using Flask-Migrate

# [Done] TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    upcoming = db.Column(db.Boolean, nullable=False, default=True)  

    def __repr__(self):
      return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>'  