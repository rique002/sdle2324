from flask import Flask, render_template, request, redirect, url_for, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, ShoppingList, ShoppingItem
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from crdts import AWORMap, ShoppingListCRDT
import requests
import uuid


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_list.db'

db.init_app(app)

last_change = None
current_shopping_list = None

class AddItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class CreateShoppingListForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    global current_shopping_list
    create_form = CreateShoppingListForm()

    if create_form.validate_on_submit():
        # new_shopping_list = ShoppingList(id=new_id ,name=create_form.name.data)
        current_shopping_list = ShoppingListCRDT(str(uuid.uuid4()), create_form.name.data, AWORMap())
        # db.session.add(new_shopping_list)
        # db.session.commit()
        return redirect(url_for('show_shopping_list', id=current_shopping_list.id))

    return render_template('index.html', create_form=create_form)

@app.route('/shopping_list/<string:id>', methods=['GET', 'POST'])
def show_shopping_list(id):
    global current_shopping_list
    if(current_shopping_list is None or current_shopping_list.id != id):
        shopping_list = ShoppingList.query.get(id)
        current_shopping_list = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap())
        for item in shopping_list.items:
            current_shopping_list.add_item(item)

    form = AddItemForm()

    if form.validate_on_submit():
        current_shopping_list.add_item(str(uuid.uuid4()), form.name.data, form.quantity.data)

        # db.session.add(item)
        # db.session.commit()
        return redirect(url_for('show_shopping_list', id=id))


    json = {'id': current_shopping_list.id, 'name': current_shopping_list.name, 'items': current_shopping_list.items.value(), 'item_names': current_shopping_list.item_names}
    return render_template('shopping_list.html', shopping_list=json, form=form)


@app.route('/clear_list/<string:id>', methods=['POST'])
def clear_list(id):
    if(current_shopping_list is None or current_shopping_list.id != id):
        shopping_list = ShoppingList.query.get(id)
        current_shopping_list = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap())
        for item in shopping_list.items:
            current_shopping_list.add_item(item)

    for item_id in current_shopping_list.items.value():
        current_shopping_list.remove_item(item_id)

    return redirect(url_for('show_shopping_list', id=id))


@app.route('/update_item', methods=['PUT'])
def update_quantity():
    data = request.json
    item_id = data['item_id']
    update_num = data['update_num']

    try:
        current_shopping_list.add_item(item_id, None, update_num)
        new_quantity = current_shopping_list.items.value()[item_id]
        return jsonify({'newQuantity': new_quantity, 'success': True}), 200
    except:
        return jsonify({'error': 'Item not found'}), 404


@app.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    try:
        current_shopping_list.remove_item(item_id)
        return 'Item removed successfully', 200
    except:
        return 'Item not found', 404

# def send_signal(mapper, connection, target):
#     item_name = target.name  # Get the name of the item
#     client_socket.send(item_name.encode('utf-8'))
#     print(f"Sent item name {item_name} to proxy")

# event.listen(ShoppingItem, 'after_delete', send_signal)

# def send_signal_after_insert_list(mapper, connection, target):
#     try :
#         response = requests.post('http://127.0.0.1:4000/list', json={'id': target.id, 'name': target.name, 'items': [{'id': item.id, 'name': item.name, 'quantity': item.quantity} for item in target.items]})
#         if response.status_code == 201:
#             print("List created successfully")
#         else:
#             print("Failed to create list")
#     except:
#         print("Not able to connect the server")
        
# def send_signal_after_insert_item(mapper, connection, target):
#     try :
#         response = requests.post('http://127.0.0.1:4000/item', json={'id': target.id, 'name': target.name, 'quantity': target.quantity, 'shopping_list_id': target.shopping_list_id})
#         if response.status_code == 201:
#             print("Item created successfully")
#         else:
#             print("Failed to create item")
#     except:
#         print("Not able to connect the server")

# def send_signal_after_delete_item(mapper, connection, target):
#     try:
#         response = requests.delete('http://127.0.0.1:4000/remove_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
#         print(response)
#         if response.status_code == 204:
#             print("Item deleted successfully")
#         else:
#             print("Failed to delete item")
#     except:
#         print("Not able to connect the server")       

# def send_signal_after_update_item(mapper, connection, target):
#     if(last_change < 0):
#         try:
#             response = requests.put('http://127.0.0.1:4000/decrement_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
#             if response.status_code == 204:
#                 print("Item decremented successfully")
#             else:
#                 print("Failed to decrement item")
#         except:
#             print("Not able to connect the server")        
    
#     else:
#         try:
#             response = requests.put('http://127.0.0.1:4000/increment_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
#             if response.status_code == 204:
#                 print("Item incremented successfully")
#             else:
#                 print("Failed to increment item")
#         except:
#             print("Not able to connect the server")        
            

# list_buffer = []
# item_buffer = []

# def collect_lists(mapper, connection, target):
#     list_buffer.append(target)

# def collect_items(mapper, connection, target):
#     item_buffer.append(target)

# def send_changes():
#     while list_buffer:
#         change = None
#         try:
#             change = list_buffer.pop()
#             response = requests.post('http://127.0.0.1:4000/list', json={'id': change.id, 'name': change.name, 'items': []})
#             if response.status_code != 201:
#                 print(f"Failed to create list '{change.name}'")
#                 list_buffer.append(change)
#                 return
#             else:
#                 print(f"List '{change.name}' created successfully")
#         except:
#             if change is not None:
#                 list_buffer.append(change)
#             print("Not able to connect to the server")
#             return
    
#     while item_buffer:
#         change = None
#         change = item_buffer.pop()
#         print(change.shopping_list_id)
#         try:
#             response = requests.post('http://127.0.0.1:4000/item', json={'id': change.id, 'name': change.name, 'quantity': change.quantity, 'shopping_list_id': change.shopping_list_id})
#             if response.status_code != 201:
#                 print(f"Failed to create item {change.name}")
#                 item_buffer.append(change)
#                 break
#             else:
#                 print(f"Item {change.name} created successfully")
#         except:
#             if change is not None:
#                 item_buffer.append(change)
#             print("Not able to connect to the server")
            # break

def send_current_shopping_list():
    if current_shopping_list is not None:
        try:
            items = []
            for item in current_shopping_list.items.value():
                items.append({'id': item, 'name': current_shopping_list.item_names[item], 'quantity': current_shopping_list.items.value()[item]})
            response = requests.post('http://127.0.0.1:4000/list', json={'id': current_shopping_list.id, 'name': current_shopping_list.name, 'items': items, 'replica_id': current_shopping_list.replica_id})
            if response.status_code == 201:
                print("List updated successfully")
            else:
                print("Failed to update list")
        except:
            print("Not able to connect the server")

def save_current_shopping_list():
    if current_shopping_list is not None:
        with app.app_context():
            try:
                shopping_list = ShoppingList.query.get(current_shopping_list.id)
                if shopping_list is not None:
                    existing_list_crdt = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap(), shopping_list.replica_id)
                    for item in shopping_list.items:
                        existing_list_crdt.add_item(item.id, item.name, item.quantity)
                    current_shopping_list.merge(existing_list_crdt)

                    shopping_list.replica_id = current_shopping_list.replica_id

                    for item_id in current_shopping_list.items.value():
                        existing_item = ShoppingItem.query.get(item_id)
                        if existing_item is None:
                            new_item = ShoppingItem(id=item_id, name=current_shopping_list.item_names[item_id], quantity=current_shopping_list.items.value()[item_id], shopping_list_id=current_shopping_list.id)
                            db.session.add(new_item)
                        else:
                            existing_item.quantity = current_shopping_list.items.value()[item_id]
                else:
                    shopping_list = ShoppingList(id=current_shopping_list.id, name=current_shopping_list.name, replica_id=current_shopping_list.replica_id)
                    db.session.add(shopping_list)
                    for item_id in current_shopping_list.items.value():
                        new_item = ShoppingItem(id=item_id, name=current_shopping_list.item_names[item_id], quantity=current_shopping_list.items.value()[item_id], shopping_list_id=current_shopping_list.id)
                        db.session.add(new_item)

                db.session.commit()
                            
                print("List saved successfully")
            except Exception as e:
                print(e)
                print("Failed to save list")
        
        current_shopping_list.replica_id += 1 

        
scheduler = BackgroundScheduler()
scheduler.add_job(send_current_shopping_list, 'interval', seconds=5)
scheduler.add_job(save_current_shopping_list, 'interval', seconds=8)
scheduler.start()

# db.event.listen(ShoppingList, 'after_insert', collect_lists)
# db.event.listen(ShoppingItem, 'after_insert', collect_items)
        
# event.listen(ShoppingList, 'after_insert', send_signal_after_insert_list)
# event.listen(ShoppingItem, 'after_insert', send_signal_after_insert_item)
# event.listen(ShoppingItem, 'after_delete', send_signal_after_delete_item)
# event.listen(ShoppingItem, 'after_update', send_signal_after_update_item)
