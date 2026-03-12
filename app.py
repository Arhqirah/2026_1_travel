from flask import Flask, render_template, request, jsonify, session, redirect
import x
import uuid
import time
import os
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from settings import settings
 
 

from icecream import ic
ic.configureOutput(prefix=f'______ | ', includeContext=True)

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
app.config['SESSION_TYPE'] = settings.SESSION_TYPE
app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, '.session_data')
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
Session(app)

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DESTINATION_DATE_COLUMNS_READY = False


##############################
# Ensures the destinations table has start/end date columns.
def ensure_destination_date_columns():
    global DESTINATION_DATE_COLUMNS_READY
    if DESTINATION_DATE_COLUMNS_READY:
        return

    db, cursor = x.db()
    try:
        q = """
            SELECT column_name
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'destinations'
            AND column_name IN ('destination_start_date', 'destination_end_date')
        """
        cursor.execute(q)
        existing_columns = {row["column_name"] for row in cursor.fetchall()}

        if "destination_start_date" not in existing_columns:
            cursor.execute("ALTER TABLE destinations ADD COLUMN destination_start_date DATE NULL")

        if "destination_end_date" not in existing_columns:
            cursor.execute("ALTER TABLE destinations ADD COLUMN destination_end_date DATE NULL")

        db.commit()
        DESTINATION_DATE_COLUMNS_READY = True
    finally:
        cursor.close()
        db.close()


##############################
# Saves the uploaded destination image and returns the filename.
def save_destination_image():
    image = request.files.get("destination_image")
    if not image or image.filename == "":
        return ""

    filename = secure_filename(image.filename)
    if "." not in filename:
        raise Exception("company_exception destination_image_type")

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise Exception("company_exception destination_image_type")

    image_name = f"{uuid.uuid4().hex}.{extension}"
    image_path = os.path.join(UPLOAD_FOLDER, image_name)
    image.save(image_path)
    return image_name


##############################
# Deletes a destination image from disk (best effort).
def remove_destination_image(image_name):
    if not image_name:
        return
    # Only use basename to avoid accidental nested paths from DB values.
    safe_image_name = os.path.basename(str(image_name))
    image_path = os.path.join(UPLOAD_FOLDER, safe_image_name)
    try:
        if os.path.isfile(image_path):
            os.remove(image_path)
    except Exception as ex:
        # Cleanup errors should not break user flows.
        ic(ex)


##############################
# Renders tooltip HTML and clears previous tip content before showing a new one.
def tip_response(message, status="error", http_status=400):
    ___tip = render_template("___tip.html", status=status, message=message)
    return f"""
    <browser mix-replace="#tooltip"></browser>
    <browser mix-after-begin="#tooltip">{___tip}</browser>
    """, http_status


##############################
@app.errorhandler(RequestEntityTooLarge)
# Returns a friendly error when upload exceeds max size.
def handle_file_too_large(_error):
    return tip_response("Image too large (max 5MB)", "error", 400)

##############################
@app.get("/")
@x.no_cache
# Home route that sends the user to login or profile.
def show_home():
    try:
        user = session.get("user", "")
        if not user: return redirect("/login")
        return redirect("/profile")
    except Exception as ex:
        ic(ex)
        return "ups"

##############################
@app.get("/signup")
@x.no_cache
# Shows signup page for non-logged-in users.
def show_signup():
    try:
        user = session.get("user", "")
        if not user: return render_template("page_signup.html", user=user, x=x)
        return redirect("/profile")
    except Exception as ex:
        ic(ex)
        return "ups"

##############################
@app.post("/api-create-user")
# Creates a new user, validates input, and hashes the password.
def api_create_user():
    try:
        user_first_name = x.validate_user_first_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        user_hashed_password = generate_password_hash(user_password)
        #ic(user_hashed_password) #'scrypt:32768:8:1$JJDIZ1LxAosR1TEL$58a474e6865bdb852983e4c7eae057025232d6ea15af8be56642373cf644283a9ae7ee28c154e7443c8856e9ae7f77030c493d67012b38818038cad98a700fed'        

        user_pk = uuid.uuid4().hex
        user_created_at = int(time.time())


        db, cursor = x.db()
        q = "INSERT INTO users VALUES(%s, %s, %s ,%s, %s,%s)"
        cursor.execute(q, (user_pk, user_first_name, user_last_name, user_email, user_hashed_password, user_created_at))
        db.commit()

        form_signup = render_template("___form_signup.html", x=x)

        return f"""
        <browser mix-replace="form">{form_signup}</browser>
        <browser mix-redirect="/login"></browser> 
        """

    except Exception as ex:
        ic(ex)

        if "company_exception user_first_name" in str(ex):
            error_message = f"user first name {x.USER_FIRST_NAME_MIN} to {x.USER_FIRST_NAME_MAX} characters"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        if "company_exception user_last_name" in str(ex):
            error_message = f"user last name {x.USER_LAST_NAME_MIN} to {x.USER_LAST_NAME_MAX} characters"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        if "company_exception user_email" in str(ex):
            error_message = f"user email invalid"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        if "company_exception user_password" in str(ex):
            error_message = f"user password {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        if "Duplicate entry" in str(ex) and "user_email" in str(ex):
            error_message = "Email already exist"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        # Oooohh my gauwd! worst case
            error_message = "System under maintenance"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


        ##############################
@app.get("/login")
@x.no_cache
    # Shows login page for non-logged-in users.
def show_login():
    try:
        user = session.get("user", "")
        if not user: return render_template("page_login.html", user=user, x=x)
        return redirect("/profile")
    except Exception as ex:
        ic(ex)
        return "ups"

##############################
@app.post("/api-login")
# Logs the user in and stores user data in session.
def api_login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()




        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()
        if not user:
            error_message = "Invalid credentials 1"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400


        if not check_password_hash(user["user_password"], user_password):
            error_message = "Invalid credentials 2"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400


        user.pop("user_password")
        session["user"] = user
        ic(user)


        return f"""<browser mix-redirect="/profile"></browser> """

    except Exception as ex:
        ic(ex)

        if "company_exception user_email" in str(ex):
            error_message = f"user email invalid"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        if "company_exception user_password" in str(ex):
            error_message = f"user password {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400

        # Oooohh my gauwd! worst case
            error_message = "System under maintenance"
            ___tip = render_template("___tip.html", status="error", message=error_message)
            return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################

@app.get("/profile")
@x.no_cache
# Shows profile page with the latest destinations.
def show_profile():
    try:
        user = session.get("user", "")
        if not user: return redirect("/login")
        ensure_destination_date_columns()

        db, cursor = x.db()
        q = """
            SELECT destination_title, destination_country, destination_image_name,
                destination_start_date, destination_end_date
            FROM destinations
            WHERE destination_user_fk = %s
            ORDER BY destination_created_at DESC
            LIMIT 2
        """
        cursor.execute(q, (user["user_pk"],))
        recent_destinations = cursor.fetchall()

        return render_template("page_profile.html", user=user, x=x, recent_destinations=recent_destinations)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.get("/logout")
# Logs the user out by clearing the session.
def logout():
    try:
        session.clear()
        return redirect("/login")
    except Exception as ex:
        ic(ex)
        return "ups"


##############################
@app.get("/destinations")
@x.no_cache
# Shows all destinations for the logged-in user.
def show_destinations():
    try:
        user = session.get("user", "")
        if not user: return redirect("/login")
        ensure_destination_date_columns()

        db, cursor = x.db()
        q = """
             SELECT destination_pk, destination_title, destination_country,
                 destination_image_name, destination_start_date, destination_end_date,
                   destination_description, destination_created_at, destination_updated_at
            FROM destinations
            WHERE destination_user_fk = %s
            ORDER BY destination_created_at DESC
        """
        cursor.execute(q, (user["user_pk"],))
        destinations = cursor.fetchall()

        return render_template("page_destinations.html", user=user, x=x, destinations=destinations)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.get("/api-destinations-json")
# Returns all destinations for the logged-in user as JSON.
def api_destinations_json():
    try:
        user = session.get("user", "")
        if not user:
            return jsonify({"ok": False, "error": "not_authenticated"}), 400

        ensure_destination_date_columns()

        db, cursor = x.db()
        q = """
             SELECT destination_pk, destination_title, destination_country,
                 destination_image_name, destination_start_date, destination_end_date,
                   destination_description, destination_created_at, destination_updated_at
            FROM destinations
            WHERE destination_user_fk = %s
            ORDER BY destination_created_at DESC
        """
        cursor.execute(q, (user["user_pk"],))
        rows = cursor.fetchall()

        destinations = []
        for row in rows:
            destinations.append({
                "destination_pk": row["destination_pk"],
                "destination_title": row["destination_title"],
                "destination_country": row["destination_country"],
                "destination_image_name": row["destination_image_name"],
                "destination_start_date": row["destination_start_date"].isoformat() if row["destination_start_date"] else None,
                "destination_end_date": row["destination_end_date"].isoformat() if row["destination_end_date"] else None,
                "destination_description": row["destination_description"],
                "destination_created_at": row["destination_created_at"],
                "destination_updated_at": row["destination_updated_at"],
            })

        return jsonify({"ok": True, "destinations": destinations})
    except Exception as ex:
        ic(ex)
        return jsonify({"ok": False, "error": "system_under_maintenance"}), 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/api-destinations-create")
# Creates a new destination including dates, notes, and optional image.
def api_destinations_create():
    try:
        user = session.get("user", "")
        if not user: return "", 400
        ensure_destination_date_columns()

        destination_title = x.validate_destination_title()
        destination_country = x.validate_destination_country()
        destination_start_date, destination_end_date = x.validate_destination_dates()
        destination_description = x.validate_destination_description()
        destination_image_name = save_destination_image()

        destination_pk = uuid.uuid4().hex
        destination_created_at = int(time.time())
        destination_updated_at = destination_created_at

        db, cursor = x.db()
        q = """
            INSERT INTO destinations (
                destination_pk,
                destination_user_fk,
                destination_title,
                destination_country,
                destination_start_date,
                destination_end_date,
                destination_description,
                destination_image_name,
                destination_created_at,
                destination_updated_at
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(q, (
            destination_pk,
            user["user_pk"],
            destination_title,
            destination_country,
            destination_start_date,
            destination_end_date,
            destination_description,
            destination_image_name,
            destination_created_at,
            destination_updated_at,
        ))
        db.commit()

        destination = {
            "destination_pk": destination_pk,
            "destination_title": destination_title,
            "destination_country": destination_country,
            "destination_image_name": destination_image_name,
            "destination_start_date": destination_start_date,
            "destination_end_date": destination_end_date,
            "destination_description": destination_description,
        }
        destination_card = render_template("___destinations_card.html", destination=destination, x=x)
        form_create_destination = render_template("___form_destinations_create.html", x=x)

        return f"""
        <browser mix-replace="#form_destinations_create">{form_create_destination}</browser>
        <browser mix-replace="#destinations-empty"></browser>
        <browser mix-after-begin="#destinations-list">{destination_card}</browser>
        """

    except RequestEntityTooLarge:
        return tip_response("Image too large (max 5MB)", "error", 400)

    except Exception as ex:
        ic(ex)

        if "company_exception destination_title" in str(ex):
            return tip_response(f"destination title {x.DESTINATION_TITLE_MIN} to {x.DESTINATION_TITLE_MAX} characters", "error", 400)

        if "company_exception destination_country" in str(ex):
            return tip_response(f"destination country {x.DESTINATION_COUNTRY_MIN} to {x.DESTINATION_COUNTRY_MAX} characters", "error", 400)

        if "company_exception destination_description" in str(ex):
            return tip_response(f"description max {x.DESTINATION_DESCRIPTION_MAX} characters", "error", 400)

        if "company_exception destination_start_date" in str(ex) or "company_exception destination_end_date" in str(ex):
            return tip_response("date must use format YYYY-MM-DD", "error", 400)

        if "company_exception destination_date_range" in str(ex):
            return tip_response("end date must be on or after start date", "error", 400)

        if "company_exception destination_past_date" in str(ex):
            return tip_response("dates cannot be in the past", "error", 400)

        if "company_exception destination_image_type" in str(ex):
            return tip_response("Invalid image type (png, jpg, jpeg, webp, gif)", "error", 400)

        return tip_response("System under maintenance", "error", 500)

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/api-destinations-update/<destination_pk>")
# Updates an existing destination and handles optional new image.
def api_destinations_update(destination_pk):
    try:
        user = session.get("user", "")
        if not user: return "", 400
        ensure_destination_date_columns()

        destination_title = x.validate_destination_title()
        destination_country = x.validate_destination_country()
        destination_start_date, destination_end_date = x.validate_destination_dates()
        destination_description = x.validate_destination_description()
        destination_updated_at = int(time.time())

        db, cursor = x.db()
        q = """
            SELECT destination_image_name
            FROM destinations
            WHERE destination_pk = %s
            AND destination_user_fk = %s
        """
        cursor.execute(q, (destination_pk, user["user_pk"]))
        existing_destination = cursor.fetchone()
        if not existing_destination:
            return tip_response("Destination not found", "error", 400)

        old_image_name = existing_destination["destination_image_name"]
        uploaded_image_name = save_destination_image()
        destination_image_name = old_image_name
        if uploaded_image_name:
            destination_image_name = uploaded_image_name

        q = """
            UPDATE destinations
            SET destination_title = %s,
                destination_country = %s,
                destination_start_date = %s,
                destination_end_date = %s,
                destination_description = %s,
                destination_image_name = %s,
                destination_updated_at = %s
            WHERE destination_pk = %s
            AND destination_user_fk = %s
        """
        cursor.execute(q, (
            destination_title,
            destination_country,
            destination_start_date,
            destination_end_date,
            destination_description,
            destination_image_name,
            destination_updated_at,
            destination_pk,
            user["user_pk"],
        ))
        db.commit()

        if uploaded_image_name and old_image_name and uploaded_image_name != old_image_name:
            remove_destination_image(old_image_name)

        destination = {
            "destination_pk": destination_pk,
            "destination_title": destination_title,
            "destination_country": destination_country,
            "destination_image_name": destination_image_name,
            "destination_start_date": destination_start_date,
            "destination_end_date": destination_end_date,
            "destination_description": destination_description,
        }
        destination_card = render_template("___destinations_card.html", destination=destination, x=x)

        return f"""<browser mix-replace="#destination-card-{destination_pk}">{destination_card}</browser>"""

    except RequestEntityTooLarge:
        return tip_response("Image too large (max 5MB)", "error", 400)

    except Exception as ex:
        ic(ex)

        if "company_exception destination_title" in str(ex):
            return tip_response(f"destination title {x.DESTINATION_TITLE_MIN} to {x.DESTINATION_TITLE_MAX} characters", "error", 400)

        if "company_exception destination_country" in str(ex):
            return tip_response(f"destination country {x.DESTINATION_COUNTRY_MIN} to {x.DESTINATION_COUNTRY_MAX} characters", "error", 400)

        if "company_exception destination_description" in str(ex):
            return tip_response(f"description max {x.DESTINATION_DESCRIPTION_MAX} characters", "error", 400)

        if "company_exception destination_start_date" in str(ex) or "company_exception destination_end_date" in str(ex):
            return tip_response("date must use format YYYY-MM-DD", "error", 400)

        if "company_exception destination_date_range" in str(ex):
            return tip_response("end date must be on or after start date", "error", 400)

        if "company_exception destination_past_date" in str(ex):
            return tip_response("dates cannot be in the past", "error", 400)

        if "company_exception destination_image_type" in str(ex):
            return tip_response("Invalid image type (png, jpg, jpeg, webp, gif)", "error", 400)

        return tip_response("System under maintenance", "error", 500)

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/api-destinations-delete/<destination_pk>")
# Deletes a destination and removes the related image.
def api_destinations_delete(destination_pk):
    try:
        user = session.get("user", "")
        if not user: return "", 400

        db, cursor = x.db()
        q = """
            SELECT destination_image_name
            FROM destinations
            WHERE destination_pk = %s
            AND destination_user_fk = %s
        """
        cursor.execute(q, (destination_pk, user["user_pk"]))
        destination = cursor.fetchone()
        if not destination:
            return tip_response("Destination not found", "error", 400)

        q = """
            DELETE FROM destinations
            WHERE destination_pk = %s
            AND destination_user_fk = %s
        """
        cursor.execute(q, (destination_pk, user["user_pk"]))
        db.commit()

        remove_destination_image(destination["destination_image_name"])

        q = "SELECT COUNT(*) AS total FROM destinations WHERE destination_user_fk = %s"
        cursor.execute(q, (user["user_pk"],))
        remaining = cursor.fetchone()["total"]

        if remaining == 0:
            empty_state = '<p id="destinations-empty" class="card">No destinations yet. Create your first one above.</p>'
            return f"""
            <browser mix-replace="#destination-card-{destination_pk}"></browser>
            <browser mix-after-begin="#destinations-list">{empty_state}</browser>
            """

        return f"""<browser mix-replace="#destination-card-{destination_pk}"></browser>"""

    except Exception as ex:
        ic(ex)
        return tip_response("System under maintenance", "error", 500)

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()