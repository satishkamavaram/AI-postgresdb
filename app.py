from strands import Agent, tool
from strands_tools import calculator, current_time, http_request
from strands.models import BedrockModel
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv
import os
import asyncio
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from pymongo import MongoClient
import asyncpg

load_dotenv()

model_id =  os.environ.get('FM_MODEL_INFERENCE_ID')
aws_region = os.environ.get('AWS_REGION', 'us-west-2')
model = BedrockModel(
    model_id=model_id,
    region_name=aws_region,
    temperature=0.3,
    max_tokens=100,
)
model = OpenAIModel(
    #client_args={
    #    "api_key": "<KEY>",
    #},
    # **model_config
    model_id="gpt-4-turbo",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)




@tool
async def run_sql_query(agent_output):
    """
    Executes a SQL query from agent output.

    Args:
        agent_output (dict): Should have 'query' (str) and optionally 'params' (list/tuple).

    Returns:
        list: Query results as a list of dicts.
    """
    db_url = "postgresql://admin:admin@localhost:5432/ai"
    conn = await asyncpg.connect(db_url)
    try:
        query = agent_output["query"]
        params = agent_output.get("params", [])
        rows = await conn.fetch(query, *params)
        # Convert asyncpg Record objects to dicts
        return [dict(row) for row in rows]
    finally:
        await conn.close()

@tool
async def generate_sql_query(user_query: str) -> str:
    """
    Generates a valid SQL query for a given user prompt.

    Args:
        user_query (str): The user prompt or query in natural language

    Returns:
        str: Returns a SQL query for executing in PostgreSQL
    """
    prompt = """
    You are a PostgreSQL specialized agent.
    When given a question about the data, generate a SQL query that can be executed in PostgreSQL.
    Always specify the table(s) the query should be run on.
    Extract the following information and return ONLY valid JSON.
    If the query requires parameters (e.g., filtering by user, date, etc.), use parameter placeholders (%s) in the SQL and provide a "params" array with the values in order.

    {
      "query": "SQL query as a string",
      "params": [list of parameter values, or null if not needed]
    }

    RULES:
    - Retrieve only the JSON object, no explanatory text
    - If query is not generated, use null for strings/arrays
    - Use valid table names for the FROM/JOIN clauses
    - Use valid SQL syntax for PostgreSQL
    - For analytical questions (e.g., totals, maximums, rankings, or involving multiple tables), use SQL aggregation functions and JOINs as needed.
    - For questions involving multiple users or multiple sales or multiple customers, use a single query with the IN operator to match all relevant userids and maps all users corrects when joining.
    - Always try to answer with a single query when possible.
    - For questions involving "most", "highest", "top", or "for which customer", use the appropriate aggregation and join clauses.
    - Always output the SQL query as a string in the "query" field in JSON.
    - If no parameters are needed, set "params" to null.
    - sometimes user gives firstname , lastname and customer name in lower case , in sql query include to match case insensitive
    - For questions that require grouping results by user and including related details (such as customer names and sale dates), use aggregation functions like SUM for totals and array_agg for collecting related values (e.g., customer names, sale dates) per user.
    - The output should be one row per user, with total sales, a list of customer names, and a list of sale dates for that user.
    - Always order the results by total sales in descending order unless otherwise specified.
    - Use array_agg(DISTINCT ...) for customer names to avoid duplicates.
    - Ensure the query is compatible with PostgreSQL and can be executed as-is.
    - please use documentation if anytime you are confused and you need help with generating complex and optimized using this url https://neon.com/postgresql/tutorial and use http_request tool
    - If the user does not specify a threshold for "weak sales", you may calculate a threshold such as the 25th percentile or the minimum sales amount, and use that in the query. Mention this in your summary.
    
    Below are the PostgreSQL table schemas:

    users table:
        userid SERIAL PRIMARY KEY,
        firstname TEXT,
        lastname TEXT,
        emailid TEXT,
        gender TEXT

    address table:
        addressid SERIAL PRIMARY KEY,
        userid INT REFERENCES users(userid),
        street TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        country TEXT

    customers table:
        customerid SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT

    sales table:
        saleid SERIAL PRIMARY KEY,
        userid INT REFERENCES users(userid),
        customerid INT REFERENCES customers(customerid),
        date DATE,
        amount NUMERIC

    Example record for users: (1, 'Alice', 'Smith', 'alice.smith@example.com', 'Female')
    Example record for address: (1, '123 Main St', 'New York', 'NY', '10001', 'USA')
    Example record for customers: ('Acme Corp', 'contact@acmecorp.com', '555-1001', '100 Acme Way, New York, NY')
    Example record for sales: (1, 1, 101, '2024-01-05', 250.00)
    """
    agent = Agent(model=model, callback_handler=None, system_prompt=prompt, tools=[http_request])
    full_response = ""
    agent_stream = agent.stream_async(user_query)
    async for event in agent_stream:
        if "data" in event:
            chunk = event["data"]
            full_response += chunk
    print(f"SQL query from agent::: {full_response}")
    return full_response

async def process_streaming_response():
        prompt = """
        You are a specialized Postgres db agent.

        Your tasks:
        - When given a user question, use the generate_sql_query tool to create an optimized Postgres SQL query.
        - Use the run_sql_query tool to execute the postgres sql generated query.
        - After running the query, analyze and summarize the results in clear, concise natural language for the user.
        """
        agent = Agent(model=model,tools=[run_sql_query,generate_sql_query] ,callback_handler=None, system_prompt=prompt)
        """ 
        1. which users has done most sales share their names with total amount
        2. list total sales of each user in descending order . share usernames and customer names for each user and date of sale
        3. list all customers and their contact info
        4. show me largest sale happened in 2025
        5. show me largest sale happened in 2024
        6. show me largest sale happened in 2024. If identified, show me customer name, user name,  amount and date
        7. show me smallest sale . If identified, show me customer name, user name,  amount and date
        8. total amount sales ivy lee made in 2024
        9. number of sales made by ivy lee made in 2024.
        10. number of sales made by ivy and Eve in 2024
        11. show me a table view of sales done by Ivy and Eve in 2024
        12. what are the top 2 sales. share usernames and customer names for each user and date of sale
        """
        
        message = """
             what are the weak sales in year 2024. share usernames and customer names for each user and date of sale
            """
        # Get an async iterator for the agent's response stream
        agent_stream = agent.stream_async(message)

        # Process events as they arrive
        async for event in agent_stream:
            if "data" in event:
                # Print text chunks as they're generated
                print(event["data"], end="", flush=True)
        

asyncio.run(process_streaming_response())
