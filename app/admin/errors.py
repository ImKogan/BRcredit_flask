'''
errors.py

error handlers
'''

from flask import render_template, request, jsonify
from . import admin

@admin.app_errorhandler(403)
def forbidden(message):
    ''' handles 404 error '''
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden', 'message': message})
        response.status_code = 403
        return response
    return render_template('403.html'), 403

@admin.app_errorhandler(404)
def page_not_found(message):
    ''' handles 404 error '''
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found', 'message': message})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@admin.app_errorhandler(500)
def internal_server_error(message):
    ''' handles 500 error '''
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error', 'message': message})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
