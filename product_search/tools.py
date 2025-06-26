import os
import json
import pandas as pd
from typing import List
from langchain_openai import ChatOpenAI
from .schema import Product, Recipe, NutritionalInfo, ToolDefinition, ToolInputSchema, ProductResponse

# Initialize the OpenAI model for recipe generation
llm = ChatOpenAI(temperature=0, model="gpt-4")

def get_products(query: str) -> str:
    """
    Searches for products in the CSV file based on a query and returns the results as a JSON string.
    """
    # Correctly locate the CSV file in the root directory
    # csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'noname_products.csv')
    csv_path = '/app/CSVs/noname_products.csv'

    # Fixed f-string syntax
    print(f"Searching for product: {query}")
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return json.dumps([])

    try:
        df = pd.read_csv(csv_path, dtype={'Article Number': str, 'Code': str})
        print(f"Loaded {len(df)} products from CSV")
        
        # Use case-insensitive search directly on the 'Name' column, after stripping whitespace
        matched_df = df[df['Name'].str.strip().str.contains(query, case=False, na=False)].copy()
        
        print(f"Found {len(matched_df)} matching products")

        # Limit the number of products to avoid exceeding the context length
        matched_df = matched_df.head(10)
        
        if matched_df.empty:
            return json.dumps([])

        # Rename columns to be valid Python identifiers
        matched_df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in matched_df.columns]
        
        products = [Product(**record) for record in matched_df.to_dict('records')]
        response_products = [ProductResponse(**p.dict()) for p in products]
        
        # Serialize the list of products to a JSON string
        return json.dumps([p.dict() for p in response_products])
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return json.dumps([])

def get_similar_products(product_name: str) -> str:
    """
    Finds products with names similar to the given product name and returns the results as a JSON string.
    """
    csv_path = '/app/CSVs/noname_products.csv'

    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return json.dumps([])

    try:
        df = pd.read_csv(csv_path, dtype={'Article Number': str, 'Code': str})
        
        # Find the aisle of the given product, after stripping whitespace
        product_row = df[df['Name'].str.strip() == product_name]
        if product_row.empty:
            print(f"Product '{product_name}' not found")
            return json.dumps([])
            
        aisle = product_row.iloc[0]['aisle']
        print(f"Found product in aisle: {aisle}")
        
        # Find other products in the same aisle, excluding the original product
        similar_df = df[(df['aisle'] == aisle) & (df['Name'].str.strip() != product_name)].head(10).copy()

        if similar_df.empty:
            print(f"No similar products found in aisle: {aisle}")
            return json.dumps([])

        # Rename columns to be valid Python identifiers
        similar_df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in similar_df.columns]
        
        products = [Product(**record) for record in similar_df.to_dict('records')]
        response_products = [ProductResponse(**p.dict()) for p in products]
        
        # Serialize the list of products to a JSON string
        return json.dumps([p.dict() for p in response_products])
        
    except Exception as e:
        print(f"Error finding similar products: {e}")
        return json.dumps([])

def get_recipe(ingredients: List[str]) -> str:
    """
    Generates a recipe from a list of ingredients and returns it as a JSON string.
    In the output, have each ingredient name on a new line and quoted with double asterisks (**)
    """
    try:
        prompt = f"Create a simple recipe using the following ingredients: {', '.join(ingredients)}. Please provide a title, the list of ingredients, and the instructions."
        response = llm.invoke(prompt)
        
        # This is a simplified parser. A more robust implementation would handle errors and edge cases.
        lines = response.content.strip().split('\n')
        title = lines[0].replace('Title: ', '').replace('# ', '').strip()
        
        ingredient_list = []
        instruction_text = ""
        
        is_ingredients = False
        is_instructions = False
        
        for line in lines[1:]:
            line_lower = line.lower()
            if "ingredients:" in line_lower or "ingredient list:" in line_lower:
                is_ingredients = True
                is_instructions = False
                continue
            elif "instructions:" in line_lower or "directions:" in line_lower or "method:" in line_lower:
                is_ingredients = False
                is_instructions = True
                continue
                
            if is_ingredients and line.strip():
                # Remove common list markers
                clean_ingredient = line.strip().lstrip('- *•').strip()
                if clean_ingredient:
                    ingredient_list.append(clean_ingredient)
            elif is_instructions and line.strip():
                instruction_text += line.strip() + "\n"
                
        recipe = Recipe(
            title=title,
            ingredients=ingredient_list,
            instructions=instruction_text.strip()
        )
        
        # Serialize the recipe to a JSON string
        return recipe.json()
        
    except Exception as e:
        print(f"Error generating recipe: {e}")
        # Return a fallback recipe
        fallback_recipe = Recipe(
            title="Simple Recipe",
            ingredients=ingredients,
            instructions="Combine ingredients and cook as desired."
        )
        return fallback_recipe.json()

def get_nutritional_info(product_name: str) -> str:
    """
    (Mock) Returns placeholder nutritional information for a given product as a JSON string.
    In a real application, this would query a nutritional database.
    """
    try:
        # Mock data - could be enhanced to vary based on product type
        nutritional_info = NutritionalInfo(
            calories=150.0,
            fat=10.5,
            protein=5.2,
            carbohydrates=20.1
        )
        # Serialize the nutritional info to a JSON string
        return nutritional_info.json()
        
    except Exception as e:
        print(f"Error getting nutritional info: {e}")
        return json.dumps({})

def get_products_with_links(query: str) -> str:
    """
    Searches for products and includes a web link for each product.
    """
    # csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'noname_products.csv')
    csv_path = '/app/CSVs/noname_products.csv'
    print(f"Searching for product with link: {query}")

    if not os.path.exists(csv_path):
        return json.dumps([])

    try:
        df = pd.read_csv(csv_path, dtype={'Article Number': str, 'Code': str})
        matched_df = df[df['Name'].str.strip().str.contains(query, case=False, na=False)].copy()
        matched_df = matched_df.head(10)

        if matched_df.empty:
            return json.dumps([])

        # Add the product link
        if 'Code' in matched_df.columns:
            matched_df['product_link'] = matched_df['Code'].apply(lambda code: f"https://www.realcanadiansuperstore.ca/p/{code}" if pd.notna(code) else None)
        else:
            matched_df['product_link'] = None

        matched_df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in matched_df.columns]
        
        products = [Product(**record) for record in matched_df.to_dict('records')]
        response_products = [ProductResponse(**p.dict()) for p in products]
        return json.dumps([p.dict() for p in response_products])

    except Exception as e:
        print(f"Error in get_products_with_links: {e}")
        return json.dumps([])

def get_similar_products_with_links(product_name: str) -> str:
    """
    Finds similar products and includes a web link for each.
    """
    csv_path = '/app/CSVs/noname_products.csv'

    if not os.path.exists(csv_path):
        return json.dumps([])

    try:
        df = pd.read_csv(csv_path, dtype={'Article Number': str, 'Code': str})
        product_row = df[df['Name'].str.strip() == product_name]
        if product_row.empty:
            return json.dumps([])
            
        aisle = product_row.iloc[0]['aisle']
        similar_df = df[(df['aisle'] == aisle) & (df['Name'].str.strip() != product_name)].head(10).copy()

        if similar_df.empty:
            return json.dumps([])

        # Add the product link
        if 'Code' in similar_df.columns:
            similar_df['product_link'] = similar_df['Code'].apply(lambda code: f"https://www.realcanadiansuperstore.ca/p/{code}" if pd.notna(code) else None)
        else:
            similar_df['product_link'] = None

        similar_df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in similar_df.columns]
        
        products = [Product(**record) for record in similar_df.to_dict('records')]
        response_products = [ProductResponse(**p.dict()) for p in products]
        return json.dumps([p.dict() for p in response_products])

    except Exception as e:
        print(f"Error in get_similar_products_with_links: {e}")
        return json.dumps([])

tool_definitions = [
    ToolDefinition(
        name="get_products",
        description="Searches for products in the CSV file based on a query and returns the results as a JSON string.",
        input_schema=ToolInputSchema(
            properties={
                "query": {"type": "string", "description": "The product to search for"}
            },
            required=["query"],
        ),
    ),
    ToolDefinition(
        name="get_similar_products",
        description="Finds products with names similar to the given product name and returns the results as a JSON string.",
        input_schema=ToolInputSchema(
            properties={
                "product_name": {
                    "type": "string",
                    "description": "The name of the product to find similar products for",
                }
            },
            required=["product_name"],
        ),
    ),
    ToolDefinition(
        name="get_recipe",
        description="Generates a recipe from a list of ingredients and returns it as a JSON string.",
        input_schema=ToolInputSchema(
            properties={
                "ingredients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of ingredients to use for the recipe",
                }
            },
            required=["ingredients"],
        ),
    ),
    ToolDefinition(
        name="get_nutritional_info",
        description="(Mock) Returns placeholder nutritional information for a given product as a JSON string.",
        input_schema=ToolInputSchema(
            properties={
                "product_name": {
                    "type": "string",
                    "description": "The name of the product to get nutritional information for",
                }
            },
            required=["product_name"],
        ),
    ),
    ToolDefinition(
        name="get_products_with_links",
        description="Searches for products and provides a web link for each.",
        input_schema=ToolInputSchema(
            properties={
                "query": {"type": "string", "description": "The product to search for"}
            },
            required=["query"],
        ),
    ),
    ToolDefinition(
        name="get_similar_products_with_links",
        description="Finds similar products and provides a web link for each.",
        input_schema=ToolInputSchema(
            properties={
                "product_name": {
                    "type": "string",
                    "description": "The name of the product to find similar products for",
                }
            },
            required=["product_name"],
        ),
    ),
]