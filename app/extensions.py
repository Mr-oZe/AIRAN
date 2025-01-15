from flask import session, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import flask_praetorian
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail

from datetime import datetime
from dateutil import parser
from html import unescape

import validators
import re
import bleach

class Extensions():
    def __init__(self):
        self.db = SQLAlchemy()
        self.guard = flask_praetorian.Praetorian()
        #self.auth = flask_praetorian
        self.cors = CORS()
        self.mail = Mail()
        self.session = session
        self.datetime = datetime
        self.validators = validators
        self.praetorian = flask_praetorian

    


extensiones = Extensions()