from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, ShoppingList, ShoppingItem
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_list.db'

db.init_app(app)

class AddItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])

class CreateShoppingListForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    shopping_lists = ShoppingList.query.all()
    create_form = CreateShoppingListForm()

    if create_form.validate_on_submit():
        new_shopping_list = ShoppingList(name=create_form.name.data)
        db.session.add(new_shopping_list)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('index.html', shopping_lists=shopping_lists, create_form=create_form)

@app.route('/shopping_list/<int:id>', methods=['GET', 'POST'])
def show_shopping_list(id):
    shopping_list = ShoppingList.query.get(id)

    if shopping_list is None:
        return "Shopping list not found", 404

    form = AddItemForm()

    if form.validate_on_submit():
        item = ShoppingItem(
            name=form.name.data,
            quantity=form.quantity.data,
            shopping_list_id=id
        )

        db.session.add(item)
        db.session.commit()

    return render_template('shopping_list.html', shopping_list=shopping_list, form=form)


@app.route('/clear_list/<int:id>', methods=['POST'])
def clear_list(id):
    shopping_list = ShoppingList.query.get(id)

    if shopping_list is None:
        return "Shopping list not found", 404

    # Clear the items from the shopping list
    shopping_list.items = []
    db.session.commit()

    return redirect(url_for('show_shopping_list', id=id))


@app.route('/increment_quantity/<int:item_id>', methods=['POST'])
def increment_quantity(item_id):
    item = ShoppingItem.query.get(item_id)
    if item:
        new_quantity = item.quantity + 1
        item.quantity = new_quantity
        db.session.commit()
        return jsonify({'newQuantity': new_quantity}), 200
    return jsonify({'error': 'Item not found'}), 404

@app.route('/decrement_quantity/<int:item_id>', methods=['POST'])
def decrement_quantity(item_id):
    item = ShoppingItem.query.get(item_id)
    if item and item.quantity > 0:
        new_quantity = item.quantity - 1
        item.quantity = new_quantity
        db.session.commit()
        return jsonify({'newQuantity': new_quantity}), 200
    return jsonify({'error': 'Item not found or quantity cannot be negative'}), 400

@app.route('/remove_item/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    item = ShoppingItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return 'Item removed successfully', 200
    return 'Item not found', 404
