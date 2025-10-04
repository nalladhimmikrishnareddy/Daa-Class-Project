# explore_db.py
import sqlite3

DB_PATH = "recipes.db"

def explore_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Count recipes
    recipe_count = c.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    print(f"Total recipes in DB: {recipe_count}")

    # Count ingredients
    ingredient_count = c.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    print(f"Total ingredient rows in DB: {ingredient_count}")

    # List distinct ingredients (first 30 only)
    ingredients = c.execute("SELECT DISTINCT name FROM ingredients ORDER BY name LIMIT 30").fetchall()
    print("\nSample ingredients (first 30):")
    for ing in ingredients:
        print(" -", ing[0])

    # Show some recipes with their ingredients
    print("\nSample recipes with ingredients:")
    rows = c.execute("""
        SELECT r.id, r.name, GROUP_CONCAT(i.name, ', ')
        FROM recipes r
        JOIN ingredients i ON r.id = i.recipe_id
        GROUP BY r.id
        ORDER BY r.id
        LIMIT 10
    """).fetchall()

    for r in rows:
        print(f"{r[0]}: {r[1]}")
        print(f"   Ingredients: {r[2]}")

    conn.close()

if __name__ == "__main__":
    explore_db()
