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


# ✅ Function: Verify User (no changes needed)
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
        return (
            f"📦 Order Status: {order['status']}\n"
            f"🚚 Expected Delivery: {order['expected_delivery']}\n"
            f"📍 Last Location: {order['last_location']}"
        )
    return "❌ Order not found. Please check the tracking ID."


# This counter tracks failed user verification attempts
fail_count = 0


# ✅ Complaint Registration (requires phone OR email)
def register_complaint(phone=None, email=None, issue=None, model=None):
    global fail_count

    user = verify_user(phone, email)
    if user:
        # Reset fail_count because user is verified successfully
        fail_count = 0

        # Now proceed with the rest of your logic
        if model and model != user["purchase"]["model"]:
            return "❌ Model number mismatch. Please check your product details."

        if check_warranty(user["purchase"]["purchase_date"]):
            ticket_id = f"TICKET-{random.randint(100000, 999999)}"
            return (
                f"I’m really sorry you’re experiencing issues with your AC. "
                f"Your complaint is registered successfully! Your ticket ID is **{ticket_id}**."
            )
        else:
            return f"❌ Warranty expired. Please contact support at {SUPPORT_NUMBER}."
    else:
        # If user verification fails, increment the counter
        fail_count += 1

        # If user has failed 3 times, provide the support contact
        if fail_count >= 3:
            return (
                f"❌ We couldn’t verify your account after multiple attempts. "
                f"Please contact our support at {SUPPORT_NUMBER}."
            )

        return (
            "❌ User verification failed. Please check your phone/email and try again. "
            "If you need help, reach out to customer support."
        )


# ✅ AI-Based Query Processor (simple intent classifier)
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


# ✅ Tools
def order_tracking_tool(order_id: str):
    return track_order(order_id)


def general_support_tool(query):
    """
    Show empathy and provide guidance or reassurance.
    """
    empathy_prompt = (
        "You are a helpful and empathetic customer support agent for Voltas AC. "
        "The user may be frustrated or upset, so show sympathy and understanding. "
        "Acknowledge their feelings and provide clear guidance or next steps.\n\n"
        f"User: {query}\n\n"
        "Please respond with a warm, empathetic tone."
    )
    return llm.invoke(empathy_prompt).content


def complaint_tool(input_data: dict):
    """
    Extracts phone, email, issue, and model from input_data correctly
    and calls register_complaint function.

    Note: We only need phone OR email, not both.
    """
    input_data = json.loads(input_data)

    phone = input_data.get("phone")
    email = input_data.get("email")
    issue = input_data.get("issue")
    model = input_data.get("model")

    # Require at least phone or email
    if not phone and not email:
        return (
            "❌ Missing contact details. Please provide at least phone OR email, "
            "along with model and a short description of your issue."
        )

    if not issue or not model:
        return (
            "❌ Missing required details. Please provide model and issue description."
        )

    return register_complaint(phone, email, issue, model)


def need_assistance_tool(query: str):
    empathy_prompt = (
        "You are a helpful and empathetic customer support agent for Voltas AC. "
        "The user wants assistance or has a question. Show warmth, understanding, "
        "and readiness to help.\n\n"
        f"User: {query}\n\n"
        "Please respond with an empathetic greeting and offer your assistance."
    )
    return llm.invoke(empathy_prompt).content


# ✅ Define AI Agent Tools
tools = [
    Tool(
        name="TrackOrder", func=order_tracking_tool, description="Track an order by ID."
    ),
    Tool(
        name="RegisterComplaint",
        func=complaint_tool,
        description="Register an AC complaint. Requires 'phone' or 'email', plus 'issue' and 'model'.",
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
    memory=memory,  # Attach memory
    verbose=True,
)


def customer_support_agent():
    print("\n🤖 Welcome to Voltas AC Customer Support! How can I assist you today?")

    while True:
        user_query = input("\nYou: ").strip()

        # End conversation if user wishes
        if user_query.lower() in ["no thanks", "ok thanks", "not now", "bye", "exit"]:
            print("\n🤖 Thank you for reaching out. Have a great day!")
            break

        # Hand the entire user query to the agent
        response = agent.run(user_query)
        print("\n🤖", response)


# ✅ Run AI Agent
if __name__ == "__main__":
    customer_support_agent()
