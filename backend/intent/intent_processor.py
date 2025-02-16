from datetime import datetime

# Simple intent processor that gives response relevant to user query about weather or time.
def process_query(query):
    if "weather" in query:
        return "The weather is sunny and beautiful today!"
    elif "time" in query:
        return f"The current time is {datetime.now()}"
    else:
        return "I'm sorry, I don't understand that query."