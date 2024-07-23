from flask import Flask, request, render_template, jsonify,session
import spacy
from pathlib import Path
import requests
import re
from flask_session import Session
from chat_function import tag
from Intent_model import intents
import random


app = Flask(__name__)


# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'supersecretkey'  # Set a secret key for security

# Initialize the session
Session(app)


# Load the SpaCy NER model
model_path = Path("ner_model/best_model")
nlp = spacy.load(model_path)
def float1(text):
    pattern = r"[-+]?\d*\.\d+|\d+"

    # Search for floats in the text
    matches = re.findall(pattern, text)
    if matches :

    # Convert matched strings to floats and store in a list
        float_values = [float(match) for match in matches]
        f=float_values[0] 
    
        return f



# Function to extract entities using SpaCy NER
def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Function to get account details from the exposed Flask API
def get_account_details(account_number):
    url = f"http://127.0.0.1:6000/api/account/{account_number}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to perform a transaction between two accounts
def perform_transaction(source_account, destination_account, amount, pin):
    url = "http://127.0.0.1:6000/api/transfer"
    data = {
        "source_account": source_account,
        "destination_account": destination_account,
        "amount": amount,
        "pin": pin
    }
    response = requests.post(url, json=data)
    
    print(response.json())
    return response.json()
    

# State to keep track of the conversation
conversation_state = {

    
    "account_details": None,
    "awaiting_transaction_details": False,
    "awaiting_pin": False,
    "transaction_details": None,
    "source_account": None,
    "pay_emi": False,
    "emi_pin": False
}

# Custom response function to handle different states and multiple details
def custom_response(statement):
    
    account_details = session.get('account_details')
    entities = extract_entities(statement)
    print(entities)
    
    response = []
    tag1=tag(statement)
    print(tag1)
    if tag1 not in ['account_balance','make_transaction','emi']:
        for intent in intents:
         if intent['tag'] == tag1:
            response1 = random.choice(intent['responses'])
            response.append(response1)
            print(response) 
    # Check for account details queries
    
    
    # Save account details and source account to conversation state
    if account_details:
        conversation_state["account_details"] = account_details
        conversation_state["source_account"] = session.get('account_number')
    
    if conversation_state['emi_pin']:
            pin = str(statement.strip())
            url = "http://127.0.0.1:6000/api/pay_emi"
            data = {
        "account_number": session.get('account_number'),
        
        "pin": pin
    }   
            print(pin)
            response = requests.post(url, json=data)
            response=response.json()
            conversation_state['emi_pin']=False
            account_details['EMI']=None
            

            if 'error' in response:
                return response['error']
            else :
            
                return (f"{response['message']}  Balance : {response['remaining_balance']}")
    
    if conversation_state["pay_emi"]:
        if 'yes' in  statement.lower():
            conversation_state['emi_pin']=True

            
            return "Please provide your PIN to authorize the transaction."
        else:
            conversation_state["pay_emi"]=False
            
    
    # Check for PIN authorization
    
    if conversation_state["awaiting_pin"]:
        pin = str(statement.strip())
        print(pin)
        
        if pin:
            transaction_details = conversation_state["transaction_details"]
            transaction_result = perform_transaction(
                conversation_state["source_account"],
                transaction_details["destination_account"],
                (transaction_details["amount"]),
                pin
            )
            conversation_state["awaiting_pin"] = False
            
            if "error" in transaction_result:
                conversation_state["awaiting_transaction_details"] = True
                
                return transaction_result['error']
            else:
                conversation_state["account_details"]["balance"] = transaction_result['source_account_balance']
                return (f"Transaction successful! "
                        f"New balance: {transaction_result['source_account_balance']} {conversation_state['account_details']['currency']}.")
        else:
            return "Please provide your PIN to authorize the transaction."
            
    # Check for transfer request
    if tag1=="make_transaction":
        conversation_state["awaiting_transaction_details"] = True
        amount = float1(statement)
        destination_account = next((ent[0] for ent in entities if ent[1] == "PERSON"), None)
        j=account_details['allowed_accounts']
        statement1=statement.upper()
        
        words = re.findall(r'\b\w+\b', statement1)
        
        for i in words:
            
            for a in j:
                
                if i==a:
                    destination_account= i        
        
        print(amount,destination_account)
        
        if amount and destination_account:
            conversation_state["transaction_details"] = {
                "amount": amount,
                "destination_account": destination_account
            }
            conversation_state["awaiting_transaction_details"] = False
            conversation_state["awaiting_pin"] = True
            
            return "Please provide your PIN to authorize the transaction."
        else:
            return "Please provide the transaction details including amount and destination."
    
    # Check for PIN authorization
    
    else:
        if tag1=="account_balance":
            response.append(f"Balance: {account_details['balance']} {account_details['currency']}")
        if "address" in statement.lower():
            response.append(f"Address: {account_details['address']}")
        if "phone" in statement.lower():
            response.append(f"Phone: {account_details['phone']}")
        if "email" in statement.lower():
            response.append(f"Email: {account_details['email']}")
        if tag1=="emi":
            if account_details['EMI'] is not None:
                response.append(f"EMI : {account_details['EMI']['amount']} {account_details['currency']} , Due Date : {account_details['EMI']['due_date']}")
        
                response.append("Would you like to pay your EMI?")
                
        
                conversation_state["pay_emi"]=True
                
            else :
                response.append('No pending emi')
            return response

    

    # Default response
    return response


# Route for home page
@app.route('/')
def login():
    return render_template('login.html')
@app.route('/index', methods=['POST'])
def home():
    acc = request.form['username']
    acc=acc.upper()
    account_details = get_account_details(acc)
    
    # Store account details in session
    session['account_details'] = account_details
    session['account_number']=acc
    
    return render_template('index.html')

# Route to handle chat input and output
@app.route('/chat', methods=['POST'])
def chat():
   
   
        user_message = request.form['user_message']
        
        bot_response = custom_response(user_message)
    
        return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
