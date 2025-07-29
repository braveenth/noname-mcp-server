# NoName MCP Server

## Overview

This project implements a Model-Context-Protocol (MCP) server that provides an intelligent, conversational interface for searching product data. The server leverages a Large Language Model (LLM) to understand natural language queries, interact with a product database stored in a CSV file, and return structured, relevant information. It's built with FastAPI and LangGraph, creating a powerful agent-based system for product discovery.

## Features

*   **Natural Language Product Search**: Ask for products in plain English (e.g., "find me some milk").
*   **Similar Product Recommendations**: Discover other products in the same aisle (e.g., "what's similar to butter?").
*   **Recipe Generation**: Get recipe ideas based on a list of ingredients.
*   **Product Link Retrieval**: Instantly get a direct link to the product page.
*   **Nutritional Information**: Access mock nutritional data for products.
*   **Extensible Toolset**: The server's capabilities can be easily expanded by adding new tools.

## Architecture

The server uses a LangGraph-based agent to process incoming requests. The agent decides which tool to use based on the user's query, executes the tool, and then formulates a final response.

## Data Sources

*   **`noname_products.csv`**: This file contains the core product data, and it was obtained from Kaggle. It includes columns such as `Name`, `aisle`, `brand`, `price`, and `Code` (the product identifier for generating links). The data is based on products from a Canadian supermarket.
*   **OpenAI API**: The `get_recipe` tool utilizes the `gpt-4` model from OpenAI to dynamically generate recipes from a given list of ingredients.

## Available Tools

| Tool                                | Description                                                              | Input Parameter(s) |
| ----------------------------------- | ------------------------------------------------------------------------ | ------------------ |
| `get_products`                      | Searches for products by name.                                           | `query` (string)   |
| `get_similar_products`              | Finds products in the same aisle as a given product.                     | `product_name` (string) |
| `get_recipe`                        | Generates a recipe from a list of ingredients.                           | `ingredients` (list of strings) |
| `get_nutritional_info`              | Returns (mock) nutritional information for a product.                    | `product_name` (string) |
| `get_products_with_links`           | Searches for products and includes a web link for each.                  | `query` (string)   |
| `get_similar_products_with_links`   | Finds similar products and includes a web link for each.                 | `product_name` (string) |

## API Endpoints

### List Available Tools

*   **`GET /tools/list`**
*   **Description**: Retrieves a list of all available tools, including their names, descriptions, and input schemas.
*   **Response**: A JSON array of `ToolDefinition` objects.

### Run the Agent

*   **`POST /mcp`**
*   **Description**: Sends a query to the MCP agent for processing.
*   **Request Body**:
    ```json
    {
      "query": "your natural language query here"
    }
    ```
*   **Response**: An `MCPResponse` object containing the agent's structured `SearchResponse`.

## Setup & Running the Server

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mcp_server
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the project root and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your-api-key-here"
    ```

4.  **Run the server:**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000
    ```
    The server will be accessible at `http://localhost:8000`.

## Usage Examples

### Get a list of tools

```bash
curl -X GET http://localhost:8000/tools/list
```

### Search for a product

```bash
curl -X POST http://localhost:8000/mcp \
-H "Content-Type: application/json" \
-d '{
  "query": "find me some eggs"
}'
```

### Find similar products with links

```bash
curl -X POST http://localhost:8000/mcp \
-H "Content-Type: application/json" \
-d '{
  "query": "find products similar to milk and give me links"
}'
```

## Project Structure

```
.
├── CSVs/
│   └── noname_products.csv   # Product data
├── product_search/
│   ├── __init__.py
│   ├── agent.py              # Defines the LangGraph agent
│   ├── graph.py              # Wires up the tools for the agent
│   ├── schema.py             # Pydantic models for data structures
│   └── tools.py              # Core tool implementations
├── .env                      # Environment variables (needs to be created)
├── app.py                    # FastAPI application and endpoints
├── Dockerfile                # Containerization configuration
└── requirements.txt          # Python dependencies
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please feel free to:

1.  **Open an issue**: Describe the issue or feature proposal.
2.  **Submit a pull request**: Fork the repository, make your changes, and submit a PR with a clear description of your work.
