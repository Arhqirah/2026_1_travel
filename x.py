from flask import request, make_response
import mysql.connector
import re # Regular expressions also called Regex
import calendar
from datetime import date
from functools import wraps
from country import COUNTRIES
from settings import settings

##############################
# Creates a database connection and returns db + dictionary cursor.
def db():
    try:
        db = mysql.connector.connect(
            host = settings.DB_HOST,
            user = settings.DB_USER,
            password = settings.DB_PASSWORD,
            database = settings.DB_NAME
        )
        cursor = db.cursor(dictionary=True)
        return db, cursor
    except Exception as e:
        print(e, flush=True)
        raise Exception("Database under maintenance", 500)


##############################
# Decorator that sets no-cache headers on a view.
def no_cache(view):
    @wraps(view)
    # Wrapper that calls the view and adds cache-control headers.
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache" #legacy fallback
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
REGEX_USER_FIRST_NAME = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"
# Validates first-name length from the form.
def validate_user_first_name():
    user_first_name = request.form.get("user_first_name", "").strip()
    if not re.match(REGEX_USER_FIRST_NAME, user_first_name):
        raise Exception("company_exception user_first_name")
    return user_first_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
REGEX_USER_LAST_NAME = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
# Validates last-name length from the form.
def validate_user_last_name():
    user_last_name = request.form.get("user_last_name", "").strip()
    if not re.match(REGEX_USER_LAST_NAME, user_last_name):
        raise Exception("company_exception user_last_name")
    return user_last_name


##############################
REGEX_USER_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
# Validates email format from the form.
def validate_user_email():
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_USER_EMAIL, user_email): 
        raise Exception("company_exception user_email")
    return user_email


##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
# Validates password length from the form.
def validate_user_password():
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password):
        raise Exception("company_exception user_password")
    return user_password


##############################
DESTINATION_TITLE_MIN = 2
DESTINATION_TITLE_MAX = 100
REGEX_DESTINATION_TITLE = f"^.{{{DESTINATION_TITLE_MIN},{DESTINATION_TITLE_MAX}}}$"
# Validates destination title.
def validate_destination_title():
    destination_title = request.form.get("destination_title", "").strip()
    if not re.match(REGEX_DESTINATION_TITLE, destination_title):
        raise Exception("company_exception destination_title")
    return destination_title


##############################
DESTINATION_COUNTRY_MIN = 2
DESTINATION_COUNTRY_MAX = 100
REGEX_DESTINATION_COUNTRY = f"^.{{{DESTINATION_COUNTRY_MIN},{DESTINATION_COUNTRY_MAX}}}$"
# Validates destination country.
def validate_destination_country():
    destination_country = request.form.get("destination_country", "").strip()
    if not re.match(REGEX_DESTINATION_COUNTRY, destination_country):
        raise Exception("company_exception destination_country")
    return destination_country


##############################
DESTINATION_DESCRIPTION_MIN = 0
DESTINATION_DESCRIPTION_MAX = 500
REGEX_DESTINATION_DESCRIPTION = f"^.{{{DESTINATION_DESCRIPTION_MIN},{DESTINATION_DESCRIPTION_MAX}}}$"
# Validates destination description/notes.
def validate_destination_description():
    destination_description = request.form.get("destination_description", "").strip()
    if not re.match(REGEX_DESTINATION_DESCRIPTION, destination_description):
        raise Exception("company_exception destination_description")
    return destination_description


##############################
REGEX_DESTINATION_DATE = r"^\d{4}-\d{2}-\d{2}$"

def _validate_destination_date_value(destination_date, field_name):
    if destination_date == "":
        return None

    if not re.match(REGEX_DESTINATION_DATE, destination_date):
        raise Exception(f"company_exception {field_name}")

    year, month, day = map(int, destination_date.split("-"))

    if year < 1 or year > 9999:
        raise Exception(f"company_exception {field_name}")

    if month < 1 or month > 12:
        raise Exception(f"company_exception {field_name}")

    max_day = calendar.monthrange(year, month)[1]
    if day < 1 or day > max_day:
        raise Exception(f"company_exception {field_name}")

    return destination_date


def _destination_date_to_date(destination_date):
    year, month, day = map(int, destination_date.split("-"))
    return date(year, month, day)


def validate_destination_dates():
    destination_start_date = validate_destination_start_date()
    destination_end_date = validate_destination_end_date()
    today = date.today()

    start_date_obj = None
    if destination_start_date:
        start_date_obj = _destination_date_to_date(destination_start_date)
        if start_date_obj < today:
            raise Exception("company_exception destination_past_date")

    end_date_obj = None
    if destination_end_date:
        end_date_obj = _destination_date_to_date(destination_end_date)
        if end_date_obj < today:
            raise Exception("company_exception destination_past_date")

    if start_date_obj and end_date_obj and end_date_obj < start_date_obj:
        raise Exception("company_exception destination_date_range")

    return destination_start_date, destination_end_date

# Validates start date in YYYY-MM-DD format or empty value.
def validate_destination_start_date():
    destination_start_date = request.form.get("destination_start_date", "").strip()
    return _validate_destination_date_value(destination_start_date, "destination_start_date")


##############################
# Validates end date in YYYY-MM-DD format or empty value.
def validate_destination_end_date():
    destination_end_date = request.form.get("destination_end_date", "").strip()
    return _validate_destination_date_value(destination_end_date, "destination_end_date")