"""Authentication views for login, registration, and user management."""

from datetime import datetime, UTC
from typing import Dict, Any, Union, Optional

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from app.database import db
from app.auth.forms import LoginForm, RegistrationForm, UserEditForm, PasswordChangeForm
from app.database.models.user import User


# Get the blueprint from the auth package
from app.auth import blueprint


class LoginView(MethodView):
    """View for handling user login."""

    def get(self):
        """Display the login form."""
        if current_user.is_authenticated:
            return redirect(url_for('items.all_events'))

        form = LoginForm()
        return render_template('auth/login.html', form=form, title='Sign In')

    def post(self):
        """Process the login form submission."""
        if current_user.is_authenticated:
            return redirect(url_for('items.all_events'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()

            if user is None or not user.verify_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))

            if not user.is_active:
                flash('This account has been deactivated.')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            next_page = request.args.get('next', '').replace('\\', '')  # Sanitize input
            allowed_paths = ['/items/all_events', '/items/some_other_page']  # Whitelist of allowed paths
            parsed_url = url_parse(next_page)
            if next_page not in allowed_paths or parsed_url.netloc or parsed_url.scheme:
                next_page = url_for('items.all_events')  # Default to a safe fallback

            return redirect(next_page)

        return render_template('auth/login.html', form=form, title='Sign In')


class RegisterView(MethodView):
    """View for handling user registration."""

    def get(self):
        """Display the registration form."""
        if current_user.is_authenticated:
            return redirect(url_for('items.all_events'))

        form = RegistrationForm()
        return render_template('auth/register.html', form=form, title='Register')

    def post(self):
        """Process the registration form submission."""
        if current_user.is_authenticated:
            return redirect(url_for('items.all_events'))

        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role='user'  # Default role for new registrations
            )
            user.password = form.password.data

            db.session.add(user)
            db.session.commit()

            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))

        return render_template('auth/register.html', form=form, title='Register')


class LogoutView(MethodView):
    """View for handling user logout."""

    @login_required
    def get(self):
        """Log out the current user."""
        logout_user()
        return redirect(url_for('items.all_events'))


class UserListView(MethodView):
    """View for listing users (admin only)."""

    @login_required
    def get(self):
        """Display list of users."""
        if not current_user.is_admin():
            flash('You do not have permission to access this page.')
            return redirect(url_for('items.all_events'))

        users = User.query.all()
        return render_template('auth/users.html', users=users, title='Users')


class UserEditView(MethodView):
    """View for editing user details (admin only)."""

    @login_required
    def get(self, user_id):
        """Display form to edit a user."""
        if not current_user.is_admin():
            flash('You do not have permission to access this page.')
            return redirect(url_for('items.all_events'))

        user = User.query.get_or_404(user_id)
        form = UserEditForm(obj=user)

        return render_template('auth/edit_user.html', form=form, user=user, title='Edit User')

    @login_required
    def post(self, user_id):
        """Process form submission to edit a user."""
        if not current_user.is_admin():
            flash('You do not have permission to access this page.')
            return redirect(url_for('items.all_events'))

        user = User.query.get_or_404(user_id)
        form = UserEditForm()

        if form.validate_on_submit():
            # Check if username or email have changed and are already taken
            if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
                flash(f'Username {form.username.data} is already taken.')
                return redirect(url_for('auth.edit_user', user_id=user_id))

            if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
                flash(f'Email {form.email.data} is already taken.')
                return redirect(url_for('auth.edit_user', user_id=user_id))

            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.role = form.role.data
            user.is_active = form.is_active.data

            db.session.commit()
            flash('User has been updated.')
            return redirect(url_for('auth.users'))

        return render_template('auth/edit_user.html', form=form, user=user, title='Edit User')


class PasswordChangeView(MethodView):
    """View for changing a user's password."""

    @login_required
    def get(self):
        """Display form to change password."""
        form = PasswordChangeForm()
        return render_template('auth/change_password.html', form=form, title='Change Password')

    @login_required
    def post(self):
        """Process form submission to change password."""
        form = PasswordChangeForm()

        if form.validate_on_submit():
            if not current_user.verify_password(form.current_password.data):
                flash('Current password is incorrect.')
                return redirect(url_for('auth.change_password'))

            current_user.password = form.new_password.data
            db.session.commit()

            flash('Your password has been updated.')
            return redirect(url_for('items.all_events'))

        return render_template('auth/change_password.html', form=form, title='Change Password')


# Register view classes
login_view = LoginView.as_view('login')
register_view = RegisterView.as_view('register')
logout_view = LogoutView.as_view('logout')
users_view = UserListView.as_view('users')
edit_user_view = UserEditView.as_view('edit_user')
change_password_view = PasswordChangeView.as_view('change_password')

# Register URL rules
blueprint.add_url_rule('/login', view_func=login_view, methods=['GET', 'POST'])
blueprint.add_url_rule(
    '/register', view_func=register_view, methods=['GET', 'POST'])
blueprint.add_url_rule('/logout', view_func=logout_view)
blueprint.add_url_rule('/users', view_func=users_view)
blueprint.add_url_rule('/users/<int:user_id>/edit',
                       view_func=edit_user_view, methods=['GET', 'POST'])
blueprint.add_url_rule(
    '/change-password', view_func=change_password_view, methods=['GET', 'POST'])
