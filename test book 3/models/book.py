from app import db
from datetime import datetime

# Many-to-many relationship between books and genres
book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    author = db.Column(db.String(128), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, index=True)
    publisher = db.Column(db.String(128))
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(128), default='default_cover.jpg')
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    genres = db.relationship('Genre', secondary=book_genre, backref=db.backref('books', lazy='dynamic'))
    loans = db.relationship('Loan', backref='book', lazy='dynamic')
    
    def is_available(self):
        """Check if at least one copy of the book is available"""
        return self.available_copies > 0
    
    def reduce_available_copies(self):
        """Reduce the number of available copies when a book is checked out"""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def increase_available_copies(self):
        """Increase the number of available copies when a book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
    def __repr__(self):
        return f'<Book {self.title}>'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Genre {self.name}>'