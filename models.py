from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    items = db.relationship('ShoppingItem', backref='shopping_list', lazy=True)

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
