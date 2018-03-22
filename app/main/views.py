from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, ConnectForm
from .. import db
from ..models import Permission, Role, User, Connect
from ..decorators import admin_required, permission_required
from .errors import forbidden


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        user = current_user._get_current_object()
        borrower_connections = Connect.query.filter_by(
            guarantor_id=user.id, status='pending').\
        order_by(Connect.last_update.desc()).all()
        return render_template('index.html', borrower_connections=borrower_connections)
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/connect-guarantor', methods=['GET', 'POST'])
@login_required
def connect_guarantor():
    user = current_user._get_current_object()
    form = ConnectForm(user)
    if form.validate_on_submit():
        guarantor = User.query.filter_by(email=form.guarantor_email.data).first()
        print(guarantor)
        connection = Connect(
            borrower_id=user.id,
            guarantor_id=guarantor.id,
            amount=form.amount.data,
            message=form.message.data)
        db.session.add(connection)
        db.session.commit()
        flash('Your connection request has been sent.')
        return redirect(url_for('.index'))
    return render_template('connect_guarantor.html', form=form)

@main.route('/accept-borrower/<id>', methods=['POST'])
@login_required
def accept_borrower(id):
    connection = Connect.query.get(id)
    if current_user._get_current_object() != connection.guarantor:
        return forbidden("Unauthorized User")
    connection.status = "accepted"
    db.session.add(connection)
    db.session.commit()
    flash('Your action has been processed.')
    return redirect(url_for('.index'))

@main.route('/reject-borrower/<id>', methods=['POST'])
@login_required
def reject_borrower(id):
    connection = Connect.query.get(id)
    if current_user._get_current_object() != connection.guarantor:
        return forbidden("Unauthorized User")
    connection.status = "rejected"
    db.session.add(connection)
    db.session.commit()
    flash('Your action has been processed.')
    return redirect(url_for('.index'))
