# import socket
from app import db, app
from models import ShoppingList, ShoppingItem  # Import your models
# from flask import Flask
# import requests

def create_and_populate_database():
    # Drop all existing tables to clear the database
    db.drop_all()

    # Create all the tables again
    db.create_all()

    # # Shopping List 1
    # shopping_list1 = ShoppingList(id=str(uuid.uuid4()), name="Groceries")
    # item1 = ShoppingItem(id=str(uuid.uuid4()), name="Apples", quantity=5)
    # item2 = ShoppingItem(id=str(uuid.uuid4()), name="Bananas", quantity=10)

    # # Shopping List 2
    # shopping_list2 = ShoppingList(id=str(uuid.uuid4()), name="Electronics")
    # item3 = ShoppingItem(id=str(uuid.uuid4()), name="Laptop", quantity=1)
    # item4 = ShoppingItem(id=str(uuid.uuid4()), name="Smartphone", quantity=2)

    # # Shopping List 3
    # shopping_list3 = ShoppingList(id=str(uuid.uuid4()), name="Clothing")
    # item5 = ShoppingItem(id=str(uuid.uuid4()), name="T-Shirts", quantity=5)
    # item6 = ShoppingItem(id=str(uuid.uuid4()), name="Jeans", quantity=3)

    # # Add items to shopping lists
    # shopping_list1.items.extend([item1, item2])
    # shopping_list2.items.extend([item3, item4])
    # shopping_list3.items.extend([item5, item6])

    # # Add shopping lists to the database
    # db.session.add_all([shopping_list1, shopping_list2, shopping_list3])
    # db.session.commit()

if __name__ == "__main__":
    # with app.app_context(),socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    with app.app_context():  # Create an application context
        create_and_populate_database() 
        app.run(host="127.0.0.1", port=8080, threaded=True)
        # print("database populated")
        # shopping_lists = ShoppingList.query.all()
        # for shopping_list in shopping_lists:
        #     print("sending shopping list " + shopping_list.name)
        #     response = requests.post('http://localhost:4000/list', json={'id': shopping_list.id, 'name': shopping_list.name, 'items': [{'id': item.id, 'name': item.name, 'quantity': item.quantity} for item in shopping_list.items]})
        #     if response.status_code == 201:
        #         print("List created successfully")
        #     else:
        #         print("Failed to create list")

                
