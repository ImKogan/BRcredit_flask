'''
views.py

views module for admin
'''

from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from . import admin
from .forms import TermForm
from .. import db
from ..models import Application, Terms, Loan, Payment
from ..decorators import admin_required

@admin.route('/pending-applications', methods=['GET', 'POST'])
@login_required
@admin_required
def pending_applications():
    ''' fetch and render pending applications'''
    applications = Application.query.filter_by(status=2).\
        order_by(Application.submitted_at.desc()).all()
    return render_template('admin/admin.html', applications=applications)

@admin.route('/approve-application/<application_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def approve_application(application_id):
    ''' approve application'''
    application = Application.query.get(application_id)
    application.status = 3
    db.session.add(application)
    loan = Loan(
        application=application,
        principal=application.amount,
        outstanding=application.amount,
        terms=application.terms,
        loan_date=datetime.utcnow(),
        borrower=application.borrower,
        guarantor=application.guarantor)
    db.session.add(loan)

    monthly_payment = -np.pmt(rate=loan.terms.rate/100,
                              nper=loan.terms.installments,
                              pv=loan.principal)

    for month in range(loan.terms.installments):
        ipmt = np.ipmt(rate=loan.terms.rate/100, per=month+1,
                       nper=loan.terms.installments, pv=loan.principal)
        ppmt = np.ppmt(rate=loan.terms.rate/100, per=month+1,
                       nper=loan.terms.installments, pv=loan.principal)
        payment = Payment(
            loan=loan,
            payment=Decimal(monthly_payment),
            principal_pmt=-ppmt,
            interest_pmt=-ipmt,
            scheduled_date=loan.loan_date + timedelta(days=30*(month+1)))
        db.session.add(payment)
    db.session.commit()
    flash('Application has been appproved.')
    return redirect(url_for('admin.pending_applications'))

@admin.route('/reject-application/<application_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reject_application(application_id):
    ''' reject application'''
    application = Application.query.get(application_id)
    application.status = 4
    db.session.add(application)
    db.session.commit()
    flash('Application has been rejected.')
    return redirect(url_for('admin.pending_applications'))

@admin.route('/manage-terms', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_terms():
    ''' manage available loan terms'''
    terms = Terms.query.all()
    return render_template('admin/manage_terms.html', terms=terms)

@admin.route('/edit-term/<term_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_term(term_id):
    ''' edit a term'''
    term = Terms.query.get(term_id)
    form = TermForm(obj=term)
    if request.method == "GET":
        return render_template('admin/term_form.html', form=form)
    else:
        if form.validate_on_submit():
            term.name = form.name.data
            term.installments = form.installments.data
            term.rate = form.rate.data
            db.session.add(term)
            db.session.commit()
            flash(flash('Term has been updated.'))
            return redirect(url_for('main.index'))

@admin.route('/term-form', methods=['GET', 'POST'])
@login_required
@admin_required
def term_form():
    ''' render term form'''
    form = TermForm()
    if form.validate_on_submit():
        term = Terms(
            name=form.name.data,
            installments=form.installments.data,
            rate=form.rate.data)
        db.session.add(term)
        db.session.commit()
        flash('Term has been added.')
        return redirect(url_for('main.index'))
    return render_template('admin/term_form.html', form=form)
