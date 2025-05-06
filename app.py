from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

def get_db_connection():
    db_path = Path(__file__).parent / "horses.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/zirgi")
def zirgi():
    conn = get_db_connection()
    
    selected_discipline = request.args.get('discipline')
    selected_competition = request.args.get('competition')

    disciplines = conn.execute("SELECT id, name FROM disciplines").fetchall()
    competitions = conn.execute("SELECT id, name FROM competition").fetchall()

    query = "SELECT * FROM horses"
    params = []

    if selected_discipline and selected_discipline != "":
        query += " WHERE disciplines_id = ?"
        params.append(selected_discipline)
    elif selected_competition and selected_competition != "":
        query += " WHERE competition_id = ?"
        params.append(selected_competition)

    horses = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template("horses.html", horses=horses, disciplines=disciplines, competitions=competitions, selected_discipline=selected_discipline, selected_competition=selected_competition)

@app.route("/horse/<int:horse_id>")
def horse_show(horse_id):
    conn = get_db_connection()
    horse = conn.execute(
        """
        SELECT 
            horses.id,
            horses.name AS horse_name,
            horses.breed,
            horses.age,
            horses.gender,
            horses.image,    
            owners.name || ' ' || owners.surname AS owner_fullname,
            categories.name AS category_name,
            disciplines.name AS discipline_name,
            competition.name AS competition_name,
            competition.location AS competition_location
        FROM horses
        LEFT JOIN owners ON horses.owner_id = owners.id
        LEFT JOIN categories ON horses.categories_id = categories.id
        LEFT JOIN disciplines ON horses.disciplines_id = disciplines.id
        LEFT JOIN competition ON horses.competition_id = competition.id
        WHERE horses.id = ?
        """,
        (horse_id,)
    ).fetchone()
    conn.close()
    return render_template("horse_show.html", horse=horse)


@app.route("/par-mums")
def par_mums():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)