from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask import jsonify
import wikipedia
from transformers import pipeline
import re
import random
from dateutil.parser import parse
import math
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect # Import CSRFProtect


app = Flask(__name__)
# Database Configuration
default_db_uri = 'mysql+mysqlconnector://root:@localhost/PAL_WEB_APP'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_uri)
if app.config['SQLALCHEMY_DATABASE_URI'] == default_db_uri:
    app.logger.info("Using default local MySQL database.")
else:
    try:
        uri_parts = app.config['SQLALCHEMY_DATABASE_URI'].split('://')
        scheme = uri_parts[0]
        rest = uri_parts[1]
        username_part = rest.split('@')[0].split(':')[0]
        host_part = rest.split('@')[1].split('/')[0] if '@' in rest and '/' in rest.split('@')[1] else "details_unavailable"
        app.logger.info(f"Using DATABASE_URL from environment. Scheme: {scheme}, User: {username_part}, Host: {host_part}")
    except Exception:
        app.logger.info("Using DATABASE_URL from environment (details redacted).")
