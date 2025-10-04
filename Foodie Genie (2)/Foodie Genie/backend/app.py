from flask import Flask, render_template, request
import sqlite3
import math

app = Flask(__name__)

DB_PATH = "recipes.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/ingredients", methods=["GET", "POST"])
def ingredients():
    if request.method == "POST":
        raw = request.form.get("ingredients", "")
        ingredients = [i.strip().lower() for i in raw.split(",") if i.strip()]
        # Pass ingredients to recipes page
        return recipes(selected_ingredients=ingredients)
    return render_template("ingredients.html")


@app.route("/recipes")
def recipes(selected_ingredients=None):
    page = int(request.args.get("page", 1))
    per_page = 12

    cuisine_filter = request.args.get("cuisine")
    diet_filter = request.args.get("diet")
    time_filter = request.args.get("time")

    conn = get_db_connection()
    c = conn.cursor()

    # Base query
    query = """
        SELECT r.id, r.name, r.cuisine, r.diet, r.prep_time,
               GROUP_CONCAT(i.name)
        FROM recipes r
        LEFT JOIN ingredients i ON r.id = i.recipe_id
        GROUP BY r.id
    """
    clauses = []
    params = []

    # Ingredient filtering (from /ingredients form)
    if selected_ingredients:
        # require at least one match
        placeholders = " OR ".join(["i.name LIKE ?"] * len(selected_ingredients))
        clauses.append(f"({placeholders})")
        params.extend([f"%{ing}%" for ing in selected_ingredients])

    # Cuisine filter
    if cuisine_filter:
        values = cuisine_filter.split(",")
        placeholders = ",".join("?" * len(values))
        clauses.append(f"r.cuisine IN ({placeholders})")
        params.extend(values)

    # Diet filter
    if diet_filter:
        values = diet_filter.split(",")
        placeholders = ",".join("?" * len(values))
        clauses.append(f"r.diet IN ({placeholders})")
        params.extend(values)

    # Prep time filter (if you have prep_time stored as string like "Under30")
    if time_filter:
        values = time_filter.split(",")
        placeholders = ",".join("?" * len(values))
        clauses.append(f"r.prep_time IN ({placeholders})")
        params.extend(values)

    if clauses:
        query += " HAVING " + " AND ".join(clauses)

    rows = c.execute(query, params).fetchall()
    conn.close()

    total = len(rows)
    start = (page - 1) * per_page
    end = start + per_page
    rows = rows[start:end]

    # Format for template
    items = []
    for r in rows:
        recipe_id, name, cuisine, diet, prep_time, ing_csv = r
        items.append({
            "id": recipe_id,
            "name": name,
            "cuisine": cuisine,
            "diet": diet,
            "prep_time": prep_time,
            "ingredients": ing_csv.split(",") if ing_csv else [],
            "score": 0  # reserved if you want ingredient matching score
        })

    return render_template(
        "recipes.html",
        items=items,
        total=total,
        page=page,
        total_pages=math.ceil(total / per_page),
    )


if __name__ == "__main__":
    app.run(debug=True)
