import json
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
DB_PATH = BASE / "recipes.db"
JSON_PATH = BASE / "recipes.json"

def insert_recipes():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Optional: clear tables if re-importing
    # c.execute("DELETE FROM ingredients")
    # c.execute("DELETE FROM recipes")
    # conn.commit()

    for rec in data:
        name = rec.get("name")
        steps = "|".join(rec.get("steps", []))  # store steps as pipe-separated string
        c.execute("INSERT INTO recipes (name, steps) VALUES (?, ?)", (name, steps))
        recipe_id = c.lastrowid
        ingredients = rec.get("ingredients", [])
        for ing in ingredients:
            ing_norm = ing.strip().lower()
            c.execute("INSERT INTO ingredients (recipe_id, name) VALUES (?, ?)", (recipe_id, ing_norm))

    conn.commit()
    conn.close()
    print(f"Inserted {len(data)} recipes into {DB_PATH}")

if __name__ == "__main__":
    insert_recipes()
