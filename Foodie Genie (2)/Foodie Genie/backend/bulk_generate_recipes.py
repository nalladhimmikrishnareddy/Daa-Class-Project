"""
bulk_generate_recipes.py
Generates N synthetic recipes and stores them in recipes.db.
Usage:
    python bulk_generate_recipes.py        # generates 500 recipes by default
    python bulk_generate_recipes.py 1000   # generates 1000 recipes
"""
import sqlite3
import random
import sys
from pathlib import Path

BASE = Path(__file__).parent
DB_PATH = BASE / "recipes.db"

# Pool of ingredients to pick from (common pantry + veggies + proteins + spices)
ING_POOL = [
    "rice","pasta","flour","bread","egg","milk","butter","cheese","yogurt","cream",
    "tomato","onion","garlic","ginger","potato","carrot","peas","beans","spinach",
    "cabbage","capsicum","broccoli","mushroom","corn","bell pepper","chili","lemon",
    "chicken","mutton","fish","paneer","tofu","soy sauce","vinegar","olive oil","vegetable oil",
    "salt","pepper","turmeric","cumin","coriander","garam masala","chili powder","sugar",
    "honey","peanut","almond","walnut","sesame","oats","banana","apple","orange",
    "cocoa","chocolate","vanilla","potato chips","spring roll sheet","noodles","soy milk",
    "black pepper","bay leaf","cinnamon","cardamom","clove","mustard seeds","fenugreek"
]

# Step templates: we'll form 2-4 steps by combining templates with ingredients
STEP_TEMPLATES = [
    "Prepare the main ingredient(s): {main}.",
    "Chop and clean vegetables: {vegs}.",
    "Heat oil in a pan and add spices: {spices}.",
    "Sauté onions and garlic until golden.",
    "Add {main} and cook until done.",
    "Boil {grain} until tender.",
    "Mix ingredients together and simmer for a few minutes.",
    "Bake in preheated oven at 180°C for 20-30 minutes.",
    "Garnish with coriander/lemon and serve hot.",
    "Whisk eggs and pour into pan, cook until set.",
    "Combine all ingredients and blend until smooth.",
    "Fry until golden and crisp, then drain on paper towels.",
    "Layer ingredients and steam for 10-15 minutes."
]

def create_tables(conn):
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS ingredients;")
    c.execute("DROP TABLE IF EXISTS recipes;")
    c.execute("""
    CREATE TABLE recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        steps TEXT
    )
    """)
    c.execute("""
    CREATE TABLE ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY(recipe_id) REFERENCES recipes(id)
    )
    """)
    conn.commit()

def gen_recipe_name(i, main_ing):
    # Generate a readable recipe name
    patterns = [
        f"{main_ing.title()} Delight",
        f"Easy {main_ing.title()} {random.choice(['Curry','Stir Fry','Bake','Salad','Sandwich'])}",
        f"{main_ing.title()} & Veg Mix",
        f"{random.choice(['Classic','Simple','Quick','Homestyle'])} {main_ing.title()}",
        f"{main_ing.title()} with {random.choice(['Garlic','Herbs','Spices','Butter'])}"
    ]
    return random.choice(patterns)

def gen_steps(main, vegs, grain, spices):
    # choose 2-4 step templates and fill them
    step_count = random.randint(3,5)
    chosen = random.sample(STEP_TEMPLATES, k=step_count)
    steps = []
    for t in chosen:
        s = t.format(main=main, vegs=", ".join(vegs) if vegs else "vegetables", grain=grain or "grain", spices=", ".join(spices) if spices else "spices")
        steps.append(s)
    return steps

def normalize(ing):
    return ing.strip().lower()

def generate_and_insert(n=500):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    create_tables(conn)

    inserted = 0
    for i in range(1, n+1):
        # pick 1 main protein/grain, 1-3 veggies, 1-2 spices, optional extras
        main = random.choice(["rice","pasta","bread","potato","chicken","paneer","tofu","egg","fish","mutton"])
        veg_count = random.choices([0,1,2,3], weights=[5,30,40,25])[0]  # bias to 1-2 veggies
        vegs = random.sample([ing for ing in ING_POOL if ing not in [main]], k=veg_count) if veg_count>0 else []
        spice_count = random.randint(1,3)
        spices = random.sample(["salt","pepper","turmeric","cumin","coriander","garam masala","chili powder","cinnamon","cardamom"], k=spice_count)
        extras = random.sample([ing for ing in ING_POOL if ing not in vegs and ing != main], k=random.choice([0,0,1,1,2]))  # sometimes extras
        # build ingredient list
        ingredients = [normalize(main)] + [normalize(x) for x in vegs + spices + extras]
        # create a name and steps
        name = gen_recipe_name(i, main)
        steps = gen_steps(main, vegs, grain=random.choice(["rice","pasta","quinoa","bread"]) if main in ["rice","pasta","bread","potato"] else None, spices=spices)
        steps_text = "|".join(steps)

        # insert recipe
        c.execute("INSERT INTO recipes (name, steps) VALUES (?, ?)", (name, steps_text))
        rid = c.lastrowid

        # insert ingredients
        for ing in ingredients:
            c.execute("INSERT INTO ingredients (recipe_id, name) VALUES (?, ?)", (rid, ing))

        inserted += 1
        if i % 50 == 0:
            conn.commit()  # commit in batches
            print(f"Inserted {i} recipes...")

    conn.commit()
    # final counts
    recipes_count = c.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    ingredients_count = c.execute("SELECT COUNT(*) FROM ingredients").fetchone()[0]
    conn.close()
    print("Done.")
    print("Recipes inserted:", recipes_count)
    print("Ingredients rows:", ingredients_count)

if __name__ == "__main__":
    # optional CLI argument for count
    try:
        N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    except:
        N = 500
    print(f"Generating {N} synthetic recipes into {DB_PATH}")
    generate_and_insert(N)
