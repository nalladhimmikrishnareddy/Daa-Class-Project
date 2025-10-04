import sqlite3

DB = "recipes.db"

# Very simple keyword rules
RULES = {
    "cuisine": {
        "Indian": ["paneer", "masala", "dal", "biryani"],
        "Italian": ["pasta", "spaghetti", "pizza"],
        "Chinese": ["noodles", "soy sauce", "manchurian"],
    },
    "diet": {
        "Non-Vegetarian": ["chicken", "mutton", "beef", "fish"],
        "Vegetarian": ["paneer", "cheese", "egg"],
        "Vegan": ["tofu", "lentil", "beans"],
    },
    "prep_time": {
        "Under30": ["salad", "sandwich", "toast"],
        "Over60": ["biryani", "slow", "roast"],
    }
}

def ensure_columns(cur):
    cur.execute("PRAGMA table_info(recipes)")
    cols = [c[1] for c in cur.fetchall()]
    if "cuisine" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN cuisine TEXT;")
    if "diet" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN diet TEXT;")
    if "prep_time" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN prep_time TEXT;")

def tag_text(text, rules):
    text = (text or "").lower()
    for tag, keywords in rules.items():
        for k in keywords:
            if k in text:
                return tag
    return None

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    ensure_columns(cur)

    cur.execute("SELECT r.id, r.name, GROUP_CONCAT(i.name) FROM recipes r LEFT JOIN ingredients i ON r.id=i.recipe_id GROUP BY r.id")
    rows = cur.fetchall()

    updates = 0
    for rid, name, ing_csv in rows:
        text = f"{name} {ing_csv}".lower()
        cuisine = tag_text(text, RULES["cuisine"]) or "Various"
        diet = tag_text(text, RULES["diet"]) or "Unknown"
        prep = tag_text(text, RULES["prep_time"]) or "30to60"

        cur.execute("UPDATE recipes SET cuisine=?, diet=?, prep_time=? WHERE id=?", (cuisine, diet, prep, rid))
        updates += 1

    conn.commit()
    conn.close()
    print(f"Tagged {updates} recipes successfully.")

if __name__ == "__main__":
    main()
