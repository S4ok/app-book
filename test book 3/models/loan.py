from app import db
from datetime import datetime, timedelta

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False)
    renewed_count = db.Column(db.Integer, default=0)
    
    def __init__(self, user_id, book_id, loan_duration=14):
        """Initialize a new loan with a default duration of 14 days"""
        self.user_id = user_id
        self.book_id = book_id
        self.checkout_date = datetime.utcnow()
        self.due_date = self.checkout_date + timedelta(days=loan_duration)
        self.returned = False
        self.renewed_count = 0
    
    def renew(self, days=14, max_renewals=2):
        """Renew a loan if it hasn't been renewed too many times"""
        if self.renewed_count < max_renewals and not self.returned:
            self.renewed_count += 1
            self.due_date = datetime.utcnow() + timedelta(days=days)
            return True
        return False
    
    def return_book(self):
        """Mark a book as returned"""
        if not self.returned:
            self.returned = True
            self.return_date = datetime.utcnow()
            return True
        return False
    
    def is_overdue(self):
        """Check if the loan is overdue"""
        return not self.returned and datetime.utcnow() > self.due_date
    
    def days_overdue(self):
        """Calculate the number of days a book is overdue"""
        if self.is_overdue():
            delta = datetime.utcnow() - self.due_date
            return delta.days
        return 0
    
    def __repr__(self):
        return f'<Loan {self.id}>'