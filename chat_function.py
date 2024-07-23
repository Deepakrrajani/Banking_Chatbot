import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import random
def tag (input_text):
# Load the pre-trained model
    clf = joblib.load('chat_test.pkl')

# Load the fitted vectorizer
    vectorizer = joblib.load('tfidf_vectorizer.pkl')

    

    
    input_text_transformed = vectorizer.transform([input_text])
    tag = clf.predict(input_text_transformed)[0]        
    return tag 





