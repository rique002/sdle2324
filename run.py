from app import app, db
from models import ShoppingList, ShoppingItem  # Import your models

def create_and_populate_database():
    # Drop all existing tables to clear the database
    db.drop_all()

    # Create all the tables again
    db.create_all()

    # Shopping List 1
    shopping_list1 = ShoppingList(name="Groceries")
    item1 = ShoppingItem(name="Apples", quantity=5, price=2.99)
    item2 = ShoppingItem(name="Bananas", quantity=10, price=1.99)

    # Shopping List 2
    shopping_list2 = ShoppingList(name="Electronics")
    item3 = ShoppingItem(name="Laptop", quantity=1, price=999.99)
    item4 = ShoppingItem(name="Smartphone", quantity=2, price=499.99)

    # Shopping List 3
    shopping_list3 = ShoppingList(name="Clothing")
    item5 = ShoppingItem(name="T-Shirts", quantity=5, price=12.99)
    item6 = ShoppingItem(name="Jeans", quantity=3, price=24.99)

    # Add items to shopping lists
    shopping_list1.items.extend([item1, item2])
    shopping_list2.items.extend([item3, item4])
    shopping_list3.items.extend([item5, item6])

    # Add shopping lists to the database
    db.session.add_all([shopping_list1, shopping_list2, shopping_list3])
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_and_populate_database()  # Call the function to create and populate the database
        app.run(debug=True)
