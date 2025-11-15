"""
API REST pour l'agent de vente alimentaire multi-canal
Permet l'intégration via SMS, voix, email, et autres canaux
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from food_sales_agent import FoodSalesAgent
import json
from typing import Dict

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

agent = FoodSalesAgent()

# Stockage des sessions de conversation par canal
conversation_sessions = {}


def get_or_create_session(channel: str, user_id: str) -> Dict:
    """Récupère ou crée une session de conversation"""
    session_key = f"{channel}_{user_id}"
    if session_key not in conversation_sessions:
        conversation_sessions[session_key] = {
            "history": [],
            "customer_id": f"client_{channel}_{user_id}"
        }
    return conversation_sessions[session_key]


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({"status": "healthy", "service": "food_sales_agent"})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint principal pour le chat
    Accepte les messages de différents canaux (web, SMS, voix, etc.)
    """
    try:
        data = request.json
        message = data.get('message')
        channel = data.get('channel', 'web')  # web, sms, voice, email, etc.
        user_id = data.get('user_id', 'default')
        
        if not message:
            return jsonify({"error": "Message requis"}), 400
        
        # Récupérer ou créer la session
        session = get_or_create_session(channel, user_id)
        customer_id = session["customer_id"]
        history = session["history"]
        
        # Obtenir la réponse de l'agent
        response = agent.chat(message, history, customer_id)
        
        # Mettre à jour l'historique
        session["history"].append({"role": "user", "content": message})
        session["history"].append({"role": "assistant", "content": response})
        
        return jsonify({
            "response": response,
            "channel": channel,
            "user_id": user_id,
            "customer_id": customer_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/products/search', methods=['GET'])
def search_products():
    """Recherche de produits via API"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Paramètre 'q' requis"}), 400
    
    results = agent.search_products(query)
    return jsonify(results)


@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Obtient les détails d'un produit"""
    details = agent.get_product_details(product_id)
    return jsonify(details)


@app.route('/cart/<customer_id>', methods=['GET'])
def get_cart(customer_id):
    """Récupère le panier d'un client"""
    cart = agent.view_cart(customer_id)
    return jsonify(cart)


@app.route('/cart/<customer_id>/add', methods=['POST'])
def add_to_cart_api(customer_id):
    """Ajoute un produit au panier via API"""
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({"error": "product_id requis"}), 400
    
    result = agent.add_to_cart(product_id, quantity, customer_id)
    return jsonify(result)


@app.route('/cart/<customer_id>/remove', methods=['POST'])
def remove_from_cart_api(customer_id):
    """Retire un produit du panier via API"""
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "product_id requis"}), 400
    
    result = agent.remove_from_cart(product_id, customer_id)
    return jsonify(result)


@app.route('/orders', methods=['POST'])
def create_order():
    """Crée une commande via API"""
    data = request.json
    customer_id = data.get('customer_id')
    delivery_address = data.get('delivery_address')
    customer_name = data.get('customer_name')
    customer_phone = data.get('customer_phone')
    customer_email = data.get('customer_email')
    
    required_fields = ['customer_id', 'delivery_address', 'customer_name', 'customer_phone', 'customer_email']
    missing = [field for field in required_fields if not data.get(field)]
    
    if missing:
        return jsonify({"error": f"Champs requis manquants: {', '.join(missing)}"}), 400
    
    result = agent.place_order(customer_id, delivery_address, customer_name, customer_phone, customer_email)
    return jsonify(result)


@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Récupère le statut d'une commande"""
    status = agent.get_order_status(order_id)
    return jsonify(status)


@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Obtient des recommandations de produits"""
    product_id = request.args.get('product_id')
    customer_id = request.args.get('customer_id')
    
    result = agent.get_recommendations(product_id, customer_id)
    return jsonify(result)


@app.route('/categories', methods=['GET'])
def get_categories():
    """Liste toutes les catégories"""
    categories = agent.get_categories()
    return jsonify(categories)


@app.route('/sms/webhook', methods=['POST'])
def sms_webhook():
    """
    Webhook pour recevoir des SMS (ex: Twilio, Vonage)
    Format attendu: {"from": "+33123456789", "body": "message text"}
    """
    try:
        data = request.json or request.form.to_dict()
        
        # Adapter selon le fournisseur SMS
        phone_number = data.get('from') or data.get('From')
        message = data.get('body') or data.get('Body')
        
        if not phone_number or not message:
            return jsonify({"error": "from et body requis"}), 400
        
        # Traiter le message via l'agent
        session = get_or_create_session('sms', phone_number)
        customer_id = session["customer_id"]
        history = session["history"]
        
        response = agent.chat(message, history, customer_id)
        
        # Mettre à jour l'historique
        session["history"].append({"role": "user", "content": message})
        session["history"].append({"role": "assistant", "content": response})
        
        # Retourner la réponse (à envoyer via le service SMS)
        return jsonify({
            "response": response,
            "to": phone_number
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/voice/webhook', methods=['POST'])
def voice_webhook():
    """
    Webhook pour recevoir des appels vocaux (ex: Twilio Voice)
    Peut être utilisé pour transcription et réponse vocale
    """
    try:
        data = request.json or request.form.to_dict()
        
        # Adapter selon le fournisseur vocal
        call_id = data.get('CallSid') or data.get('call_id')
        transcription = data.get('TranscriptionText') or data.get('transcription')
        
        if not transcription:
            return jsonify({
                "action": "gather",
                "message": "Bonjour! Je suis votre assistant virtuel. Comment puis-je vous aider?"
            })
        
        # Traiter la transcription
        session = get_or_create_session('voice', call_id)
        customer_id = session["customer_id"]
        history = session["history"]
        
        response = agent.chat(transcription, history, customer_id)
        
        # Mettre à jour l'historique
        session["history"].append({"role": "user", "content": transcription})
        session["history"].append({"role": "assistant", "content": response})
        
        # Retourner la réponse (à convertir en voix via TTS)
        return jsonify({
            "response": response,
            "action": "say",
            "call_id": call_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("🚀 Démarrage du serveur API multi-canal...")
    print("📡 Endpoints disponibles:")
    print("   - POST /chat - Chat principal")
    print("   - GET /products/search?q=... - Recherche produits")
    print("   - GET /products/<id> - Détails produit")
    print("   - GET /cart/<customer_id> - Voir panier")
    print("   - POST /cart/<customer_id>/add - Ajouter au panier")
    print("   - POST /orders - Créer commande")
    print("   - GET /orders/<order_id> - Statut commande")
    print("   - POST /sms/webhook - Webhook SMS")
    print("   - POST /voice/webhook - Webhook voix")
    print("\n🌐 Serveur démarré sur http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

