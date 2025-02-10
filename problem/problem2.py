import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# Initialize the LLM (adjust settings and API key as needed)
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

# Create conversation memory to store the chat history dynamically.
memory = ConversationBufferMemory(
    memory_key="chat_history",  # conversation history key
    return_messages=True,
)


promotional_db = {
    "AC": {
        "product_name": "SuperCool 1.5 Ton Split AC",
        "description": "An energy-efficient, whisper-quiet split AC ideal for modern homes.",
        "coupon_code": "ACPROMO2025",
    }
}

# --- Step A: The Multi-Turn Conversation Chain ---
#
# This prompt instructs the assistant to check the conversation history for missing AC details.
# If details such as AC type or dimensions are missing, the assistant will ask for them.
# (Once provided, the conversation history grows dynamically, and the assistant will not repeat questions.)
conversation_template = """
You are a helpful sales assistant.

The conversation so far is:
{chat_history}

User's current input: {input}

Instructions:
1. If the user’s inquiry is about purchasing an AC, check if the conversation includes the following details:
   - The type of AC (for example: split, window, or central).
   - The dimensions or capacity requirements.
2. If any of these details is missing, ask the user only for the missing information (do not repeat questions already answered).
3. If all the required details are present, respond by acknowledging that all details have been received and that you will now provide a recommendation.

Your answer:
"""

conversation_prompt = PromptTemplate(
    input_variables=["chat_history", "input"], template=conversation_template
)

conversation_chain = LLMChain(llm=llm, prompt=conversation_prompt, memory=memory)

# --- Simulate the Multi-Turn Conversation ---
# Turn 1: User expresses the intent.
print("User: I want to purchase an AC.")
response = conversation_chain.run({"input": "I want to purchase an AC."})
print("Assistant:", response)

# Turn 2: Assistant should now ask for any missing details.
# (For example, if the assistant asks for the AC type.)
print("\nUser: I prefer a split AC.")
response = conversation_chain.run({"input": "I prefer a split AC."})
print("Assistant:", response)

# Turn 3: Next, the assistant might ask for dimensions or capacity.
print("\nUser: I need one with a capacity of 1.5 tons.")
response = conversation_chain.run({"input": "I need one with a capacity of 1.5 tons."})
print("Assistant:", response)

# Turn 4: Now that all details are provided, the conversation turns to finalizing the recommendation.
print("\nUser: That's all for now.")
response = conversation_chain.run({"input": "That's all for now."})
print("Assistant:", response)

# At this point, the conversation history includes the AC purchase intent,
# the AC type ("split AC"), and the capacity/dimensions ("1.5 tons").

# --- Step B: Finalization Chain with Promotional Data ---
#
# Now that we have all the details, we create a final prompt that includes:
# - The dynamic conversation history (which implicitly contains the AC type and capacity).
# - The promotional AC details from our separate database.
#
# The final chain will instruct the assistant to provide a recommendation that includes the promotional coupon code.
final_template = """
You are a helpful sales assistant.

Based on the conversation so far:
{chat_history}

The user’s AC purchase requirements are complete.
For clarity, assume the following extracted details:
- AC Type: {ac_type}
- Capacity/Dimensions: {ac_dimensions}

Our promotional home appliance database offers the following AC product that matches the requirements:
Product Name: {product_name}
Description: {description}
Promotional Coupon Code: {coupon_code}

Provide a final response to the user that:
1. Confirms their requirements.
2. Presents the recommended AC product.
3. Includes the promotional coupon code and any additional helpful information.

Your final answer:
"""

final_prompt = PromptTemplate(
    input_variables=[
        "chat_history",
        "ac_type",
        "ac_dimensions",
        "product_name",
        "description",
        "coupon_code",
    ],
    template=final_template,
)

final_chain = LLMChain(llm=llm, prompt=final_prompt, memory=memory)

# For this demonstration, we assume that the extracted details are as follows:
# (In a production setting, you might extract these details from the conversation history using parsing or an LLM.)
ac_type_extracted = "split AC"
ac_dimensions_extracted = "1.5 tons"

# Retrieve the promotional AC details from our promotional database.
promo_ac = promotional_db["AC"]

# Run the final chain.
final_response = final_chain.run(
    {
        "ac_type": ac_type_extracted,
        "ac_dimensions": ac_dimensions_extracted,
        "product_name": promo_ac["product_name"],
        "description": promo_ac["description"],
        "coupon_code": promo_ac["coupon_code"],
    }
)

print("\nAssistant Final Response:")
print(final_response)
