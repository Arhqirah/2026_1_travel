# Kode Noter

Denne note forklarer de linjer/monstre, der bruges mest i `app.py`, `x.py` og `static/app.js`.
Formatet er lavet som "linje for linje" i praksis: kort forklaring af hver typisk linje i flowet.

## 1. Typisk Flask-route i `app.py`

Eksempel-monster:
```python
@app.get("/profile")
@x.no_cache
def show_profile():
    try:
        user = session.get("user", "")
        if not user: return redirect("/login")

        db, cursor = x.db()
        q = "SELECT ... WHERE destination_user_fk = %s"
        cursor.execute(q, (user["user_pk"],))
        rows = cursor.fetchall()

        return render_template("page_profile.html", user=user, rows=rows)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
```

Linje-forklaring:
- `@app.get(...)` / `@app.post(...)`: Binder funktionen til en URL + HTTP-metode.
- `@x.no_cache`: Forhindrer browser-cache pa sider med login/session-data.
- `def show_profile():`: Selve route-handleren.
- `try:`: Beskytter flowet sa fejl kan fanges kontrolleret.
- `user = session.get("user", "")`: Henter logget bruger fra session.
- `if not user: return redirect("/login")`: Stopper adgang for ikke-loggede brugere.
- `db, cursor = x.db()`: Opretter DB-forbindelse + cursor.
- `q = "..."`: SQL-foresporgsel gemmes i variabel (lettere at laese).
- `cursor.execute(q, (...))`: Korer SQL med sikre parametre.
- `fetchall()` / `fetchone()`: Henter mange eller en enkelt raekke.
- `return render_template(...)`: Returnerer HTML-side med data.
- `except Exception as ex`: Fang generel fejl.
- `ic(ex)`: Logger fejl i terminal for debugging.
- `finally:`: Korer altid, uanset succes/fejl.
- `if "cursor" in locals(): cursor.close()`: Luk cursor kun hvis oprettet.
- `if "db" in locals(): db.close()`: Luk DB kun hvis oprettet.

## 2. Mest brugte valideringslinjer i `x.py`

Eksempel-monster:
```python
value = request.form.get("destination_title", "").strip()
if not re.match(REGEX_DESTINATION_TITLE, value):
    raise Exception("company_exception destination_title")
return value
```

Linje-forklaring:
- `request.form.get(..., "")`: Henter felt sikkert fra form-data.
- `.strip()`: Fjerner mellemrum i start/slut.
- `re.match(...)`: Tjekker om input matcher regel.
- `raise Exception("company_exception ...")`: Sender kontrolleret fejl op til `app.py`.
- `return value`: Returnerer valideret data.

## 3. Dato-validering (vigtig ved inspect/manipulation)

Eksempel-monster:
```python
if not re.match(REGEX_DESTINATION_DATE, destination_start_date):
    raise Exception("company_exception destination_start_date")
date.fromisoformat(destination_start_date)
```

Linje-forklaring:
- Regex tjekker format `YYYY-MM-DD`.
- `date.fromisoformat(...)` tjekker at datoen faktisk findes (fx afviser `2026-02-31`).
- I `app.py` tjekkes der oveni:
- ingen dato i fortiden (`< date.today()`)
- slutdato ikke foer startdato.

## 4. Mest brugte SQL-linjer

Eksempel-monster:
```python
cursor.execute(q, (destination_pk, user["user_pk"]))
db.commit()
```

Linje-forklaring:
- Parametre gives separat i tuple, ikke via string-concat (god sikkerhed).
- `db.commit()` gemmer `INSERT/UPDATE/DELETE` permanent.
- Ved `SELECT` bruges normalt ikke `commit()`.

## 5. Mest brugte fejlhaandterings-linjer i `app.py`

Eksempel-monster:
```python
if "company_exception destination_country" in str(ex):
    error_message = "..."
    ___tip = render_template("___tip.html", status="error", message=error_message)
    return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 400
```

Linje-forklaring:
- Matcher pa intern fejlkode i exception-teksten.
- Bygger en bruger-venlig fejlbesked.
- Returnerer HTML-snippet med HTTP-status 400 (bad request).

## 6. Mest brugte session/auth-linjer

- `session["user"] = user`: Gemmer bruger i session ved login.
- `user.pop("user_password")`: Fjerner hash fra session-data.
- `session.clear()`: Logger ud.
- `if not user: return redirect("/login")`: Route-guard.

## 7. Mest brugte upload-linjer

Eksempel-monster:
```python
filename = secure_filename(image.filename)
extension = filename.rsplit(".", 1)[1].lower()
image_name = f"{uuid.uuid4().hex}.{extension}"
image.save(image_path)
```

Linje-forklaring:
- `secure_filename(...)`: Renser filnavn.
- `rsplit(".", 1)`: Finder filtype sikkert fra sidste punktum.
- `uuid4().hex`: Giver unikt filnavn (undgar overlap).
- `image.save(...)`: Gemmer filen fysisk i `static/uploads`.

## 8. Mest brugte JS-linjer i `static/app.js`

Bekraeftelsesflow:
- `event.preventDefault()` + `event.stopPropagation()`: Stopper standard submit/click.
- `appConfirm(...).then(...)`: Viser custom modal foer handling.
- `requestSubmit()`: Triggerer form-submit programmatisk efter bekraeftelse.

Dato-flow:
- `startInput.min = todayIso`: Ingen startdato i fortiden.
- `endInput.min = max(today, startdato)`: Slutdato kan ikke vaere foer start eller i fortiden.
- Hvis slutdato bliver ugyldig: feltet nulstilles.

## 9. Hurtig ordbog (de 10 vigtigste)

- `locals()`: Lokale variabler i nuvaerende funktion.
- `session`: Browser-session pa serveren (login-state).
- `redirect(...)`: Sender bruger til en anden URL.
- `render_template(...)`: Renderer HTML fra en Jinja-template.
- `cursor.execute(...)`: Korer SQL.
- `fetchone()/fetchall()`: Henter DB-resultater.
- `commit()`: Gemmer DB-aendringer.
- `finally`: Korer altid, bruges til cleanup.
- `raise Exception(...)`: Stopper flow og sender fejl op.
- `@decorator`: Udvider en funktion med ekstra adfaerd.

## 10. Din konkrete linje

`if not user: return redirect("/login")`

Kort betydning:
- Hvis der ikke findes en bruger i sessionen, ma route ikke vises.
- Brugeren sendes derfor til login.

Praktisk betydning:
- Beskytter private sider mod uautoriseret adgang.

## 11. Forskel pa `import time` og `import datetime`

Kort version:
- `import time`: Bruges mest til timestamps, ventetid og maaling af varighed.
- `import datetime`: Bruges mest til rigtige datoer/tidspunkter og datologik.

### `import time`

Typiske linjer:
```python
import time

now_ts = int(time.time())
time.sleep(1)
```

Forklaring:
- `time.time()`: Antal sekunder siden epoch (1970-01-01 UTC).
- God til `created_at` / `updated_at` felter som heltal.
- `time.sleep(...)`: Pauser kode i x sekunder.

### `import datetime`

Typiske linjer:
```python
from datetime import date

today = date.today()
d = date.fromisoformat("2026-03-09")
```

Forklaring:
- `date.today()`: Dagens dato som dato-objekt.
- `date.fromisoformat(...)`: Parser streng i `YYYY-MM-DD` til dato.
- God til validering som: ingen dato i fortiden, slutdato efter startdato.

### Hvad passer til dit projekt?

- Brug `time` til Unix timestamps i DB (fx `destination_created_at`).
- Brug `datetime/date` til dato-felter og sammenligninger (fx start/slutdato).
