from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.loan import Loan
from forms.user import UserEditForm, UserSearchForm
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@login_required
def index():
    """List all users (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    form = UserSearchForm()
    query = request.args.get('query', '')
    
    if query:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.email.ilike(f'%{query}%')) |
            (User.first_name.ilike(f'%{query}%')) |
            (User.last_name.ilike(f'%{query}%'))
        ).order_by(User.username).all()
    else:
        users = User.query.order_by(User.username).all()
    
    return render_template('users/index.html', users=users, form=form, query=query)

@users_bp.route('/users/<int:id>')
@login_required
def show(id):
    """Show user details (admin or self only)"""
    user = User.query.get_or_404(id)
    
    if not current_user.is_admin and current_user.id != user.id:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    active_loans = user.get_active_loans()
    loan_history = user.get_loan_history()
    
    return render_template('users/show.html', 
                           user=user,
                           active_loans=active_loans,
                           loan_history=loan_history)

@users_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit user details (admin or self only)"""
    user = User.query.get_or_404(id)
    
    if not current_user.is_admin and current_user.id != user.id:
        flash('You do not have permission to edit this user.', 'danger')
        return redirect(url_for('main.index'))
    
    form = UserEditForm(obj=user)
    
    # Only admins can change admin status
    if not current_user.is_admin:
        del form.is_admin
    
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.address = form.address.data
        
        # Only admins can change admin status
        if current_user.is_admin and hasattr(form, 'is_admin'):
            user.is_admin = form.is_admin.data
        
        # Change password if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User information updated successfully.', 'success')
        
        if current_user.id == user.id:
            return redirect(url_for('auth.profile'))
        else:
            return redirect(url_for('users.show', id=user.id))
    
    return render_template('users/edit.html', form=form, user=user)

@users_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a user (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to delete users.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.index'))
    
    # Check for active loans
    active_loans = user.get_active_loans()
    if active_loans:
        flash('Cannot delete user with active loans. Please return all books first.', 'danger')
        return redirect(url_for('users.show', id=user.id))
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/reports')
@login_required
def reports():
    """Show library reports (admin only)"""
    if not current_user.is_admin:
        flash('You do not have permission to access reports.', 'danger')
        return redirect(url_for('main.index'))
    
    # Overdue books report
    overdue_loans = Loan.query.filter(
        Loan.returned == False,
        Loan.due_date < datetime.utcnow()
    ).order_by(Loan.due_date).all()
    
    # Most popular books report
    popular_books = db.session.query(
        Book, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(Book).order_by(
        db.func.count(Loan.id).desc()
    ).limit(10).all()
    
    # Active users report
    active_users = db.session.query(
        User, db.func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(User).order_by(
        db.func.count(Loan.id).desc()
    ).limit(10).all()
    
    return render_template('users/reports.html',
                           overdue_loans=overdue_loans,
                           popular_books=popular_books,
                           active_users=active_users)