import requests
from dotenv import load_dotenv
import os

load_dotenv()

SPOONACULAR_API_KEY  = os.environ["SPOONACULAR_API_KEY"]

# Set your Spoonacular API key here
BASE_URL = "https://api.spoonacular.com"

# Function to fetch recipes based on user query
def fetch_recipes_by_query(query):
    try:
        # Make a request to Spoonacular API to find recipes
        response = requests.get(
            f"{BASE_URL}/recipes/complexSearch",
            params={
                "query": query,
                "apiKey": SPOONACULAR_API_KEY,
                "number": 1,  # Get n number of recipes (you can adjust this)
            }
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        recipes = response.json()

        return recipes
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return []


# Function to fetch recipes based on user input ingredients
def fetch_recipes_by_ingredients(ingredients):
    try:
        # Make a request to Spoonacular API to find recipes
        response = requests.get(
            f"{BASE_URL}/recipes/findByIngredients",
            params={
                "ingredients": ingredients,
                "apiKey": SPOONACULAR_API_KEY,
                "number": 1,  # Get 5 recipes (you can adjust this)
            }
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        recipes = response.json()

        return recipes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipes: {e}")
        return []

# Function to fetch detailed recipe information (including cooking techniques and preparation times)
def fetch_recipe_details(recipe_id):
    try:
        # Make a request to get detailed recipe information
        response = requests.get(
            f"{BASE_URL}/recipes/{recipe_id}/information",
            params={
                "apiKey": SPOONACULAR_API_KEY,
            }
        )
        response.raise_for_status()
        recipe_details = response.json()
        print("recipe_details")
        print(recipe_details)

        # Extract cooking time, preparation time, and techniques
        cooking_time = recipe_details.get('readyInMinutes', 'Not available')
        preparation_time = recipe_details.get('preparationTime', 'Not available')
        cooking_techniques = recipe_details.get('cookingInstructions', 'Not available')

        print(f"\nDetails for {recipe_details['title']}:")
        print(f"Cooking Time: {cooking_time} minutes")
        print(f"Preparation Time: {preparation_time} minutes")
        print(f"Cooking Techniques: {cooking_techniques}\n")

        return recipe_details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe details: {e}")
        return {}
