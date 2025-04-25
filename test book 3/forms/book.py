from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from models.book import Book
import re

class BookForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=128)
    ])
    author = StringField('Author', validators=[
        DataRequired(),
        Length(max=128)
    ])
    isbn = StringField('ISBN', validators=[
        DataRequired(),
        Length(max=20)
    ])
    publisher = StringField('Publisher', validators=[
        Optional(),
        Length(max=128)
    ])
    publication_year = IntegerField('Publication Year', validators=[
        Optional(),
        NumberRange(min=1000, max=3000)
    ])
    description = TextAreaField('Description', validators=[
        Optional()
    ])
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    total_copies = IntegerField('Total Copies', validators=[
        DataRequired(),
        NumberRange(min=1, message='At least one copy is required')
    ])
    genres = SelectMultipleField('Genres', coerce=int)
    submit = SubmitField('Save Book')
    
    def validate_isbn(self, isbn):
        """Validate ISBN format and uniqueness"""
        # ISBN-13 validation (simple check)
        if not re.match(r'^(\d{13}|\d{10}|[\d-]{17})$', isbn.data):
            raise ValidationError('ISBN must be 10 or 13 digits, or formatted with hyphens.')
        
        # Check uniqueness, excluding the current book in case of edit
        book = Book.query.filter_by(isbn=isbn.data).first()
        if book and (not hasattr(self, 'id') or book.id != self.id.data):
            raise ValidationError('A book with this ISBN already exists.')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')