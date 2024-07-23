from flask import Flask, request, render_template, jsonify
import requests
import re
from nltk.chat.util import Chat, reflections

app = Flask(__name__)

# Function to get account details from the exposed Flask API
def get_account_details(account_number):
    
    url = f"https://proud-bugs-pay.loca.lt/api/account/{account_number}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch account details or account not found"}

# Function to perform a transaction between two accounts
def perform_transaction(source_account, destination_account, amount, pin):
    url = "https://proud-bugs-pay.loca.lt/api/transfer"
    data = {
        "source_account": source_account,
        "destination_account": destination_account,
        "amount": amount,
        "pin": pin
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Transaction failed"}

# State to keep track of the conversation
conversation_state = {
    "awaiting_account_number": True,
    "account_details": None,
    "awaiting_transaction_details": False,
    "awaiting_pin": False,
    "transaction_details": None,
    "source_account": None
}

# Custom response function to handle different states and multiple details
def custom_response(statement):
    if conversation_state["awaiting_account_number"]:
        match = re.search(r'(\d+)', statement)
        if match:
            account_number = match.group(1)
            account_details = get_account_details(account_number)
            if "error" in account_details:
                return "Account not found. Please provide a valid account number."
            else:
                conversation_state["awaiting_account_number"] = False
                conversation_state["account_details"] = account_details
                conversation_state["source_account"] = account_number
                return "Account details found. You can ask questions about this account or perform a transaction."
        else:
            return "Please provide your account number."

    elif conversation_state["awaiting_transaction_details"]:
        match = re.match(r'transfer (\d+(\.\d+)?) to (\d+)', statement)
        if match:
            amount = float(match.group(1))
            destination_account = match.group(3)
            conversation_state["transaction_details"] = {
                "amount": amount,
                "destination_account": destination_account
            }
            conversation_state["awaiting_transaction_details"] = False
            conversation_state["awaiting_pin"] = True
            return "Please provide your PIN to authorize the transaction."
        else:
            return "Please provide the transaction details in the format: 'transfer <amount> to <destination_account>'."

    elif conversation_state["awaiting_pin"]:
        pin = statement.strip()
        transaction_details = conversation_state["transaction_details"]
        transaction_result = perform_transaction(conversation_state["source_account"],
                                                 transaction_details["destination_account"],
                                                 transaction_details["amount"],
                                                 pin)
        conversation_state["awaiting_pin"] = False
        if "error" in transaction_result:
            conversation_state["awaiting_transaction_details"] = True
            return transaction_result["error"]
        else:
            conversation_state["account_details"]["balance"] = transaction_result['source_account_balance']
            return ("Transaction successful! "
                    f"New balance: {transaction_result['source_account_balance']} {conversation_state['account_details']['currency']}.")

    else:
        account_details = conversation_state["account_details"]
        response = []
        if "balance" in statement.lower():
            response.append(f"Balance: {account_details['balance']} {account_details['currency']}")
        if "address" in statement.lower():
            response.append(f"Address: {account_details['address']}")
        if "phone" in statement.lower():
            response.append(f"Phone: {account_details['phone']}")
        if "email" in statement.lower():
            response.append(f"Email: {account_details['email']}")
        if "transfer" in statement.lower():
            conversation_state["awaiting_transaction_details"] = True
           
        if response:
            return "Here are the details you requested:\n" + "\n".join(response)
        else:
            return ("I can provide information about the account balance, address, phone number, or email. "
                    "Please ask about one or more of these details.")

# Define pairs of patterns and responses
pairs = [
    (r'(.*)', [custom_response])
]

# Custom class to override the Chat class to use custom response
class CustomChat(Chat):
    def respond(self, statement):
        for pattern, responses in self._pairs:
            match = re.match(pattern, statement)
            if match:
                response = responses[0]
                if callable(response):
                    response = response(statement)
                if response:
                    return response
        return "I am not sure how to respond to that."

# Create an instance of CustomChat
chatbot = CustomChat(pairs, reflections)



# Route for home page
@app.route('/index')
def home():
    return render_template('index.html')




# Route to handle chat input and output
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['user_message']
    
    bot_response = chatbot.respond(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
