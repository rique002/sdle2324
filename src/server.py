# import socket
# import threading
# import sqlite3
from flask import Flask, request, jsonify
from models import db, ShoppingList, ShoppingItem
from apscheduler.schedulers.background import BackgroundScheduler
from crdts import AWORMap, ShoppingListCRDT
import sys
import requests

server_id = sys.argv[1] if len(sys.argv) > 1 else 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///shopping_list_server{server_id}.db'
db.init_app(app)

local_shopping_lists_crdts = {}

@app.route('/list', methods=['POST'])
def create_list():
    list_data = request.json
    print(list_data)
    
    try:
        new_list_crdt = ShoppingListCRDT(list_data['id'], list_data['name'], AWORMap(), list_data['replica_id'])
        for item in list_data['items']:
            new_list_crdt.add_item(item['id'], item['name'], item['quantity'])

        existing_list_crdt = local_shopping_lists_crdts.get(list_data['id'])
        
        if existing_list_crdt:
            print("EXISTING LIST "+str(existing_list_crdt.replica_id))    
            print(existing_list_crdt.items.value())
            print("NEW LIST " + str(new_list_crdt.replica_id))    
            print(new_list_crdt.items.value())
            existing_list_crdt.merge(new_list_crdt)
            print("MERGED LIST " +  str(existing_list_crdt.replica_id))    
            print(existing_list_crdt.items.value())
        
            new_list_crdt = existing_list_crdt

        local_shopping_lists_crdts[list_data['id']] = new_list_crdt


        return "List updated successfully", 201

    except Exception as e:
        print(e)
        return "List not created", 400


@app.route('/list/<string:list_id>', methods=['GET'])
def get_list(list_id):
    print(local_shopping_lists_crdts)
    shopping_list = local_shopping_lists_crdts.get(list_id)
    
    if shopping_list is None:
        return "List not found", 404
    
    items = []
    for item_id in shopping_list.items.value():
        items.append({'id': item_id, 'name': shopping_list.item_names[item_id], 'quantity': shopping_list.items.value()[item_id]})
    
    return jsonify({'id': shopping_list.id, 'replica_id': shopping_list.replica_id, 'name': shopping_list.name, 'items': items})


def save_local_shopping_lists():
    with app.app_context():
        try:
            for shopping_list_crdt in local_shopping_lists_crdts.values():
                shopping_list = db.session.get(ShoppingList, shopping_list_crdt.id)
                if shopping_list is not None:
                    existing_list_crdt = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap(), shopping_list.replica_id)
                    for item in shopping_list.items:
                        existing_list_crdt.add_item(item.id, item.name, item.quantity)
                    print("SAVE EXISTING LIST "+str(existing_list_crdt.replica_id))
                    print(existing_list_crdt.items.value())
                    print("SAVE SHOPPING LIST " + str(shopping_list_crdt.replica_id))
                    print(shopping_list_crdt.items.value())
                    existing_list_crdt.merge(shopping_list_crdt)
                    shopping_list_crdt=existing_list_crdt
                    print("SAVE MERGED LIST " +  str(shopping_list_crdt.replica_id))
                    print(shopping_list_crdt.items.value())
                    shopping_list.replica_id = shopping_list_crdt.replica_id
                    for item_id in shopping_list_crdt.items.value():
                        existing_item = db.session.get(ShoppingItem, item_id)
                        if existing_item is None:
                            new_item = ShoppingItem(id=item_id, name=shopping_list_crdt.item_names[item_id], quantity=shopping_list_crdt.items.value()[item_id], shopping_list_id=shopping_list_crdt.id)
                            db.session.add(new_item)
                        else:
                            existing_item.quantity = shopping_list_crdt.items.value()[item_id]
                else:
                    shopping_list = ShoppingList(id=shopping_list_crdt.id, name=shopping_list_crdt.name, replica_id=shopping_list_crdt.replica_id)
                    db.session.add(shopping_list)
                    for item_id in shopping_list_crdt.items.value():
                        new_item = ShoppingItem(id=item_id, name=shopping_list_crdt.item_names[item_id], quantity=shopping_list_crdt.items.value()[item_id], shopping_list_id=shopping_list_crdt.id)
                        db.session.add(new_item)

                db.session.commit()
            
            print("Local shopping lists saved successfully")
        except Exception as e:
            print(e)
            print("Local shopping lists not saved")


scheduler = BackgroundScheduler()
scheduler.add_job(save_local_shopping_lists, 'interval', seconds=8)
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        for shopping_list in db.session.query(ShoppingList).all():
            shopping_list_crdt = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap(), shopping_list.replica_id)
            for item in shopping_list.items:
                shopping_list_crdt.add_item(item.id, item.name, item.quantity)
            local_shopping_lists_crdts[shopping_list.id] = shopping_list_crdt
    while True:
        response = requests.post("http://127.0.0.1:4000/server", json={"url": f"http://localhost:{5000+int(server_id)}"})
        if response.status_code == 200:
            print("Server added to proxy")
            break
        else:
            print("Server not added to proxy")   
    app.run(host="127.0.0.1", port=5000+int(server_id), threaded=True)
