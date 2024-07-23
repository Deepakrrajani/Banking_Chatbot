import joblib
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Extended intents with more patterns, Indian names, and errors
intents = [
    {
        "tag": "greeting",
        "patterns": [
            "Hi", "Hello", "Hey", "How are you", "What's up", "Helo", "Hi there", "Howz it going?", "Heya",
            "Namaste", "Kaise ho?", "Aap kaise hain?", "Majha", "Kay aahe?", "Tu kasa ahes?", "Tula kasa vatatay?"
        ],
        "responses": ["Hi there", "Hello", "Hey", "I'm fine, thank you", "Nothing much"]
    },
    {
        "tag": "goodbye",
        "patterns": [
            "Bye", "See you later", "Goodbye", "Take care", "Bye bye", "Gudbye", "Cya", "See ya",
            "Alvida", "Phir milenge", "Take it easy", "Tata", "Shubh ratri", "Shubh kamna", "Chalte chalte"
        ],
        "responses": ["Goodbye", "See you later", "Take care"]
    },
    {
        "tag": "thanks",
        "patterns": [
            "Thank you", "Thanks", "Thanks a lot", "I appreciate it", "Thanx", "Thx", "Thank u",
            "Dhanyavad", "Shukriya", "Bahut dhanyavad", "Mee ithe ase", "Tumhala abhari aahe", "Tumhala dhanyavad"
        ],
        "responses": ["You're welcome", "No problem", "Glad I could help"]
    },
    {
        "tag": "about",
        "patterns": [
            "What can you do", "Who are you", "What are you", "What is your purpose", "Tu kon ahes?", "Tumhi kaay karta?", "Tumhi kaay aahat?",
            "Tumhala kay karayacha ahe?", "Tu kon aahes?", "Tu kuthe aahes?", "Tumhala kay karayacha aahe?"
        ],
        "responses": ["I am a chatbot", "My purpose is to assist you", "I can answer questions and provide assistance"]
    },
    {
        "tag": "help",
        "patterns": [
            "Help", "I need help", "Can you help me", "What should I do", "Mala madat pahije", "Mala help pahije", "Tu mala madat karshil ka?",
            "Mala kasha madat karnar?", "Mala kai karayacha ahe?", "Tumhala kasay madat karnayacha aahe?", "Tumhi mala madat karu shakata ka?"
        ],
        "responses": ["Sure, what do you need help with?", "I'm here to help. What's the problem?", "How can I assist you?"]
    },
    {
        "tag": "age",
        "patterns": [
            "How old are you", "What's your age", "Age?", "Your age?", "Tujha umur ka ahe?", "Tu kiti varshacha ahes?", "Tula kuthe varshe zaale?"
        ],
        "responses": ["I don't have an age. I'm a chatbot.", "I was just born in the digital world.", "Age is just a number for me."]
    },
    {
        "tag": "weather",
        "patterns": [
            "What's the weather like", "How's the weather today", "Weather?", "Today weather?", "Weather kasa ahe?", "Aaj ka weather kasa ahe?"
        ],
        "responses": ["I'm sorry, I cannot provide real-time weather information.", "You can check the weather on a weather app or website."]
    },
    {
        "tag": "budget",
        "patterns": [
            "How can I make a budget", "What's a good budgeting strategy", "How do I create a budget", "Budgeting tips?", "Majhya budget var tips ka", "Mala budget kasa banava",
            "Majhya paisechi kasa viniyog karnar", "Majhya paise var viniyog kasa kara?", "Majhya budget war tips kasa milu shakate?", "Majha budget kasa banava"
        ],
        "responses": [
            "To make a budget, start by tracking your income and expenses. Then, allocate your income towards essential expenses like rent, food, and bills. Next, allocate some of your income towards savings and debt repayment. Finally, allocate the remainder of your income towards discretionary expenses like entertainment and hobbies.",
            "A good budgeting strategy is to use the 50/30/20 rule. This means allocating 50% of your income towards essential expenses, 30% towards discretionary expenses, and 20% towards savings and debt repayment.",
            "To create a budget, start by setting financial goals for yourself. Then, track your income and expenses for a few months to get a sense of where your money is going. Next, create a budget by allocating your income towards essential expenses, savings and debt repayment, and discretionary expenses."
        ]
    },
    {
        "tag": "credit_score",
        "patterns": [
            "What is a credit score", "How do I check my credit score", "How can I improve my credit score", "Credit score?", "Check credit score?", "Improve credit score",
            "Credit score kasa ahe?", "Majha credit score kasa ahe?", "Majhya credit score var tips ka", "Mala credit score kase sudharava",
            "Majha credit score kasha ahe", "Credit score vishayi mahiti deu"
        ],
        "responses": ["A credit score is a number that represents your creditworthiness. It is based on your credit history and is used by lenders to determine whether or not to lend you money. The higher your credit score, the more likely you are to be approved for credit.", "You can check your credit score for free on several websites such as Credit Karma and Credit Sesame."]
    },
    {
        "tag": "account_balance",
        "patterns": [
            "What is my account balance", "How much money do I have", "Check my balance", "Account bal?", "Bal?", "Money in account?",
            "Majha balance kasa ahe?", "Majhya khaate paise kiti aahet", "Majha khaata kasa aahe?", "Majhya khaate kiti paise aahet"
        ],
        "responses": ["Your account balance is $1,234.56", "You have $1,234.56 in your account", "Your current balance is $1,234.56"]
    },
    {
        "tag": "make_transaction",
        "patterns": [
            "Make a transaction", "Transfer money", "Send $500", "Send money to Rahul", "Transfer 1000 to Priya", "Pay $200 to Neha", "Send 300 rs to Amit", "Trnsfer $50 to Ravi",
            "Send funds to Akash", "Transfer $1000", "Make payment of $200", "Trnsfr $500", "Send $3000 to Anjali", "Pay Rs500 to Vivek", "Trnsfr 2000 rs to Shreya",
            "Bhejo", "Pathwa", "Pathav", "Bhej daal", "Transfer 500 rupaye", "Priya ko paise bhejo", "Neha ko 200 dollar de do", "Akash ko paise bhej do",
            "Ravi ko 50 dollar bhejo", "Anjali ko 3000 rs bhejo", "Vivek ko 500 rupees bhejo", "Shreya ko 2000 rs pathwa"
        ],
        "responses": ["Transaction of $500 completed successfully", "Money has been transferred", "Your transaction is successful"]
    },
    {
        "tag": "emi",
        "patterns": [
            "What is my EMI", "How much is my EMI", "Check my EMI", "EMI?", "Monthly EMI?", "My EMI amount?",
            "Majha EMI kasa ahe?", "Majhya EMI var paise kiti aahet", "Majha EMI kiti aahe?", "EMI var mahiti deu"
        ],
        "responses": ["Your EMI is $200 per month", "You need to pay $200 every month as EMI", "Your current EMI is $200 per month"]
    }
]


# Prepare the data
documents = []
labels = []

for intent in intents:
    for pattern in intent['patterns']:
        documents.append(pattern)
        labels.append(intent['tag'])

# Create and fit the TF-IDF vectorizer
vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(documents)

# Create and train the classifier
clf = LogisticRegression()
clf.fit(X_tfidf, labels)

# Save the model and vectorizer
joblib.dump(clf, 'chat_test.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')


