from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models.book import Book, Genre
from models.loan import Loan
from forms.book import BookForm, SearchForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime

books_bp = Blueprint('books', __name__)

@books_bp.route('/books')
def index():
    """Display all books with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', None, type=int)
    availability = request.args.get('available', None, type=str)
    sort_by = request.args.get('sort', 'title', type=str)
    
    # Base query
    query = Book.query
    
    # Apply filters
    if genre_id:
        genre = Genre.query.get_or_404(genre_id)
        query = genre.books
    
    if availability == 'yes':
        query = query.filter(Book.available_copies > 0)
    elif availability == 'no':
        query = query.filter(Book.available_copies == 0)
    
    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Book.author)
    elif sort_by == 'newest':
        query = query.order_by(Book.added_date.desc())
    
    # Paginate
    books = query.paginate(page=page, per_page=current_app.config['BOOKS_PER_PAGE'])
    genres = Genre.query.order_by(Genre.name).all()
    
    return render_template('books/index.html', 
                           books=books,
                           genres=genres,
                           current_genre=genre_id,
                           availability=availability,
                           sort_by=sort_by)

@books_bp.route('/books/<int:id>')
def show(id):
    """Display details for a specific book"""
    book = Book.query.get_or_404(id)
    # Check if user has this book on loan
    user_has_book = False
    if current_user.is_authenticated:
        loan = Loan.query.filter_by(
            user_id=current_user.id,
            book_id=book.id,
            returned=False
        ).first()
        user_has_book = loan is not None
    
    return render_template('books/show.html', book=book, user_has_book=user_has_book)

@books_bp.route('/books/new', methods=['GET', 'POST'])
@login_required
def new():
    """Add a new book (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('books.index'))
    
    form = BookForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name)]
    
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data,
            publisher=form.publisher.data,
            publication_year=form.publication_year.data,
            description=form.description.data,
            total_copies=form.total_copies.data,
            available_copies=form.total_copies.data
        )
        
        # Handle cover image upload
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            # Create unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            form.cover_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            book.cover_image = filename
        
        # Add selected genres
        for genre_id in form.genres.data:
            genre = Genre.query.get(genre_id)
            if genre:
                book.genres.append(genre)
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.show', id=book.id))
    
    return render_template('books/new.html', form=form)

@books_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing book (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('books.index'))
    
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name)]
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.isbn = form.isbn.data
        book.publisher = form.publisher.data
        book.publication_year = form.publication_year.data
        book.description = form.description.data
        
        # Update copies (handle potential conflicts with loans)
        new_total = form.total_copies.data
        current_on_loan = book.total_copies - book.available_copies
        
        if new_total < current_on_loan:
            flash('Cannot reduce total copies below the number currently on loan.', 'danger')
        else:
            book.total_copies = new_total
            book.available_copies = new_total - current_on_loan
        
        # Handle cover image upload
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            # Create unique filename
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            form.cover_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
            # Remove old image if it's not the default
            if book.cover_image != 'default_cover.jpg':
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover_image))
                except:
                    pass
                    
            book.cover_image = filename
        
        # Update genres
        book.genres = []
        for genre_id in form.genres.data:
            genre = Genre.query.get(genre_id)
            if genre:
                book.genres.append(genre)
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.show', id=book.id))
    
    # Pre-select current genres
    form.genres.data = [genre.id for genre in book.genres]
    
    return render_template('books/edit.html', form=form, book=book)

@books_bp.route('/books/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a book (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('books.index'))
    
    book = Book.query.get_or_404(id)
    
    # Check if any copies are on loan
    if book.available_copies < book.total_copies:
        flash('Cannot delete book while copies are on loan.', 'danger')
        return redirect(url_for('books.show', id=book.id))
    
    # Remove cover image if it's not the default
    if book.cover_image != 'default_cover.jpg':
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover_image))
        except:
            pass
    
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books.index'))

@books_bp.route('/books/<int:id>/checkout', methods=['POST'])
@login_required
def checkout(id):
    """Check out a book"""
    book = Book.query.get_or_404(id)
    
    # Check if book is available
    if not book.is_available():
        flash('This book is not available for checkout.', 'danger')
        return redirect(url_for('books.show', id=book.id))
    
    # Check if user already has this book
    existing_loan = Loan.query.filter_by(
        user_id=current_user.id,
        book_id=book.id,
        returned=False
    ).first()
    
    if existing_loan:
        flash('You already have this book checked out.', 'warning')
        return redirect(url_for('books.show', id=book.id))
    
    # Create new loan
    loan = Loan(user_id=current_user.id, book_id=book.id)
    
    # Update book availability
    book.reduce_available_copies()
    
    db.session.add(loan)
    db.session.commit()
    
    flash(f'You have checked out "{book.title}". It is due back on {loan.due_date.strftime("%B %d, %Y")}.', 'success')
    return redirect(url_for('auth.profile'))

@books_bp.route('/books/<int:id>/return', methods=['POST'])
@login_required
def return_book(id):
    """Return a book"""
    loan = Loan.query.filter_by(
        user_id=current_user.id,
        book_id=id,
        returned=False
    ).first_or_404()
    
    book = Book.query.get_or_404(id)
    
    # Mark as returned and update book availability
    loan.return_book()
    book.increase_available_copies()
    
    db.session.commit()
    
    flash(f'You have returned "{book.title}".', 'success')
    return redirect(url_for('auth.profile'))

@books_bp.route('/books/<int:id>/renew', methods=['POST'])
@login_required
def renew(id):
    """Renew a book loan"""
    loan = Loan.query.filter_by(
        user_id=current_user.id,
        book_id=id,
        returned=False
    ).first_or_404()
    
    book = Book.query.get_or_404(id)
    
    # Try to renew
    if loan.renew():
        db.session.commit()
        flash(f'You have renewed "{book.title}". It is now due back on {loan.due_date.strftime("%B %d, %Y")}.', 'success')
    else:
        flash('Unable to renew. You may have reached the maximum number of renewals.', 'danger')
    
    return redirect(url_for('auth.profile'))