"""
Démonstration rapide de l'agent de vente alimentaire en créole
"""
from food_sales_agent import FoodSalesAgent

def demo():
    """Démonstration de l'agent en créole"""
    print("=" * 60)
    print("🛒 DEMO: Agent IA de Vente Alimentaire en Créole")
    print("=" * 60)
    print()
    
    # Initialiser l'agent
    agent = FoodSalesAgent()
    customer_id = "client_demo"
    history = []
    
    # Exemples de conversations en créole
    conversations = [
        "Bonjou! Ki jan mwen ka ede w jodi a?",
        "Mwen ap chèche pòm",
        "Ki pri yo ye?",
        "Mwen vle ajoute 2 kg pòm nan panyen mwen",
        "Montre m panyen mwen",
        "Ki lòt pwodwi ou rekòmande?",
    ]
    
    print("💬 Conversation avec l'agent:\n")
    
    for i, message in enumerate(conversations, 1):
        print(f"👤 Kliyan: {message}")
        response = agent.chat(message, history, customer_id)
        print(f"🤖 Agent: {response}")
        print()
        
        # Mettre à jour l'historique pour la prochaine itération
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
    
    print("=" * 60)
    print("✅ Démonstration terminée!")
    print("=" * 60)

if __name__ == "__main__":
    demo()

