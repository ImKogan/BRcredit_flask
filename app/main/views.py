from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, ConnectForm,\
    PersonalInfoForm, AddressForm, FinancesForm, ReviewApplication
from .. import db
from ..models import User, Connect, Address, Terms, Application, Finances, Loan, Role, Payment
#from ..decorators import 
from .errors import forbidden

import numpy as np


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        user = current_user._get_current_object()
        # redo using relationship
        borrower_connections = Connect.query.filter_by(
            guarantor_id=user.id, status='pending').\
            order_by(Connect.last_update.desc()).all()
        guarantor_connections = Connect.query.filter_by(
            borrower_id=user.id, status='accepted').\
            order_by(Connect.last_update.desc()).all()
        borrower_applications = Application.query.filter_by(
            guarantor_id=user.id, status=1).\
            order_by(Application.updated_at.desc()).all()
        return render_template('index.html', 
            borrower_connections=borrower_connections,
            guarantor_connections=guarantor_connections,
            borrower_applications=borrower_applications)
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
        current_user.username = form.username.data
        current_user.location = form.location.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.location.data = current_user.location
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
#@admin_required
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

@main.route('/continue-application/<application_id>/<applicant>', methods=['GET', 'POST'])
@login_required
def continue_application(application_id, applicant):
    application = Application.query.get(application_id)
    if applicant not in ('borrower','guarantor'):
        return forbidden("Unauthorized User")
    elif applicant == 'borrower' and \
            current_user._get_current_object() != application.borrower:
        return forbidden("Unauthorized User")
    elif applicant == 'guarantor' and \
            current_user._get_current_object() != application.guarantor:
        return forbidden("Unauthorized User")
    
    form = PersonalInfoForm()
    if request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.cpf.data = current_user.cpf
        form.dob.data = current_user.dob
        return render_template('personal_info.html', form=form)
    else:
        if form.validate_on_submit():
            current_user.firstname = form.firstname.data
            current_user.lastname = form.lastname.data
            current_user.cpf = form.cpf.data
            current_user.dob = form.dob.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash('Your information has been updated.')
            return redirect(url_for('.address_list',
                application_id=application.id, applicant=applicant))
        else:
            return redirect(url_for('.continue_application',
                application_id=application.id, applicant=applicant))

@main.route('/start-application/<connection_id>/<applicant>', methods=['GET', 'POST'])
@login_required
def start_application(connection_id, applicant):
    connection = Connect.query.get(connection_id)
    if applicant not in ('borrower','guarantor'):
        return forbidden("Unauthorized User")
    elif applicant == 'borrower' and \
            current_user._get_current_object() != connection.borrower:
        return forbidden("Unauthorized User")
    elif applicant == 'guarantor' and \
            current_user._get_current_object() != connection.guarantor:
        return forbidden("Unauthorized User")
    
    form = PersonalInfoForm()
    if request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.cpf.data = current_user.cpf
        form.dob.data = current_user.dob
        return render_template('personal_info.html', form=form)
    else:
        if form.validate_on_submit():
            application = Application(connection=connection,
                            borrower=connection.borrower,
                            guarantor=connection.guarantor,
                            amount=connection.amount)
            db.session.add(application)
            db.session.commit()
            current_user.firstname = form.firstname.data
            current_user.lastname = form.lastname.data
            current_user.cpf = form.cpf.data
            current_user.dob = form.dob.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash('Your information has been updated.')
            return redirect(url_for('.address_list',
                application_id=application.id, applicant=applicant))
        else:
            return redirect(url_for('.start_application',
                connection_id=connection_id, applicant=applicant))
    
# @main.route('/address-list/<application_id>/<applicant>/',
#     defaults={'address_id': None}, methods=['GET', 'POST'])
@main.route('/address-list/<application_id>/<applicant>/', methods=['GET', 'POST'])
@login_required
def address_list(application_id, applicant):
    if request.method == "GET":
        addresses = current_user._get_current_object().addresses
        if len(addresses) > 0:
            return render_template('address_list.html',
                addresses=addresses, application=application_id, applicant=applicant)
        return redirect(url_for('.address_form',
            application_id=application_id, applicant=applicant))
    else:
        address_id = request.form["address_id"]
        address = Address.query.get(address_id)
        address.user = current_user._get_current_object()
        application = Application.query.get(application_id)
        if applicant == "borrower":
            application.borrower_address = address
        elif applicant == "guarantor":
            application.guarantor_address = address
        db.session.add(address)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('.finances_form',
            application_id=application_id, applicant=applicant))

@main.route('/address-form/<application_id>/<applicant>', methods=['GET', 'POST'])
@login_required
def address_form(application_id, applicant):
    form = AddressForm()
    if request.method == "GET":
        return render_template('address_form.html', form=form)
    else:
        if form.validate_on_submit():
            address = Address(
                street = form.street.data,
                house = form.house.data,
                apartment = form.apartment.data,
                city = form.city.data,
                state = form.state.data,
                country = form.country.data,
                zipcode = form.zipcode.data)
            address.user = current_user._get_current_object()
            db.session.add(address)
            application = Application.query.get(application_id)
            if applicant == "borrower":
                application.borrower_address = address
            elif applicant == "guarantor":
                application.guarantor_address = address
            db.session.add(application)
            db.session.commit()
            return redirect(url_for('.finances_form',
                application_id=application_id, applicant=applicant))
        else:
            return redirect(url_for('.address_form',
                application_id=application_id, applicant=applicant))

@main.route('/finances-form/<application_id>/<applicant>', methods=['GET', 'POST'])
@login_required
def finances_form(application_id, applicant):
    if request.method == "GET":
        application = Application.query.get(application_id)
        if applicant == "borrower":
            finances = application.borrower_finances
        elif applicant == "guarantor":
            finances = application.guarantor_finances
        form = FinancesForm(obj=finances)
        return render_template('finances_form.html', form=form)
    else:
        form = FinancesForm()
        print(form.employment_status.choices)
        print(form.employment_status)
        if form.validate_on_submit():
            finances = Finances(
                salary = form.salary.data,
                occupation = form.occupation.data,
                employer = form.employer.data,
                time_employed = form.time_employed.data,
                employment_status = form.employment_status.data)
            #finances.user = current_user._get_current_object()
            db.session.add(finances)
            application = Application.query.get(application_id)
            if applicant == "borrower":
                application.borrower_finances = finances
            elif applicant == "guarantor":
                application.guarantor_finances = finances
            db.session.add(application)
            db.session.commit()
            if applicant == 'borrower':
                return redirect(url_for('.choose_terms',
                    application_id=application_id, applicant=applicant))
            elif applicant == 'guarantor':
                return redirect(url_for('.review_application',
                    application_id=application_id, applicant=applicant))                
        else:
            print("invalid")
            return redirect(url_for('.finances_form',
                application_id=application_id, applicant=applicant))

@main.route('/choose-terms/<application_id>/<applicant>/',
    defaults={'term_id': None}, methods=['GET', 'POST'])
@main.route('/choose-terms/<application_id>/<applicant>/<term_id>', methods=['GET', 'POST'])
@login_required
def choose_terms(application_id, applicant, term_id):
    if request.method == "GET":
        terms = Terms.query.all()
        amount = Application.query.get(application_id).amount
        info = []
        for term in terms:
            info.append({"term_id": term.id,
                "amount": amount,
                "rate": term.rate, 
                "installments": term.installments,
                "payment": -np.pmt(rate=term.rate/100, nper=term.installments,pv=amount)})
        return render_template('terms.html', terms=info,
            application=application_id, applicant=applicant)
    else:
        terms = Terms.query.get(request.form["terms_id"])
        application = Application.query.get(application_id)
        application.terms = terms
        db.session.add(application)
        db.session.commit()

        return redirect(url_for('.review_application',
            application_id=application_id, applicant=applicant))

@main.route('/review-application/<application_id>/<applicant>', methods=['GET', 'POST'])
@login_required
def review_application(application_id, applicant):
    if request.method == 'GET':
        user = current_user._get_current_object()
        application = Application.query.get(application_id)
        personal_form = PersonalInfoForm(obj=user)
        del personal_form.submit
        amount = application.amount
        term = application.terms
        if applicant == 'borrower':
            print(application.borrower_address)
            address_form = AddressForm(obj=application.borrower_address)
            finances_form = FinancesForm(obj=application.borrower_finances)
        elif applicant == 'guarantor':
            address_form = AddressForm(obj=application.guarantor_address)
            finances_form = FinancesForm(obj=application.guarantor_finances)
        del address_form.submit
        del finances_form.submit
        # terms = {
        #     "amount": amount,
        #     "rate": term.rate, 
        #     "installments": term.installments,
        #     "payment": -np.pmt(rate=term.rate/100, nper=term.installments,pv=amount)               
        #}
        terms_form = ReviewApplication()
        terms_form.amount.data = amount
        terms_form.rate.data = term.rate
        terms_form.installments.data = term.installments
        terms_form.payment.data = -np.pmt(rate=term.rate/100, nper=term.installments,pv=amount)
        return render_template('review_application.html',
            application=application_id, applicant=applicant,
            personal_form=personal_form, address_form=address_form,
            finances_form=finances_form, terms_form=terms_form)
    else:
        application = Application.query.get(application_id)
        application.created_at = datetime.utcnow()
        if applicant == "borrower":
            application.status = 1
        elif applicant == "guarantor":
            application.status = 2
        
        connection = application.connection
        connection.status = 'submitted'
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted.')
        return redirect(url_for('.index'))

@main.route('/manage-loans', methods=['GET', 'POST'])
@login_required
def manage_loans():
    user = current_user._get_current_object()
    borrower_loans = user.borrow_loans
    guarantor_loans = user.guarantee_loans
    return render_template('manage_loans.html',
        borrower_loans=borrower_loans, guarantor_loans=guarantor_loans)

@main.route('/loan-manager/<loan_id>', methods=['GET', 'POST'])
@login_required
def loan_manager(loan_id):
    loan = Loan.query.get(loan_id)
    return render_template('loan_manager.html', loan=loan)

@main.route('/make-payment/<payment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(payment_id):
    user = current_user._get_current_object()
    payment = Payment.query.get(payment_id)
    loan = payment.loan
    payment.payment_date = datetime.utcnow()
    payment.paid = 1
    if user == loan.guarantor:
        payment.paid_by_guarantor = 1
    loan.outstanding = loan.outstanding-payment.principal_pmt
    db.session.add(payment)
    db.session.add(loan)
    db.session.commit()
    flash('Your payment has been processed.')
    return redirect(url_for('.loan_manager',
        loan_id=loan.id))
    
