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
        current_shopping_list = ShoppingListCRDT(str(uuid.uuid4()), create_form.name.data, AWORMap())
        return redirect(url_for('show_shopping_list', id=current_shopping_list.id))

    return render_template('index.html', create_form=create_form)

@app.route('/shopping_list/<string:id>', methods=['GET', 'POST'])
def show_shopping_list(id):
    global current_shopping_list
    if(current_shopping_list is None or current_shopping_list.id != id):
        shopping_list = ShoppingList.query.get(id)
        if shopping_list is None:
            pull()
            if current_shopping_list is None:
                return 'List not found', 404
        else: 
            current_shopping_list = ShoppingListCRDT(shopping_list.id, shopping_list.name, AWORMap())
            for item in shopping_list.items:
                current_shopping_list.add_item(item)

    form = AddItemForm()

    if form.validate_on_submit():
        current_shopping_list.add_item(str(uuid.uuid4()), form.name.data, form.quantity.data)
        
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
    
@app.route('/save', methods=['POST'])
def save_route():
    save()
    return 'Saved', 200

@app.route('/push', methods=['POST'])
def push_route():
    push()
    return 'Pushed', 200

@app.route('/pull', methods=['POST'])
def pull_route():
    pull()
    return 'Pulled', 200

def push():
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
    print(current_shopping_list.items.value())

def pull():
    if current_shopping_list is not None:
        try:
            server_shopping_list = requests.get(f'http://127.0.0.1:4000/list/{current_shopping_list.id}').json()
            if server_shopping_list is not None:
                server_shopping_list = ShoppingListCRDT(server_shopping_list['id'], server_shopping_list['name'], AWORMap(), server_shopping_list['replica_id'])
                for item in server_shopping_list.items.value():
                    server_shopping_list.add_item(item['id'], item['name'], item['quantity'])
                current_shopping_list.merge(server_shopping_list)
                current_shopping_list.replica_id += 1
                print("List updated successfully")
            else:
                print("Server does not contain the list")
        except:
            print("Not able to connect the server")
    print(current_shopping_list.items.value())
            
def save():
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
    print(current_shopping_list.items.value())
        
