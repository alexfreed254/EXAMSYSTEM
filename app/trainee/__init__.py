from flask import Blueprint

trainee = Blueprint('trainee', __name__)

from app.trainee import routes
