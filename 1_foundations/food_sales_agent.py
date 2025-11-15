from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import gradio as gr

load_dotenv(override=True)

# Base de données des produits alimentaires
PRODUCTS_DATABASE = {
    "pommes": {
        "id": "prod_001",
        "name": "Pommes Golden",
        "category": "Fruits",
        "price": 3.50,
        "unit": "kg",
        "stock": 150,
        "description": "Pommes Golden délicieuses et croquantes, cultivées localement",
        "allergens": [],
        "nutrition": {"calories": 52, "carbs": "14g", "fiber": "2.4g"}
    },
    "bananes": {
        "id": "prod_002",
        "name": "Bananes Bio",
        "category": "Fruits",
        "price": 2.90,
        "unit": "kg",
        "stock": 200,
        "description": "Bananes biologiques, parfaitement mûres",
        "allergens": [],
        "nutrition": {"calories": 89, "carbs": "23g", "fiber": "2.6g"}
    },
    "tomates": {
        "id": "prod_003",
        "name": "Tomates Cerises",
        "category": "Légumes",
        "price": 4.20,
        "unit": "kg",
        "stock": 80,
        "description": "Tomates cerises juteuses et sucrées",
        "allergens": [],
        "nutrition": {"calories": 18, "carbs": "3.9g", "fiber": "1.2g"}
    },
    "pain": {
        "id": "prod_004",
        "name": "Pain de Campagne",
        "category": "Boulangerie",
        "price": 2.50,
        "unit": "pièce",
        "stock": 45,
        "description": "Pain de campagne artisanal, cuit au feu de bois",
        "allergens": ["gluten"],
        "nutrition": {"calories": 265, "carbs": "49g", "fiber": "2.7g"}
    },
    "lait": {
        "id": "prod_005",
        "name": "Lait Entier Bio",
        "category": "Produits Laitiers",
        "price": 1.80,
        "unit": "litre",
        "stock": 120,
        "description": "Lait entier biologique, frais du jour",
        "allergens": ["lactose"],
        "nutrition": {"calories": 61, "carbs": "4.8g", "protein": "3.2g"}
    },
    "fromage": {
        "id": "prod_006",
        "name": "Fromage de Chèvre",
        "category": "Produits Laitiers",
        "price": 5.90,
        "unit": "200g",
        "stock": 60,
        "description": "Fromage de chèvre artisanal, crémeux et savoureux",
        "allergens": ["lactose"],
        "nutrition": {"calories": 364, "carbs": "2.4g", "protein": "22g"}
    },
    "poulet": {
        "id": "prod_007",
        "name": "Poulet Fermier",
        "category": "Viande",
        "price": 12.90,
        "unit": "kg",
        "stock": 30,
        "description": "Poulet fermier élevé en plein air",
        "allergens": [],
        "nutrition": {"calories": 239, "carbs": "0g", "protein": "27g"}
    },
    "saumon": {
        "id": "prod_008",
        "name": "Saumon Frais",
        "category": "Poisson",
        "price": 18.50,
        "unit": "kg",
        "stock": 25,
        "description": "Saumon frais, pêché durablement",
        "allergens": ["poisson"],
        "nutrition": {"calories": 208, "carbs": "0g", "protein": "20g"}
    },
    "riz": {
        "id": "prod_009",
        "name": "Riz Basmati Bio",
        "category": "Épicerie",
        "price": 4.50,
        "unit": "kg",
        "stock": 100,
        "description": "Riz basmati biologique, grain long et parfumé",
        "allergens": [],
        "nutrition": {"calories": 365, "carbs": "80g", "fiber": "1.3g"}
    },
    "huile": {
        "id": "prod_010",
        "name": "Huile d'Olive Extra Vierge",
        "category": "Épicerie",
        "price": 8.90,
        "unit": "500ml",
        "stock": 70,
        "description": "Huile d'olive extra vierge, première pression à froid",
        "allergens": [],
        "nutrition": {"calories": 884, "carbs": "0g", "fat": "100g"}
    }
}

# Stockage des paniers et commandes (en production, utiliser une vraie base de données)
shopping_carts = {}
orders = {}
order_counter = 1000


class FoodSalesAgent:
    def __init__(self):
        self.openai = OpenAI()
        self.products = PRODUCTS_DATABASE
        self.tools = self._define_tools()
    
    def _define_tools(self):
        """Définit les outils disponibles pour l'agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Chache pwodwi manje pa non, kategori oswa deskripsyon. Sèvi ak sa a pou jwenn pwodwi lè kliyan an mande yon bagay.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Terme de recherche (nom de produit, catégorie, ou mots-clés)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_details",
                    "description": "Jwenn tout detay yon pwodwi espesifik (pri, deskripsyon, alèjèn, nwitrisyon, stock).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "L'ID du produit (ex: prod_001) ou le nom du produit"
                            }
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_cart",
                    "description": "Ajoute yon pwodwi nan panyen kliyan an. Kreye yon nouvo panyen si sa nesesè.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "L'ID du produit à ajouter"
                            },
                            "quantity": {
                                "type": "number",
                                "description": "La quantité à ajouter"
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "Identifiant unique du client (peut être généré si nouveau client)"
                            }
                        },
                        "required": ["product_id", "quantity", "customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "view_cart",
                    "description": "Montre sa ki nan panyen kliyan an ak total la.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "L'identifiant du client"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_from_cart",
                    "description": "Retire yon pwodwi nan panyen kliyan an.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "L'ID du produit à retirer"
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "L'identifiant du client"
                            }
                        },
                        "required": ["product_id", "customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "place_order",
                    "description": "Pase kòmand kliyan an. Bezwen enfòmasyon livrezon an.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "L'identifiant du client"
                            },
                            "delivery_address": {
                                "type": "string",
                                "description": "Adresse de livraison complète"
                            },
                            "customer_name": {
                                "type": "string",
                                "description": "Nom du client"
                            },
                            "customer_phone": {
                                "type": "string",
                                "description": "Numéro de téléphone du client"
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "Email du client"
                            }
                        },
                        "required": ["customer_id", "delivery_address", "customer_name", "customer_phone", "customer_email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order_status",
                    "description": "Tcheke estati yon kòmand ki egziste deja.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Le numéro de commande"
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations",
                    "description": "Sijere pwodwi ki sanble oswa ki konplemantè ki baze sou preferans oswa panyen aktyèl la.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "ID du produit de référence, ou laissez vide pour des recommandations générales"
                            },
                            "customer_id": {
                                "type": "string",
                                "description": "ID du client pour des recommandations personnalisées"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_categories",
                    "description": "Fè lis tout kategori pwodwi ki disponib yo.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def search_products(self, query: str) -> Dict:
        """Recherche des produits dans la base de données"""
        query_lower = query.lower()
        results = []
        
        for product_id, product in self.products.items():
            if (query_lower in product["name"].lower() or 
                query_lower in product["category"].lower() or
                query_lower in product["description"].lower() or
                query_lower in product_id.lower()):
                results.append({
                    "id": product["id"],
                    "name": product["name"],
                    "category": product["category"],
                    "price": product["price"],
                    "unit": product["unit"],
                    "stock": product["stock"]
                })
        
        return {"products": results, "count": len(results)}
    
    def get_product_details(self, product_id: str) -> Dict:
        """Obtient les détails complets d'un produit"""
        # Chercher par ID ou par nom
        product = None
        for key, prod in self.products.items():
            if prod["id"] == product_id or key.lower() == product_id.lower() or prod["name"].lower() == product_id.lower():
                product = prod
                break
        
        if not product:
            return {"error": f"Pwodwi '{product_id}' pa jwenn"}
        
        return product
    
    def add_to_cart(self, product_id: str, quantity: float, customer_id: str) -> Dict:
        """Ajoute un produit au panier"""
        product = None
        for key, prod in self.products.items():
            if prod["id"] == product_id or key.lower() == product_id.lower():
                product = prod
                break
        
        if not product:
            return {"error": f"Pwodwi '{product_id}' pa jwenn"}
        
        if product["stock"] < quantity:
            return {"error": f"Stock pa ase. Disponib: {product['stock']} {product['unit']}"}
        
        if customer_id not in shopping_carts:
            shopping_carts[customer_id] = {}
        
        if product_id in shopping_carts[customer_id]:
            shopping_carts[customer_id][product_id]["quantity"] += quantity
        else:
            shopping_carts[customer_id][product_id] = {
                "product": product,
                "quantity": quantity
            }
        
        return {
            "success": True,
            "message": f"Ajoute {quantity} {product['unit']} {product['name']} nan panyen an",
            "cart_total": self._calculate_cart_total(customer_id)
        }
    
    def view_cart(self, customer_id: str) -> Dict:
        """Affiche le contenu du panier"""
        if customer_id not in shopping_carts or not shopping_carts[customer_id]:
            return {"message": "Panyen ou a vid", "items": [], "total": 0.0}
        
        items = []
        for product_id, item in shopping_carts[customer_id].items():
            product = item["product"]
            subtotal = product["price"] * item["quantity"]
            items.append({
                "product_id": product_id,
                "name": product["name"],
                "quantity": item["quantity"],
                "unit": product["unit"],
                "price_per_unit": product["price"],
                "subtotal": round(subtotal, 2)
            })
        
        total = self._calculate_cart_total(customer_id)
        return {
            "items": items,
            "total": round(total, 2),
            "item_count": len(items)
        }
    
    def remove_from_cart(self, product_id: str, customer_id: str) -> Dict:
        """Retire un produit du panier"""
        if customer_id not in shopping_carts:
            return {"error": "Panyen vid"}
        
        if product_id not in shopping_carts[customer_id]:
            return {"error": f"Pwodwi '{product_id}' pa jwenn nan panyen an"}
        
        product_name = shopping_carts[customer_id][product_id]["product"]["name"]
        del shopping_carts[customer_id][product_id]
        
        return {
            "success": True,
            "message": f"{product_name} retire nan panyen an",
            "cart_total": self._calculate_cart_total(customer_id)
        }
    
    def place_order(self, customer_id: str, delivery_address: str, 
                   customer_name: str, customer_phone: str, customer_email: str) -> Dict:
        """Passe une commande"""
        if customer_id not in shopping_carts or not shopping_carts[customer_id]:
            return {"error": "Panyen an vid. Ajoute pwodwi anvan pase kòmand."}
        
        global order_counter
        order_id = f"CMD-{order_counter}"
        order_counter += 1
        
        cart_items = []
        total = 0.0
        for product_id, item in shopping_carts[customer_id].items():
            product = item["product"]
            subtotal = product["price"] * item["quantity"]
            total += subtotal
            cart_items.append({
                "product_id": product_id,
                "name": product["name"],
                "quantity": item["quantity"],
                "unit": product["unit"],
                "price": product["price"],
                "subtotal": round(subtotal, 2)
            })
        
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "delivery_address": delivery_address,
            "items": cart_items,
            "total": round(total, 2),
            "status": "confirmée",
            "date": datetime.now().isoformat()
        }
        
        orders[order_id] = order
        # Vider le panier après commande
        shopping_carts[customer_id] = {}
        
        return {
            "success": True,
            "order_id": order_id,
            "message": f"Kòmand {order_id} konfime! Total: {round(total, 2)}€",
            "order": order
        }
    
    def get_order_status(self, order_id: str) -> Dict:
        """Vérifie le statut d'une commande"""
        if order_id not in orders:
            return {"error": f"Kòmand '{order_id}' pa jwenn"}
        
        return orders[order_id]
    
    def get_recommendations(self, product_id: Optional[str] = None, customer_id: Optional[str] = None) -> Dict:
        """Génère des recommandations de produits"""
        recommendations = []
        
        if product_id:
            # Recommandations basées sur un produit spécifique
            product = None
            for key, prod in self.products.items():
                if prod["id"] == product_id or key.lower() == product_id.lower():
                    product = prod
                    break
            
            if product:
                # Recommander des produits de la même catégorie
                for key, prod in self.products.items():
                    if prod["category"] == product["category"] and prod["id"] != product["id"]:
                        recommendations.append({
                            "id": prod["id"],
                            "name": prod["name"],
                            "category": prod["category"],
                            "price": prod["price"],
                            "reason": f"Autre produit de la catégorie {prod['category']}"
                        })
        elif customer_id and customer_id in shopping_carts:
            # Recommandations basées sur le panier
            cart_categories = set()
            for item in shopping_carts[customer_id].values():
                cart_categories.add(item["product"]["category"])
            
            for key, prod in self.products.items():
                if prod["category"] in cart_categories:
                    recommendations.append({
                        "id": prod["id"],
                        "name": prod["name"],
                        "category": prod["category"],
                        "price": prod["price"],
                        "reason": "Complément à votre panier"
                    })
        else:
            # Recommandations générales (produits populaires)
            popular_products = ["pommes", "bananes", "pain", "lait", "tomates"]
            for key in popular_products[:5]:
                if key in self.products:
                    prod = self.products[key]
                    recommendations.append({
                        "id": prod["id"],
                        "name": prod["name"],
                        "category": prod["category"],
                        "price": prod["price"],
                        "reason": "Produit populaire"
                    })
        
        return {"recommendations": recommendations[:5]}
    
    def get_categories(self) -> Dict:
        """Liste toutes les catégories"""
        categories = set()
        for product in self.products.values():
            categories.add(product["category"])
        return {"categories": sorted(list(categories))}
    
    def _calculate_cart_total(self, customer_id: str) -> float:
        """Calcule le total du panier"""
        if customer_id not in shopping_carts:
            return 0.0
        
        total = 0.0
        for item in shopping_carts[customer_id].values():
            total += item["product"]["price"] * item["quantity"]
        return total
    
    def handle_tool_call(self, tool_calls):
        """Gère les appels d'outils"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"🔧 Outil appelé: {tool_name} avec arguments: {arguments}", flush=True)
            
            # Appeler la méthode correspondante
            method = getattr(self, tool_name, None)
            if method:
                result = method(**arguments)
            else:
                result = {"error": f"Méthode {tool_name} non trouvée"}
            
            results.append({
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self) -> str:
        """Génère le prompt système pour l'agent"""
        return """Ou se yon asistan vityèl pou vann nan yon boutik manje sou entènèt ki espesyalize nan pwodwi manje fre ak bon kalite.

WÒL OU:
- Akeyi kliyan yo nan yon fason cho ak pwofesyonèl
- Ede kliyan yo jwenn pwodwi yo ap chèche
- Bay enfòmasyon detaye sou pwodwi yo (pri, deskripsyon, alèjèn, nwitrisyon)
- Jere panyen acha ak kòmand yo
- Sijere pwodwi ki konplemantè oswa ki sanble
- Reponn kesyon sou pwodwi yo, kòmand yo, ak sèvis la

KONPÒTMAN OU:
- Sois zanmitay, sèvisyab ak pwofesyonèl
- Toujou sèvi ak zouti ki disponib yo pou chèche pwodwi, konsilte detay yo, jere panyen an
- Si yon kliyan mande yon pwodwi, sèvi ak search_products pou jwenn li
- Si yon kliyan vle ajoute nan panyen, sèvi ak add_to_cart (jenere yon customer_id si sa nesesè, pa egzanp "client_001")
- Toujou pwopoze rekòmandasyon ki enpòtan
- Enfòme sou alèjèn ak enfòmasyon nwitrisyonèl lè sa apwopriye
- Toujou konfime aksyon enpòtan yo (ajoute nan panyen, kòmand)

PWODWI KI DISPONIB:
- Fwi: pòm, bannann, elatriye
- Legim: tomat, elatriye
- Boulanje: pen, elatriye
- Pwodwi lèt: lèt, fwomaj, elatriye
- Vyann: poul, elatriye
- Pwason: somon, elatriye
- Episri: diri, lwil, elatriye

ENPÒTAN:
- Toujou sèvi ak zouti yo pou jwenn enfòmasyon egzak
- Pa janm envante pri oswa detay pwodwi
- Tcheke stock la anvan konfime disponibilite
- Gide kliyan an etap pa etap nan pwosesis acha a

LANG: Ou dwe pale ak kliyan yo an kreyòl ayisyen. Si kliyan an pale an fransè oswa an anglè, ou ka reponn nan lang sa a tou, men prefere kreyòl la. Toujou sèvi ak kreyòl la pou tout kominikasyon ak kliyan ayisyen yo."""
    
    def chat(self, message: str, history: List, customer_id: str = "client_001"):
        """Gère une conversation avec l'agent"""
        # Construire les messages avec le contexte
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "system", "content": f"ID kliyan aktyèl la: {customer_id}. Sèvi ak ID sa a pou tout operasyon panyen ak kòmand."}
        ]
        
        # Ajouter l'historique
        messages.extend(history)
        
        # Ajouter le message actuel
        messages.append({"role": "user", "content": message})
        
        done = False
        max_iterations = 10
        iteration = 0
        
        while not done and iteration < max_iterations:
            iteration += 1
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                temperature=0.7
            )
            
            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message_obj)
                messages.extend(results)
            else:
                done = True
        
        return response.choices[0].message.content


def create_web_interface():
    """Crée l'interface web avec Gradio"""
    agent = FoodSalesAgent()
    
    def chat_fn(message, history):
        # Utiliser un customer_id basé sur la session
        customer_id = "client_001"  # En production, générer un ID unique par session
        response = agent.chat(message, history, customer_id)
        return response
    
    # Interface Gradio avec design amélioré
    interface = gr.ChatInterface(
        fn=chat_fn,
        title="🛒 Asistan Vityèl - Boutik Manje sou Entènèt",
        description="""
        Byenveni nan boutik manje nou sou entènèt! Mwen se asistan vityèl ou.
        
        Mwen ka ede w ak:
        - 🔍 Chèche pwodwi manje
        - 📋 Wè detay pwodwi yo (pri, alèjèn, nwitrisyon)
        - 🛒 Jere panyen acha ou
        - 💳 Pase yon kòmand
        - ✨ Sijere pwodwi pou ou
        - 📦 Tcheke estati kòmand ou yo
        
        Di m sa w ap chèche oswa ki jan mwen ka ede w!
        """,
        theme=gr.themes.Soft(),
        examples=[
            "Mwen ap chèche pòm",
            "Ki pwodwi fwi ou genyen?",
            "Montre m panyen mwen",
            "Mwen vle ajoute pen nan panyen mwen",
            "Ki rekòmandasyon ou genyen?",
            "Mwen vle pase kòmand"
        ],
        type="messages"
    )
    
    return interface


if __name__ == "__main__":
    interface = create_web_interface()
    interface.launch(share=False, server_name="0.0.0.0", server_port=7860)

