import json
from langchain_core.tools import tool
from .tools import get_products, get_similar_products, get_recipe, get_nutritional_info, get_products_with_links, get_similar_products_with_links

# Define the tools for the agent
@tool
def product_search(query: str) -> str:
    """Searches for products and returns them as a JSON string."""
    products_json = get_products(query)
    products = json.loads(products_json)
    if not products:
        return json.dumps({"response": "No products found."})
    return products_json

@tool
def similar_products_search(product_name: str) -> str:
    """Searches for similar products and returns them as a JSON string."""
    products_json = get_similar_products(product_name)
    products = json.loads(products_json)
    if not products:
        return json.dumps({"response": "No similar products found."})
    return products_json

@tool
def product_search_with_links(query: str) -> str:
    """Searches for products and returns them with a web link as a JSON string."""
    products_json = get_products_with_links(query)
    products = json.loads(products_json)
    if not products:
        return json.dumps({"response": "No products found."})
    return products_json

@tool
def similar_products_search_with_links(product_name: str) -> str:
    """Searches for similar products and returns them with a web link as a JSON string."""
    products_json = get_similar_products_with_links(product_name)
    products = json.loads(products_json)
    if not products:
        return json.dumps({"response": "No similar products found."})
    return products_json

@tool
def recipe_generator(ingredients: list[str]) -> str:
    """Generates a recipe from a list of ingredients and returns it as a JSON string."""
    return get_recipe(ingredients)

@tool
def nutritional_info_getter(product_name: str) -> str:
    """Gets nutritional information for a product and returns it as a JSON string."""
    return get_nutritional_info(product_name)

# Create a tool executor
tools = [
    product_search,
    similar_products_search,
    recipe_generator,
    nutritional_info_getter,
    product_search_with_links,
    similar_products_search_with_links,
]