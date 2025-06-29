import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bson import ObjectId
from pymongo import MongoClient, ASCENDING
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.schema import HumanMessage
import re
from urllib.parse import quote_plus
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
load_dotenv()

user = os.getenv("MONGO_USER") or ""
password_env = os.getenv("MONGO_PASS") or ""
password = quote_plus(password_env.encode())

# Configuration
GOOGLE_API_KEY = "AIzaSyBvfnsc7nLQX4FTnQMHRyq0Hjm5O_Dnu3Y"  # Replace with your actual API key
MONGODB_URI = f"mongodb+srv://{user}:{password}@ottelo.y5psic0.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "ottelodb"

class MongoDBAssistant:
    def __init__(self, api_key: str, mongodb_uri: str, db_name: str):
        # Initialize Gemini
        genai.configure(api_key=api_key)
        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash-exp",
        #     google_api_key=api_key,
        #     temperature=0.1
        # )
        self.llm = OllamaLLM(model="llama3.2:3b")
        
        # Initialize MongoDB
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        
        # Setup tools and agent
        self.tools = self.create_tools()
        self.agent = self.create_agent()
    
    def safe_json_loads(self, s: str) -> Dict:
        """Safely parse JSON, handling ObjectId and datetime"""
        try:
            # Replace ObjectId representations
            s = re.sub(r'ObjectId\(["\']([^"\']+)["\']\)', r'"\1"', s)
            return json.loads(s)
        except:
            return {}
    
    def serialize_doc(self, doc) -> Dict:
        """Serialize MongoDB document for JSON response"""
        if doc is None:
            return {}
        
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = [self.serialize_doc(item) if isinstance(item, dict) else 
                              str(item) if isinstance(item, ObjectId) else item for item in value]
            elif isinstance(value, dict):
                result[key] = self.serialize_doc(value)
            else:
                result[key] = value
        return result
    
    def query_database(self, query_description: str) -> str:
        """Execute database queries based on natural language description"""
        try:
            # Use LLM to convert natural language to MongoDB query
            prompt = f"""
            Convert this natural language query to MongoDB aggregation pipeline or find query.
            Database Schema:
            - hosts: {{name, phone_number, created_at}}
            - properties: {{host_id, name, location, default_price, rooms: [{{room_id, name, type, max_guests, is_active}}], created_at}}
            - bookings: {{room_id, property_id, guest_name, check_in, check_out, amount_paid, source, created_at}}
            - availability_calendar: {{room_id, date, is_available, price}}
            - guests: {{phone_number, ...}}
            
            Query: {query_description}
            
            Respond with ONLY a JSON object containing:
            - "collection": the collection name
            - "operation": "find", "aggregate", or "count"
            - "query": the MongoDB query/pipeline as a JSON object
            - "limit": number (optional, default 10)
            
            Example format:
            {{"collection": "bookings", "operation": "find", "query": {{}}, "limit": 10}}
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            if isinstance(response, list):
                content_str = "".join(str(item) for item in response)
            else:
                content_str = response
            query_data = self.safe_json_loads(content_str.strip())
            
            if not query_data:
                return "Could not parse the query. Please try rephrasing."
            
            collection_name = query_data.get("collection")
            operation = query_data.get("operation", "find")
            query = query_data.get("query", {})
            limit = query_data.get("limit", 10)
            
            # Get collection
            if not collection_name or not isinstance(collection_name, str):
                return "Invalid or missing collection name in the query."
            collection = self.db[collection_name]
            
            # Execute query
            if operation == "find":
                results = list(collection.find(query).limit(limit))
            elif operation == "aggregate":
                results = list(collection.aggregate(query))
            elif operation == "count":
                results = [{"count": collection.count_documents(query)}]
            else:
                return f"Unsupported operation: {operation}"
            
            # Serialize results
            serialized_results = [self.serialize_doc(doc) for doc in results]
            
            return json.dumps(serialized_results, indent=2)
            
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def update_database(self, update_description: str) -> str:
        """Execute database updates based on natural language description"""
        try:
            prompt = f"""
            Convert this natural language update request to MongoDB update operation.
            Database Schema:
            - hosts: {{name, phone_number, created_at}}
            - properties: {{host_id, name, location, default_price, rooms: [{{room_id, name, type, max_guests, is_active}}], created_at}}
            - bookings: {{room_id, property_id, guest_name, check_in, check_out, amount_paid, source, created_at}}
            - availability_calendar: {{room_id, date, is_available, price}}
            - guests: {{phone_number, ...}}
            
            Update Request: {update_description}
            
            Respond with ONLY a JSON object containing:
            - "collection": the collection name
            - "operation": "update_one", "update_many", "insert_one", or "delete_one"
            - "filter": the filter criteria (for updates/deletes)
            - "update": the update document (for updates)
            - "document": the document to insert (for inserts)
            
            Example format:
            {{"collection": "bookings", "operation": "update_one", "filter": {{"guest_name": "John"}}, "update": {{"$set": {{"amount_paid": 5000}}}}}}
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Fix: response is a string or list, not an object with 'content'
            if isinstance(response, list):
                content_str = "".join(str(item) for item in response)
            else:
                content_str = response
            update_data = self.safe_json_loads(content_str.strip())
            
            if not update_data:
                return "Could not parse the update request. Please try rephrasing."
            
            collection_name = update_data.get("collection")
            operation = update_data.get("operation")
            
            if not collection_name or not isinstance(collection_name, str):
                return "Invalid or missing collection name in the update request."
            collection = self.db[collection_name]
            
            if operation == "update_one":
                filter_criteria = update_data.get("filter", {})
                update_doc = update_data.get("update", {})
                result = collection.update_one(filter_criteria, update_doc)
                return f"Updated {result.modified_count} document(s)"
                
            elif operation == "update_many":
                filter_criteria = update_data.get("filter", {})
                update_doc = update_data.get("update", {})
                result = collection.update_many(filter_criteria, update_doc)
                return f"Updated {result.modified_count} document(s)"
                
            elif operation == "insert_one":
                document = update_data.get("document", {})
                if "created_at" not in document:
                    document["created_at"] = datetime.utcnow()
                result = collection.insert_one(document)
                return f"Inserted document with ID: {result.inserted_id}"
                
            elif operation == "delete_one":
                filter_criteria = update_data.get("filter", {})
                result = collection.delete_one(filter_criteria)
                return f"Deleted {result.deleted_count} document(s)"
                
            else:
                return f"Unsupported operation: {operation}"
                
        except Exception as e:
            return f"Error executing update: {str(e)}"
    
    def get_database_info(self, info_request: str = "") -> str:
        """Get information about the database structure and contents"""
        try:
            collections_info = {}
            for collection_name in ["hosts", "properties", "bookings", "availability_calendar", "guests"]:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                sample_doc = collection.find_one()
                collections_info[collection_name] = {
                    "count": count,
                    "sample_structure": self.serialize_doc(sample_doc) if sample_doc else {}
                }
            
            return json.dumps(collections_info, indent=2)
        except Exception as e:
            return f"Error getting database info: {str(e)}"
    
    def create_tools(self) -> List[Tool]:
        """Create LangChain tools for database operations"""
        return [
            Tool(
                name="query_database",
                description="Query the MongoDB database using natural language. Use this for SELECT-like operations, finding data, counting records, etc.",
                func=self.query_database
            ),
            Tool(
                name="update_database",
                description="Update, insert, or delete data in MongoDB using natural language. Use this for INSERT, UPDATE, DELETE operations.",
                func=self.update_database
            ),
            Tool(
                name="get_database_info",
                description="Get information about database structure, collections, and sample data. Use this when user asks about what data is available.",
                func=self.get_database_info
            )
        ]
    
    def create_agent(self):
        """Create the LangChain agent"""
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def chat(self, message: str) -> str:
        """Main chat interface"""
        try:
            response = self.agent.invoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"Error processing request: {str(e)}"

def main():
    """Main function to run the assistant"""
    # Initialize the assistant
    assistant = MongoDBAssistant(
        api_key=GOOGLE_API_KEY,
        mongodb_uri=MONGODB_URI,
        db_name=DATABASE_NAME
    )
    
    # Insert sample data
    
    print("🤖 MongoDB AI Assistant is ready!")
    print("You can ask questions like:")
    print("- 'Show me all bookings'")
    print("- 'What properties are in Jaipur?'")
    print("- 'Update Robin Shukla's booking amount to 5000'")
    print("- 'Add a new host named John with phone 9876543210'")
    print("- 'How many rooms are available?'")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        print("🤖 Assistant:", assistant.chat(user_input))
        print()

if __name__ == "__main__":
    # Install required packages first:
    # pip install pymongo google-generativeai langchain langchain-google-genai langchainhub
    
    main()