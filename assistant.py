from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import json
import time
import requests

_ : bool = load_dotenv(find_dotenv())

client = OpenAI()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
FMP_API_KEY = os.environ["FMP_API_KEY"]

# Define financial statement functions
def get_income_statement(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

def get_balance_sheet(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

def get_cash_flow_statement(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

def get_key_metrics(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

def get_financial_ratios(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

def get_financial_growth(ticker, period, limit):
    url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    return json.dumps(response.json())

# Map available functions
available_functions = {
    "get_income_statement": get_income_statement,
    "get_balance_sheet": get_balance_sheet,
    "get_cash_flow_statement": get_cash_flow_statement,
    "get_key_metrics": get_key_metrics,
    "get_financial_ratios": get_cash_flow_statement,
    "get_financial_growth": get_financial_ratios
}

import time

# Define the main function
def run_assistant(user_message):

    # Creating an assistant with specific instructions and tools
    assistant = client.beta.assistants.create(
        instructions="Act as a financial analyst by accessing detailed financial data through the Financial Modeling Prep API. Your capabilities include analyzing key metrics, comprehensive financial statements, vital financial ratios, and tracking financial growth trends. ",
        model="gpt-3.5-turbo-1106",
        tools=[
            {
                "type": "function", 
                "function": {
                    "name": "get_income_statement", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_balance_sheet", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_cash_flow_statement", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_key_metrics", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_cash_flow_statement", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_financial_ratios", 
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "ticker": {"type": "string"}, 
                            "period": {"type": "string"}, 
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
        ]
    )

    # Creating a new thread
    thread = client.beta.threads.create()

    # Adding a user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # Running the assistant on the created thread
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)


    answersList = []
    
    # Loop until the run completes or requires action
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Add run steps retrieval here
        run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id, run_id=run.id)
        print("Run Steps:", run_steps)

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name in available_functions:
                    function_to_call = available_functions[function_name]

                    try:
                        output = function_to_call(**function_args)
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output,
                        })
                    except:
                        pass

            # Submit tool outputs and update the run
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status == "completed":
            # List the messages to get the response
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                role_label = "User" if message.role == "user" else "Assistant"
                message_content = message.content[0].text.value
                print(f"{role_label}: {message_content}\n")

                if(role_label=="Assistant"):
                    answersList.append(message_content)

            break  # Exit the loop after processing the completed run

        elif run.status == "failed":
            print("Run failed.")
            break

        elif run.status in ["in_progress", "queued"]:
            print(f"Run is {run.status}. Waiting...")
            time.sleep(5)  # Wait for 5 seconds before checking again

        else:
            print(f"Unexpected status: {run.status}")
            break
    return answersList