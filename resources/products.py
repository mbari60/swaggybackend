from flask_restful import Resource, reqparse, fields, marshal
from models import ProductModel, db
from admin.onlyadmin import admin_required
from sqlalchemy import event
from flask_jwt_extended import jwt_required

product_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "price": fields.Integer,
    "stock_quantity": fields.Integer,
    "category": fields.String,
    "image_url": fields.String,
    "insta_url": fields.String,
    "rating": fields.Integer,
}

class ProductResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help="Product name is required")
        self.parser.add_argument('description', type=str, required=True, help="Product description is required")
        self.parser.add_argument('price', type=int, required=True, help="Product price is required")
        self.parser.add_argument('stock_quantity', type=int, required=False, help="Stock quantity is optional")
        self.parser.add_argument('category', type=str, required=True, help="Product category is required")
        self.parser.add_argument('image_url', type=str, required=True, help="Image URL is required")
        self.parser.add_argument('insta_url', type=str, required=False, help="insta url is required")
        self.parser.add_argument('rating', type=int, required=False, help="Product rating is optional")

    @staticmethod
    def validate_rating(target, value, oldvalue, initiator):
        if value is not None:
            return max(0, min(value, 5))
        return None

    @event.listens_for(ProductModel.rating, 'set')
    def validate_rating(target, value, oldvalue, initiator):
        if value is not None:
            return max(0, min(value, 5))
        return None
    
    
    # make sure only logged in users
    def get(self):
        products = ProductModel.query.all()
        if products:
            return marshal(products, product_fields)
        else:
            return {"message": "No products available"}, 404

    # ensure that only admin can post 
    @jwt_required()
    @admin_required
    def post(self):
        args = self.parser.parse_args()
        product = ProductModel(**args)
        db.session.add(product)
        db.session.commit()
        return marshal(product, product_fields), 201
    
     # ensure that only admin can update a product 
    @jwt_required()
    @admin_required
    def put(self, product_id):
        args = self.parser.parse_args()
        product = ProductModel.query.get(product_id)
        if product:
            for key, value in args.items():
                setattr(product, key, value)
            db.session.commit()
            return marshal(product, product_fields), 200
        else:
            return {"message": "Product not found"}, 404

    # ensure only admin can delete 
    @jwt_required()
    @admin_required
    def delete(self, product_id):
        product = ProductModel.query.get(product_id)
        if product:
             try:
                 db.session.delete(product)
                 db.session.commit()
                 return {"message": "Product deleted successfully"}, 200
             except:
                 return {"message": "error deleting product"}, 200
        else:
            return {"message": "Product not found"}, 404
