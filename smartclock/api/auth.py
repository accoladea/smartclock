from flask_httpauth import HTTPTokenAuth
from smartclock.model.models import User
from flask import g
from flask_restplus import abort

token_auth = HTTPTokenAuth()

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return abort(401, custom='Comes from API')
