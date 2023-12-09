from flask import Flask, render_template, request, redirect, url_for, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from sqlalchemy import event
from models import db, ShoppingList, ShoppingItem
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
import uuid

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_list.db'

db.init_app(app)
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.connect(('127.0.0.1', 8888))
#             print("Connection successful")
#         except socket.error as e:
#             print(f"Connection failed: {e}")

last_change = 0

class AddItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class CreateShoppingListForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    create_form = CreateShoppingListForm()

    if create_form.validate_on_submit():
        new_shopping_list = ShoppingList(id=str(uuid.uuid4()) ,name=create_form.name.data)
        db.session.add(new_shopping_list)
        db.session.commit()
        return redirect(url_for('show_shopping_list', id=new_shopping_list.id))

    return render_template('index.html', create_form=create_form)

@app.route('/shopping_list/<string:id>', methods=['GET', 'POST'])
def show_shopping_list(id):
    shopping_list = ShoppingList.query.get(id)

    if shopping_list is None:
        return "Shopping list not found", 404

    form = AddItemForm()

    if form.validate_on_submit():
        item = ShoppingItem(
            id=str(uuid.uuid4()),
            name=form.name.data,
            quantity=form.quantity.data,
            shopping_list_id=id
        )

        db.session.add(item)
        db.session.commit()
        return redirect(url_for('show_shopping_list', id=id))


    return render_template('shopping_list.html', shopping_list=shopping_list, form=form)


@app.route('/clear_list/<string:id>', methods=['POST'])
def clear_list(id):
    shopping_list = ShoppingList.query.get(id)

    if shopping_list is None:
        return "Shopping list not found", 404

    # Clear the items from the shopping list
    shopping_list.items = []
    db.session.commit()

    return redirect(url_for('show_shopping_list', id=id))


@app.route('/update_item', methods=['PUT'])
def update_quantity():
    data = request.json
    item_id = data['item_id']
    update_num = data['update_num']

    item = ShoppingItem.query.get(item_id)
    if item and item.quantity + update_num >= 0:
        new_quantity = item.quantity + update_num
        item.quantity = new_quantity
        db.session.commit()
        last_change = update_num
        return jsonify({'newQuantity': new_quantity, 'success': True}), 200
    return jsonify({'error': 'Item not found'}), 404

@app.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    item = ShoppingItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return 'Item removed successfully', 200
    return 'Item not found', 404

# def send_signal(mapper, connection, target):
#     item_name = target.name  # Get the name of the item
#     client_socket.send(item_name.encode('utf-8'))
#     print(f"Sent item name {item_name} to proxy")

# event.listen(ShoppingItem, 'after_delete', send_signal)

def send_signal_after_insert_list(mapper, connection, target):
    try :
        response = requests.post('http://127.0.0.1:4000/list', json={'id': target.id, 'name': target.name, 'items': [{'id': item.id, 'name': item.name, 'quantity': item.quantity} for item in target.items]})
        if response.status_code == 201:
            print("List created successfully")
        else:
            print("Failed to create list")
    except:
        print("Not able to connect the server")
        
def send_signal_after_insert_item(mapper, connection, target):
    try :
        response = requests.post('http://127.0.0.1:4000/item', json={'id': target.id, 'name': target.name, 'quantity': target.quantity, 'shopping_list_id': target.shopping_list_id})
        if response.status_code == 201:
            print("Item created successfully")
        else:
            print("Failed to create item")
    except:
        print("Not able to connect the server")

def send_signal_after_delete_item(mapper, connection, target):
    try:
        response = requests.delete('http://127.0.0.1:4000/remove_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
        print(response)
        if response.status_code == 204:
            print("Item deleted successfully")
        else:
            print("Failed to delete item")
    except:
        print("Not able to connect the server")       

def send_signal_after_update_item(mapper, connection, target):
    if(last_change < 0):
        try:
            response = requests.put('http://127.0.0.1:4000/decrement_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
            if response.status_code == 204:
                print("Item decremented successfully")
            else:
                print("Failed to decrement item")
        except:
            print("Not able to connect the server")        
    
    else:
        try:
            response = requests.put('http://127.0.0.1:4000/increment_item', json={'shopping_list_id': target.shopping_list_id, 'item_id': target.id})
            if response.status_code == 204:
                print("Item incremented successfully")
            else:
                print("Failed to increment item")
        except:
            print("Not able to connect the server")        
            

list_buffer = []
item_buffer = []

def collect_lists(mapper, connection, target):
    list_buffer.append(target)

def collect_items(mapper, connection, target):
    item_buffer.append(target)

def send_changes():
    for change in list_buffer:
        try :
            response = requests.post('http://127.0.0.1:4000/list', json={'id': change.id, 'name': change.name, 'items': []})
            if response.status_code == 201:
                print("List created successfully")
            else:
                print("Failed to create list")
            list_buffer.remove(change)
        except:
            print("Not able to connect the server")

    for change in item_buffer:
        try :
            response = requests.post('http://127.0.0.1:4000/item', json={'id': change.id, 'name': change.name, 'quantity': change.quantity, 'shopping_list_id': change.shopping_list_id})
            if response.status_code == 201:
                print("Item created successfully")
            else:
                print("Failed to create item")
        except:
            print("Not able to connect the server")


scheduler = BackgroundScheduler()
scheduler.add_job(send_changes, 'interval', seconds=5)
scheduler.start()

db.event.listen(ShoppingList, 'after_insert', collect_lists)
db.event.listen(ShoppingItem, 'after_insert', collect_items)
        
# event.listen(ShoppingList, 'after_insert', send_signal_after_insert_list)
event.listen(ShoppingItem, 'after_insert', send_signal_after_insert_item)
event.listen(ShoppingItem, 'after_delete', send_signal_after_delete_item)
event.listen(ShoppingItem, 'after_update', send_signal_after_update_item)





