# 🛒 Agent IA de Vente Alimentaire - Assistance Virtuelle Multi-Canal en Créole

Un agent IA intelligent pour la vente de produits alimentaires en ligne avec support créole haïtien et assistance virtuelle multi-canal.

## 🌟 Fonctionnalités

- **Communication en Créole**: L'agent parle et comprend le créole haïtien
- **Multi-Canal**: Support pour web, SMS, voix, email, et API REST
- **Recherche de Produits**: Recherche intelligente par nom, catégorie ou description
- **Gestion de Panier**: Ajout, suppression et visualisation du panier
- **Commandes**: Passage de commande avec gestion complète
- **Recommandations**: Suggestions de produits basées sur les préférences
- **Informations Détaillées**: Prix, allergènes, nutrition, stock

## 📋 Prérequis

```bash
pip install -r requirements.txt
```

Assurez-vous d'avoir une clé API OpenAI dans votre fichier `.env`:
```
OPENAI_API_KEY=votre_cle_api
```

## 🚀 Utilisation

### 1. Interface Web (Gradio)

Lancez l'interface web interactive:

```bash
python food_sales_agent.py
```

L'interface sera accessible sur `http://localhost:7860`

### 2. API REST (Multi-Canal)

Démarrez le serveur API:

```bash
python food_sales_api.py
```

Le serveur sera accessible sur `http://localhost:5000`

#### Endpoints Disponibles

- `POST /chat` - Chat principal (web, SMS, voix, etc.)
- `GET /products/search?q=...` - Recherche de produits
- `GET /products/<product_id>` - Détails d'un produit
- `GET /cart/<customer_id>` - Voir le panier
- `POST /cart/<customer_id>/add` - Ajouter au panier
- `POST /orders` - Créer une commande
- `GET /orders/<order_id>` - Statut d'une commande
- `POST /sms/webhook` - Webhook pour SMS (Twilio, Vonage, etc.)
- `POST /voice/webhook` - Webhook pour voix (Twilio Voice, etc.)

### 3. Exemple d'Utilisation API

#### Chat via API (simule SMS)

```python
import requests

response = requests.post(
    "http://localhost:5000/chat",
    json={
        "message": "Mwen ap chèche pòm",
        "channel": "sms",
        "user_id": "+33123456789"
    }
)
print(response.json())
```

#### Recherche de Produits

```python
response = requests.get("http://localhost:5000/products/search?q=bannann")
print(response.json())
```

#### Ajouter au Panier

```python
response = requests.post(
    "http://localhost:5000/cart/client_001/add",
    json={
        "product_id": "prod_001",
        "quantity": 2.5
    }
)
print(response.json())
```

## 📱 Intégration Multi-Canal

### SMS (Twilio)

```python
# Webhook configuré pour recevoir les SMS
# Format attendu: {"from": "+33123456789", "body": "message"}
```

### Voix (Twilio Voice)

```python
# Webhook configuré pour recevoir les appels vocaux
# Supporte la transcription et la réponse vocale
```

### Email

Utilisez l'endpoint `/chat` avec `channel: "email"` pour traiter les emails.

## 🗣️ Exemples de Conversation en Créole

```
Kliyan: Bonjou, mwen ap chèche pòm
Agent: Bonjou! Mwen kontan ede w. Mwen gen pòm Golden ki disponib. Vle w wè detay yo?

Kliyan: Ki pri li ye?
Agent: Pòm Golden yo koute 3.50€ pou chak kilogram. Vle w ajoute nan panyen w?

Kliyan: Wi, mwen vle 2 kg
Agent: Mwen ajoute 2 kg pòm Golden nan panyen w. Vle w ajoute lòt bagay?
```

## 🛠️ Structure du Projet

```
food_sales_agent.py      # Agent principal avec interface Gradio
food_sales_api.py        # API REST pour multi-canal
food_sales_example.ipynb # Exemples d'utilisation
README_FOOD_SALES.md     # Documentation
```

## 📦 Produits Disponibles

- **Fruits**: Pommes, Bananes
- **Légumes**: Tomates
- **Boulangerie**: Pain
- **Produits Laitiers**: Lait, Fromage
- **Viande**: Poulet
- **Poisson**: Saumon
- **Épicerie**: Riz, Huile d'olive

## 🔧 Personnalisation

### Ajouter des Produits

Modifiez le dictionnaire `PRODUCTS_DATABASE` dans `food_sales_agent.py`:

```python
PRODUCTS_DATABASE = {
    "nouveau_produit": {
        "id": "prod_011",
        "name": "Nom du Produit",
        "category": "Catégorie",
        "price": 10.00,
        "unit": "kg",
        "stock": 100,
        "description": "Description du produit",
        "allergens": [],
        "nutrition": {"calories": 100, "carbs": "20g"}
    }
}
```

### Modifier le Prompt Système

Modifiez la méthode `system_prompt()` dans la classe `FoodSalesAgent` pour personnaliser le comportement de l'agent.

## 🌐 Support Multi-Langue

L'agent est configuré pour parler créole haïtien par défaut, mais peut aussi comprendre et répondre en français et en anglais si nécessaire.

## 📝 Notes

- En production, remplacez les dictionnaires en mémoire par une vraie base de données
- Ajoutez l'authentification pour les endpoints API
- Implémentez la gestion des paiements
- Ajoutez le suivi des livraisons

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT.

