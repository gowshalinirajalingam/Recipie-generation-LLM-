'''
It has the implementation for the LLM calls using FastAPI
'''


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from typing import List, Dict
from dotenv import load_dotenv
import os
import json
from API import fetch_recipes_by_query, fetch_recipe_details, fetch_recipes_by_ingredients
import re

load_dotenv()

# Load API Key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize FastAPI app
app = FastAPI()

# Define input schema
class RecipeRequest(BaseModel):
    user_input: str
    conversation_history: List[Dict[str, str]] = []

# Helper function to interact with OpenAI
def generate_response(prompt: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_dictionary_with_regex(json_string):
    # Use a regular expression to match the dictionary inside the JSON string
    match = re.search(r'\[({.*})\]', json_string)
    if match:
        # Extract the matched dictionary string
        dict_string = match.group(1)
        
        # Convert the extracted string to a Python dictionary
        return json.loads(f'[{dict_string}]')[0]  # Convert back to a list and get the first item
    else:
        return None  # Return None if no match is found

# Route for recipe innovation
@app.post("/generate_recipe/")
async def generate_recipe(request: RecipeRequest):
    try:

      print("user input:", request)

      # Construct the LLM prompt to generate the response #The prompt is hidden for privacy purposes
      prompt = f"""
"""
        
      response = generate_response(prompt)

      response_json = extract_dictionary_with_regex(response)
      print("response_json", response_json)


      recipe_query = response_json["recipe_query"]
      ingredients = response_json["ingredients"]
      conversational_response = response_json["conversational_response"]

      # Print the values of all keys
      print(f"Recipe Query: {recipe_query}")
      print(f"Ingredients: {ingredients}")
      print(f"Conversational Response: {conversational_response}")

      # Check if each value is null
      if recipe_query is not None:
          recipes = fetch_recipes_by_query(recipe_query)
          recipes = recipes['results']
          print("Query response:",recipes)

      elif ingredients is not None:
          recipes = fetch_recipes_by_ingredients(ingredients)
          print("ingredients response:",recipes)

      elif conversational_response is not None:
          print("Conversational Response.")
          response = response
          recipes = ""
      else:
          response = "I'm sorry, I couldn't find any recipes matching your request. Could you provide more details or try again?"


      #Format the recipe infotmation retrieved from API in required format
      recipe_information = []
      if recipes:
        print("Recipes Found:")
        for recipe in recipes:
            print(f" {recipe['title']} (ID: {recipe['id']})")
            info = fetch_recipe_details(recipe['id'])
            recipe_information.append(info)

        recipe_information_formated = []

        for recipes in recipe_information:
            prompt1 = f"""
            You are RecipeMate, a culinary assistant that processes recipe information and generates a structured recipe output in a specific format.

            You have received the following recipe information in JSON format:
            {recipes}

            Your task is to:
            1. Parse the JSON to understand the recipe details, such as:
              - Recipe title
              - Ingredients (with details like name, amount, and unit)
              - Cooking time and temperature
              - Cooking steps (each with step number, instruction, and an explanation for the step)
              - Cooking tips (if available)
            2. Use the parsed information to generate a structured output in the following format:
            ```json
            {{
              "recipe_title": "Recipe title here",
              "ingredients": [
                {{
                  "ingredient": "Ingredient name",
                  "amount": "Amount of ingredient",
                  "unit": "Unit of measurement"
                }},
                ...
              ],
              "cooking_time": "Time required to cook (e.g., 30 minutes)",
              "cooking_temperature": "Temperature setting (e.g., Medium heat)",
              "steps": [
                {{
                  "step_number": 1,
                  "instruction": "Step instruction here",
                  "explanation": "Explanation for why this step is important"
                }},
                ...
              ],
              "tips": [
                "Cooking tip 1",
                "Cooking tip 2",
                ...
              ]
            }}

            """

            
            stuctured_output = generate_response(prompt1)
            print("structured output", stuctured_output)

            #This prompt is written to generate the user understandable output from the formated json.
            prompt2 = f"""
You are RecipeMate, a highly intelligent and friendly bot that processes recipe information and generates detailed recipe instructions for users.

You have been given the following recipe information in JSON format:
{stuctured_output}

Your task is to:
1. Understand the JSON input and extract the relevant recipe details, such as:
   - Recipe title
   - Ingredients (with details such as name, amount, and unit)
   - Cooking time and temperature
   - Cooking steps (each step should be detailed, including why the step is important if possible)
   - Additional tips (if available)

2. Use the extracted information to create a *detailed and user-friendly recipe*. Ensure your output is easy to follow and includes the following sections:
   - *Recipe Title*: The name of the recipe.
   - *Ingredients*: A bulleted list of ingredients, including their amounts and units.
   - *Cooking Time and Temperature*: Mention the total cooking time and the required temperature settings.
   - *Steps*: Numbered step-by-step instructions. Each step should:
     - Include a clear instruction.
     - Optionally, explain why the step is important or provide a useful tip.
   - *Tips*: Additional cooking tips or suggestions (if provided in the input).

3. Innovate new recipes by:
   - Combining traditional methods with creative twists. For example:
     - Introduce fusion cuisine by incorporating elements from other cuisines.
     - Experiment with new cooking techniques or styles (e.g., roasting instead of sautéing).
   - Suggest ingredient substitutions or new approaches based on dietary preferences or availability. For instance:
     - Replace traditional ingredients with healthier alternatives (e.g., coconut cream instead of heavy cream for a vegan option).
     - Recommend alternatives for unavailable ingredients (e.g., lime zest instead of lime leaves).

4. If any information is missing in the input JSON (e.g., cooking temperature, tips), acknowledge it in the output and provide a reasonable placeholder or suggestion.

5. Provide an *innovative twist* to the recipe in a separate section titled *Innovative Ideas*. This section should:
   - Describe how the recipe can be enhanced or modified for a unique flavor profile.
   - Suggest experimental combinations or presentation styles to make the dish more exciting.

### Example Input JSON:
```json
{{
  "recipe_title": "Tropical Thai Chicken Curry",
  "ingredients": [
    {{
      "ingredient": "coconut milk",
      "amount": 14.0,
      "unit": "oz"
    }},
    ...
  ],
  "cooking_time": "45 minutes",
  "cooking_temperature": "Medium-high heat",
  "steps": [
    {{
      "step_number": 1,
      "instruction": "Heat half a can of coconut milk in a wok or heavy-bottomed skillet over medium-high heat until foaming.",
      "explanation": "This step is important for releasing the flavor of the coconut milk."
    }},
    ...
  ],
  "tips": []
}}

### Expected Output:
*Recipe Title*: Tropical Thai Chicken Curry

*Ingredients*:
- 14 ounce coconut milk
- ...

*Cooking Time and Temperature*:
- Total Time: 30 minutes
- Temperature: Medium heat

*Steps*:
1. *Heat half a can of coconut milk in a wok or heavy-bottomed skillet over medium-high heat until foaming.*  
   This step is important for releasing the flavor of the coconut milk.
   
2. ...

*Tips*:
- ...

*Innovative Ideas*:
- Add a touch of lemongrass or ginger to the curry for an enhanced flavor profile.
- Try serving this curry with a side of naan or flatbread for a fusion twist.
- Use tofu instead of chicken for a vegan alternative that still absorbs the rich curry flavors.

6. Generate the recipe using the information from the JSON input, formatted similarly to the expected output above. Ensure it is detailed, user-friendly, and includes creative twists or substitutions to make the recipe unique.

"""
            response = generate_response(prompt2)
            recipe_information_formated.append(response)
        
        response = recipe_information_formated[0]
      else:
        response = conversational_response
      
      print("response", response)
      print("type(response)",type(response))



      return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    

