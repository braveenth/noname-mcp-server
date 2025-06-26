from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Product(BaseModel):
    date: int = Field(..., description="Date of the record")
    store_id: int = Field(..., description="ID of the store")
    code: str = Field(..., description="Product code")
    article_number: str = Field(..., description="Article number")
    name: str = Field(..., description="Name of the product")
    aisle: str = Field(..., description="Aisle where the product is located")
    brand: str = Field(..., description="Brand of the product")
    package_size: str = Field(..., description="Size of the product packaging")
    price: float = Field(..., description="Price of the product")
    unit: str = Field(..., description="Unit of measurement for the price")
    sale_type: str = Field(..., description="Type of sale (e.g., REGULAR, SPECIAL)")
    product_link: Optional[str] = Field(None, description="URL link to the product page")

class ProductResponse(BaseModel):
    date: int = Field(..., description="Date of the record")
    store_id: int = Field(..., description="ID of the store")
    code: str = Field(..., description="Product code")
    article_number: str = Field(..., description="Article number")
    name: str = Field(..., description="Name of the product")
    aisle: str = Field(..., description="Aisle where the product is located")
    brand: str = Field(..., description="Brand of the product")
    package_size: str = Field(..., description="Size of the product packaging")
    price: float = Field(..., description="Price of the product")
    unit: str = Field(..., description="Unit of measurement for the price")
    sale_type: str = Field(..., description="Type of sale (e.g., REGULAR, SPECIAL)")
    product_link: Optional[str] = Field(None, description="URL link to the product page")

class Recipe(BaseModel):
    title: str = Field(..., description="Title of the recipe")
    ingredients: List[str] = Field(..., description="List of ingredients")
    instructions: str = Field(..., description="Cooking instructions")

class NutritionalInfo(BaseModel):
    calories: Optional[float] = Field(None, description="Calories per serving")
    fat: Optional[float] = Field(None, description="Fat per serving in grams")
    protein: Optional[float] = Field(None, description="Protein per serving in grams")
    carbohydrates: Optional[float] = Field(None, description="Carbohydrates per serving in grams")

class SearchRequest(BaseModel):
    query: str = Field(..., description="The user's search query")

class SearchResponse(BaseModel):
    products: Optional[List[ProductResponse]] = None
    recipe: Optional[Recipe] = None
    similar_products: Optional[List[Product]] = None
    nutritional_info: Optional[NutritionalInfo] = None
    summary: str = Field(..., description="A summary of the results")

class MCPRequest(BaseModel):
    query: str

class MCPResponse(BaseModel):
    data: SearchResponse

class ToolInputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = Field(..., description="Schema for individual parameters")
    required: List[str] = Field(..., description="List of required parameter names")

class ToolDefinition(BaseModel):
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="A description of what the tool does")
    input_schema: ToolInputSchema = Field(..., description="The input schema for the tool")