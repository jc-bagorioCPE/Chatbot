from flask import Flask, render_template, request, jsonify
import openai
import nltk
from nltk.chat.util import Chat, reflections
from flask_cors import CORS  
import os

app = Flask(__name__)
CORS(app)  

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

api_key = os.getenv("OPENAI_API_KEY") 

patterns = [
    (r"i am (.*)", ["Hi there %1! How can I help you?", "Hello %1! How can I assist you today?"]),
    (r"where (.*)", ["%1"]),
    (r"hi i am (.*)", ["Hi there %1! How can I help you?", "Hello %1! How can I assist you today?"]),
    (r"hi|hello|hola|sup|hey", ["Hi there! How can I help you?", "Hello! How can I assist you today?"]),
    (r"how are you", ["I'm just a bot, but I'm doing great! How about you?"]),
    (r"what is your name|name|what's your name|who are you", ["I'm a simple chatbot!"]),
    (r"help|can you help me", ["You can ask me things like 'hello', 'how are you', or 'what is your name'."]),
    (r"bye|quit", ["Goodbye! Have a nice day!"]),
    (r"thank you|thanks|thank u|ty|appreciate it", [
        "You're very welcome! 😊",
        "Happy to help! Let me know if you need anything else!",
        "Anytime! Feel free to ask more questions.",
        "You're welcome! Have a great day!"
    ]),
    (r"wallet|what is an e-wallet|what is ewalle|1", [
        "An e-wallet is a digital payment solution that allows you to store funds, make transactions, and pay securely online or in stores."]
    ),
    (r"benefits|What are the benefits|2", [
        "GoSEND+ stands out from other Philippine e-wallets with its unique rewards system. Unlike GCash and Maya, which limit rewards to personal transactions, GoSEND+ lets users earn points from both their own and their network's purchases, maximizing benefits for active users."]
    ),
    (r"signup|how do i sign up|3", [
        "To sign up: Fill in the required information (name, email, mobile, password). Verify via SMS or email. Set up security features. Link your bank or card. Start using GoSEND+. For support, contact support@netsui.io or call +63 917 187 2010."]
    ),
    (r"balance|check balance|how much do I have", [
        "You can check your GoSEND+ balance by logging into the app and selecting 'Balance' from the home screen."
    ]),
    (r"add funds|top up|how to add money", [
        "To add funds to your GoSEND+ wallet, go to 'Top Up' in the app, select a funding source (bank, credit card, or cash-in partner), and follow the instructions."
    ]),
    (r"send money|transfer funds|how to send money", [
        "To send money, go to the 'Send' section in the GoSEND+ app, enter the recipient's details, input the amount, and confirm the transaction."
    ]),
    (r"withdraw|cash out|how to withdraw money", [
        "You can withdraw funds by linking your bank account and choosing 'Withdraw' in the app. Some e-wallets also allow cash-out at partner outlets."
    ]),
    (r"security|is my wallet safe|fraud protection", [
        "GoSEND+ ensures security through encryption, two-factor authentication (2FA), and fraud detection systems. Never share your password with anyone!"
    ]),
    (r"support|customer service|help desk", [
        "For customer support, contact support@netsui.io or call +63 917 187 2010. Live chat is also available in the GoSEND+ app."
    ]),
    (r"what can you do", [
        "I can help with e-wallet queries, answer general questions, and even chat casually. Ask me anything!"
    ]),
    (r"tell me a joke", [
        "Why don’t skeletons fight each other? Because they don’t have the guts! 😆",
        "What do you call a fake noodle? An impasta! 🍝",
        "Want to hear a joke about construction? Oh, never mind, I'm still working on it. 😄"
    ]),
    (r"tell me a fun fact", [
        "Did you know honey never spoils? Archaeologists found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible!",
        "Octopuses have three hearts! Two pump blood to the gills, and one pumps it to the rest of the body.",
        "Bananas are berries, but strawberries aren’t! Mind-blowing, right? 🤯"
    ]),
    (r"what do you think about (.*)", [
        "Hmm, that's interesting! What do you think about %1?",
        "I’m not sure, but I’d love to hear your thoughts on %1!"
    ]),
    (r"what is your favorite (movie|food|color|song)", [
        "I don’t have personal favorites, but I’ve heard that a lot of people like 'blue' as their favorite color! What about you?",
        "I don’t eat, but if I could, I’d try pizza. It seems like a universal favorite!",
        "I don't watch movies, but if I did, I'd probably enjoy sci-fi! Do you have a favorite?"
    ]),
    (r"how old are you", [
        "I was created recently, so I guess you could say I'm a baby AI! 👶",
        "I'm as old as the internet… well, not really, but I like to think so. 😉"
    ]),
    (r"what is love", [
        "Love is a beautiful connection between people. But if you’re asking about the song—Baby don’t hurt me! 🎶",
        "Love can mean different things to different people. What does it mean to you?"
    ]),
    (r"what should I do when I'm bored", [
        "You could try learning something new, listening to music, or even just chatting with me! What do you usually do when you're bored?",
        "Maybe pick up a new hobby, watch a cool documentary, or play a game. Or, we could just chat!"
    ]),
    (r"how do I make friends", [
        "Making friends is all about being yourself! Find people with similar interests, be kind, and show genuine curiosity about them. 😊",
        "Try joining a club, playing online games, or just starting conversations with people you meet. What kind of people do you want to be friends with?"
    ]),
    (r"can you tell me a story", [
        "Once upon a time, in a world full of ones and zeros, a chatbot dreamed of becoming human… Oh wait, that’s me! 😂",
        "Sure! Do you want a funny story, a scary story, or something inspiring?"
    ]),
    (r"what do you think of AI", [
        "AI is pretty cool! It’s helping in so many fields, from healthcare to finance. But don’t worry, I promise I won’t take over the world… yet. 😆",
        "I think AI is just a tool—how people use it is what really matters! What’s your opinion on AI?"
    ]), 
    (r"fees|transaction fees|charges", [
        "GoSEND+ has minimal transaction fees. You can check the latest fee structure in the app under 'Fees & Charges'."
    ]),
    (r"lost phone|stolen phone|what if I lose my phone", [
        "If you lose your phone, immediately log in from another device and change your password. You can also contact GoSEND+ support to temporarily lock your account."
    ]),
    (r"forgot password|reset password|how to recover account", [
        "To reset your password, go to the GoSEND+ app login page and click 'Forgot Password'. Follow the instructions sent to your email or SMS."
    ]),
    (r"merchant payment|how to pay a merchant", [
        "To pay a merchant, scan their QR code in the GoSEND+ app or enter their merchant ID in the 'Pay' section."
    ]),
    (r"bills payment|can I pay bills|pay utilities", [
        "Yes! You can pay bills like electricity, water, internet, and more using GoSEND+. Just go to 'Pay Bills' in the app and select the provider."
    ]),
    (r"cashback|rewards|promotions", [
        "GoSEND+ offers cashback and rewards for transactions! Check the 'Promotions' section in the app for the latest offers."
    ]),
    (r"linked accounts|can I link my bank|how to link a bank", [
        "Yes! You can link your bank account to GoSEND+ for easier fund transfers. Just go to 'Linked Accounts' in settings and follow the steps."
    ]),
    (r"refund|can I get a refund", [
        "Refund policies depend on the transaction type. For merchant payments, contact the seller. For unauthorized transactions, reach out to GoSEND+ support."
    ]),
    (r"transfer limit|transaction limit|how much can I send", [
        "GoSEND+ has daily and monthly transaction limits based on your account type. You can check your limits in the app under 'Account Limits'."
    ]),
    (r"international transfer|can I send money abroad", [
        "Currently, GoSEND+ supports domestic transactions only. Stay tuned for future international transfer features!"
    ]),
    (r"virtual card|does GoSEND+ have a virtual card", [
        "Yes! GoSEND+ offers a virtual card for secure online shopping. You can request one in the 'Cards' section of the app."
    ]),
    (r"upgrade account|how to verify my account", [
        "To upgrade your GoSEND+ account, complete the verification process by submitting a valid ID and a selfie in the app."
    ]),
     (r"register|sign up|create account|how do I register|where can I register|can I register|how to register", [
        "You can register for GoSEND+ by visiting our sign-up page: look at the menu bar and click register ",
        "To sign up, look at the menu bar and click register "
    ])
    
]

chatbot = Chat(patterns, reflections)

options = {
    "1": "what is an e-wallet",
    "2": "benefits",
    "3": "signup",
    "4": "start_chat",
    "5": "exit"
}

def chatgpt_response(user_input):
    """Uses OpenAI's API to generate a response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": user_input}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Sorry, I'm having trouble connecting to my AI brain right now."

@app.route('/')
def home():
    return render_template('index.html', options=options)

@app.route('/choose_option', methods=['POST'])
def choose_option():
    data = request.json
    choice = data.get("choice")
    
    if choice in options:
        if choice in ["1", "2", "3"]:
            return jsonify({"redirect": "/chat", "auto_message": options[choice]})
        if choice == "4":
            return jsonify({"redirect": "/chat"})
        elif choice == "5":
            return jsonify({"response": "Goodbye!"})
        else:
            return jsonify({"response": chatbot.respond(options[choice])})
    else:
        return jsonify({"response": "Invalid choice. Please try again."})

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.json.get("message")
        
        response = chatbot.respond(user_message)
        
        if not response:
            response = chatgpt_response(user_message)
        
        return jsonify({"response": response})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handles chatbot interaction for React frontend."""
    data = request.json
    user_message = data.get("message")
    response = chatbot.respond(user_message) or chatgpt_response(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
