from flask import Blueprint, render_template, request
from flask_login import current_user
from models.book import Book, Genre
from models.loan import Loan
from sqlalchemy import func
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page showing dashboard with stats and recently added books"""
    # Recently added books
    recent_books = Book.query.order_by(Book.added_date.desc()).limit(8).all()
    
    # Statistics for logged-in users
    user_stats = None
    if current_user.is_authenticated:
        active_loans = Loan.query.filter_by(user_id=current_user.id, returned=False).all()
        overdue_loans = [loan for loan in active_loans if loan.is_overdue()]
        user_stats = {
            'active_loans': len(active_loans),
            'overdue_loans': len(overdue_loans)
        }
    
    # General statistics
    total_books = Book.query.count()
    total_genres = Genre.query.count()
    books_on_loan = Book.query.filter(Book.available_copies < Book.total_copies).count()
    
    # Popular genres
    popular_genres = db.session.query(
        Genre.name,
        func.count(book_genre.c.book_id).label('book_count')
    ).join(book_genre).group_by(Genre.name).order_by(
        func.count(book_genre.c.book_id).desc()
    ).limit(5).all()
    
    return render_template('index.html', 
                           recent_books=recent_books,
                           user_stats=user_stats,
                           total_books=total_books,
                           total_genres=total_genres,
                           books_on_loan=books_on_loan,
                           popular_genres=popular_genres)

@main_bp.route('/search')
def search():
    """Search for books by title, author, or ISBN"""
    query = request.args.get('query', '')
    if not query:
        return render_template('search.html', books=[], query='')
    
    # Search in title, author, and ISBN
    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) |
        (Book.author.ilike(f'%{query}%')) |
        (Book.isbn.ilike(f'%{query}%'))
    ).all()
    
    return render_template('search.html', books=books, query=query)

@main_bp.route('/about')
def about():
    """About page with information about the library system"""
    return render_template('about.html')