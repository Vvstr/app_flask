from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
import logging

# Инициализация Flask и SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)

# Логирование
logging.basicConfig(level=logging.INFO)

# Модель данных
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

# Swagger описание модели
item_model = api.model('Item', {
    'id': fields.Integer(readonly=True, description='The item unique identifier'),
    'name': fields.String(required=True, description='The name of the item'),
    'description': fields.String(description='The description of the item')
})

# Роуты
@api.route('/items')
class ItemList(Resource):
    def get(self):
        """Получить все элементы"""
        items = Item.query.all()
        return [{'id': item.id, 'name': item.name, 'description': item.description} for item in items], 200


    @api.expect(item_model)
    def post(self):
        """Создать новый элемент"""
        data = request.get_json()
        try:
            new_item = Item(name=data['name'], description=data.get('description', ''))
            db.session.add(new_item)
            db.session.commit()
            return {'message': 'Item created'}, 201
        except Exception as e:
            logging.error(f"Error: {e}")
            return {'error': 'Invalid data'}, 400

@api.route('/items/<int:id>')
class ItemDetail(Resource):
    def get(self, id):
        """Получить элемент по ID"""
        item = Item.query.get_or_404(id)
        return {'id': item.id, 'name': item.name, 'description': item.description}

    @api.expect(item_model)
    def put(self, id):
        """Обновить элемент"""
        data = request.get_json()
        item = Item.query.get(id)
        if item:
            item.name = data['name']
            item.description = data.get('description', item.description)
            db.session.commit()
            return {'message': 'Item updated'}
        return {'error': 'Item not found'}, 404

    def delete(self, id):
        """Удалить элемент"""
        item = Item.query.get(id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return {'message': 'Item deleted'}
        return {'error': 'Item not found'}, 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц внутри контекста приложения
    app.run(debug=True, host='0.0.0.0')

