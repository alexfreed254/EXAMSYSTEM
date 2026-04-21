from flask import Blueprint

trainer = Blueprint('trainer', __name__)

from app.trainer import routes
