import datetime
import json
import os
import random
import re

from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()

# ✅ Load API Key
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ✅ Dummy customer database
customer_data = {
    "users": [
        {
            "name": "Pankaj Jarial",
            "phone": "1234567890",
            "email": "pankaj@gmail.com",
            "purchase": {
                "product": "Voltas AC",
                "model": "VT-AC123",
                "purchase_date": "2024-08-15",
            },
        }
    ]
}

# ✅ Static Customer Support Contact
SUPPORT_NUMBER = "+91 9876543210"

# ✅ Dummy Order Tracking Data
order_tracking_data = {
    "123456": {
        "status": "In Transit",
        "expected_delivery": "2024-02-10",
        "last_location": "Delhi Warehouse",
    },
    "654321": {
        "status": "Delivered",
        "expected_delivery": "2024-01-25",
        "last_location": "Customer Address",
    },
}

# ✅ AI Model
llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
# ✅ Initialize Memory for Chat History
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# ✅ Function: Extract Phone & Email from User Input
def extract_contact_info(user_input):
    phone_match = re.search(r"\b\d{10}\b", user_input)
    email_match = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input
    )

    phone = phone_match.group() if phone_match else None
    email = email_match.group() if email_match else None

    return phone, email


# ✅ Function: Verify User
def verify_user(phone=None, email=None):
    for user in customer_data["users"]:
        if (phone and user["phone"] == phone) or (email and user["email"] == email):
            return user
    return None


# ✅ Function: Check Warranty Validity
def check_warranty(purchase_date):
    purchase_date = datetime.datetime.strptime(purchase_date, "%Y-%m-%d")
    warranty_period = datetime.timedelta(days=365)  # 1-year warranty
    expiry_date = purchase_date + warranty_period
    return expiry_date >= datetime.datetime.now()


# ✅ Function: Track Order
def track_order(order_id):
    if order_id in order_tracking_data:
        order = order_tracking_data[order_id]
        return f"📦 Order Status: {order['status']}\n🚚 Expected Delivery: {order['expected_delivery']}\n📍 Last Location: {order['last_location']}"
    return "❌ Order not found. Please check the tracking ID."


# ✅ Function: Register Complaint & Generate Ticket
def register_complaint(phone=None, email=None, issue=None, model=None):
    print(f"{phone= }, {email= }, {issue= }, {model= }")
    user = verify_user(phone, email)

    if user:
        if model and model != user["purchase"]["model"]:
            return "❌ Model number mismatch. Please check your product details."

        if check_warranty(user["purchase"]["purchase_date"]):
            ticket_id = f"TICKET-{random.randint(100000, 999999)}"
            return f"Complaint registered successfully! Your ticket ID is {ticket_id}."
        else:
            return f"❌ Warranty expired. Contact support at {SUPPORT_NUMBER}."
    return "User verification failed."


# ✅ AI-Based Query Processor (Ensure it always returns a valid response)
def ai_query_processor(query):
    response = llm.invoke(
        f"Analyze the user request and classify it. User said: {query}. "
        f"Decide if this is a 'track_order', 'register_complaint', 'general_support' or 'need_assistance'. "
        f"Reply with only one of these four labels."
    ).content

    valid_intents = [
        "track_order",
        "register_complaint",
        "general_support",
        "need_assistance",
    ]
    return response if response in valid_intents else "need_assistance"


# ✅ AI Tool: Handle Order Tracking
def order_tracking_tool(order_id: str):
    return track_order(order_id)


def general_support_tool(query):
    return llm.invoke(
        f"Show emotions on the user query, like apologies that you facing this issue or sympathy like emotions and guide them based on the bases of that.\n\nUser: {query}"
    ).content


# ✅ AI Tool: Handle Complaint Registration
def complaint_tool(input_data: dict):
    """
    Extracts phone, email, issue, and model from input_data correctly
    and calls register_complaint function.
    """
    input_data = json.loads(input_data)
    phone = input_data.get("phone")
    email = input_data.get("email")
    issue = input_data.get("issue")
    model = input_data.get("model")

    if not phone or not email or not issue or not model:
        return "❌ Missing required details. Please provide phone, email, model, and issue description."

    return register_complaint(phone, email, issue, model)


# ✅ AI Tool: Assistance
def need_assistance_tool(query: str):
    return llm.invoke(
        f"Greet the customer and inform them that you are here to assist with Voltas AC support.\n\nUser: {query}"
    ).content


# ✅ Define AI Agent Tools
tools = [
    Tool(
        name="TrackOrder", func=order_tracking_tool, description="Track an order by ID."
    ),
    Tool(
        name="RegisterComplaint",
        func=complaint_tool,  # Correct function reference
        description="Register an AC complaint. Requires 'phone', 'email', 'issue', and 'model'.",
    ),
    Tool(
        name="GeneralSupport",
        func=general_support_tool,
        description="Provide general customer support information.",
    ),
    Tool(
        name="NeedAssistance",
        func=need_assistance_tool,
        description="Assist customer with general inquiries.",
    ),
]

# ✅ Initialize LangChain AI Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    memory=memory,  # Attach memory here
    verbose=True,
)


def customer_support_agent():
    print("\n🤖 Welcome to Voltas AC Customer Support! How can I assist you today?")

    while True:
        user_query = input("\nYou: ").strip()

        # ✅ If User Wants to Exit, Stop the Conversation
        if user_query.lower() in ["no thanks", "ok thanks", "not now"]:
            print("\n🤖 Thank you for reaching out. Have a great day!")
            break

        # ✅ AI Identifies Intent While Remembering Chat History
        query_type = ai_query_processor(user_query)

        # ✅ Track Order
        if query_type == "track_order":
            order_id = input("\n📦 Please enter your Order Tracking ID: ")
            response = agent.invoke(
                {"input": order_id, "chat_history": memory.load_memory_variables({})}
            )
        elif query_type == "general_support":
            response = agent.invoke(
                {
                    "input": "General Support",
                    "chat_history": memory.load_memory_variables({}),
                }
            )

        # ✅ Complaint Registration
        elif query_type == "register_complaint":
            phone, email = extract_contact_info(user_query)

            # ✅ Ask for missing details
            if not phone or not email:
                print(
                    "\n🤖 Can you please provide your registered mobile number and/or email?"
                )
                additional_input = input("\nYou: ")
                new_phone, new_email = extract_contact_info(additional_input)
                phone = phone or new_phone
                email = email or new_email

            print("\n🤖 Please provide your AC model number.")
            model_number = input("\nYou: ").strip()

            print("\n🔧 Describe the issue with your AC.")
            issue_desc = input("\nYou: ").strip()

            # ✅ Register Complaint (Ensure Proper Argument Passing)
            complaint_data = {
                "phone": phone if phone else "Unknown",
                "email": email if email else "Unknown",
                "issue": issue_desc,
                "model": model_number,
            }
            # ✅ Convert dictionary `complaint_data` to a properly formatted string
            complaint_text = json.dumps(complaint_data, ensure_ascii=False)

            # ✅ Pass the formatted complaint data as a string to `invoke()`
            response = agent.invoke(
                {
                    "input": complaint_text,  # ✅ Fix: Ensure "input" is a string
                    "chat_history": memory.load_memory_variables({}),
                }
            )

        # ✅ General Assistance
        elif query_type == "need_assistance":
            response = agent.invoke(
                {
                    "input": "Need Assistance",
                    "chat_history": memory.load_memory_variables({}),
                }
            )

        print("\n🤖", response)

        # ✅ Extract only the "output" key if response is a dictionary
        if isinstance(response, dict):
            response_text = response.get("output", "No response available.")
        else:
            response_text = str(response)

        memory.save_context({"input": str(user_query)}, {"output": response_text})


# ✅ Run AI Agent
if __name__ == "__main__":
    customer_support_agent()
