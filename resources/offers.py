from flask_restful import Resource, reqparse, fields, marshal
from models import OfferModel, db
from datetime import datetime, timedelta
from admin.onlyadmin import admin_required
from flask_jwt_extended import jwt_required

offer_fields = {
    "id": fields.Integer,
    "offer_name": fields.String,
    "description": fields.String,
    "previous_price": fields.Integer,
    "offer_price": fields.Integer,
    "timeline": fields.Integer,
    "image_url": fields.String,
    "insta_url": fields.String,
    "slots_limit": fields.Integer,
    "created_at": fields.DateTime(dt_format="iso8601"),
    "rating": fields.Integer,
}

class OfferResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('offer_name', type=str, required=True, help="Offer name is required")
        self.parser.add_argument('description', type=str)
        self.parser.add_argument('previous_price', type=int)
        self.parser.add_argument('offer_price', type=int, required=True, help="Offer price is required")
        self.parser.add_argument('timeline', type=int, default=60)
        self.parser.add_argument('image_url', type=str)
        self.parser.add_argument('insta_url', type=str, required=False, help="insta url is required")
        self.parser.add_argument('slots_limit', type=int)
        self.parser.add_argument('rating', type=int)

    def get(self, offer_id=None):
        if offer_id:
            offer = OfferModel.query.get(offer_id)
            if offer:
                return marshal(offer, offer_fields), 200
            else:
                return {"message": "Offer not found"}, 404
        else:
            offers = OfferModel.query.all()
            if offers:
                return marshal(offers, offer_fields)
            else:
                return {"message": "No offers available"}, 404
    @jwt_required()
    @admin_required
    def post(self):
        args = self.parser.parse_args()
        offer = OfferModel(**args)
        db.session.add(offer)
        db.session.commit()
        return marshal(offer, offer_fields), 201
    
    @jwt_required()
    @admin_required
    def put(self, offer_id):
        args = self.parser.parse_args()
        offer = OfferModel.query.get(offer_id)
        if offer:
            offer.offer_name = args['offer_name']
            offer.description = args['description']
            offer.previous_price = args['previous_price']
            offer.offer_price = args['offer_price']
            offer.timeline = args['timeline']
            offer.image_url = args['image_url']
            offer.insta_url = args['insta_url']
            offer.slots_limit = args['slots_limit']
            offer.rating = args['rating']
            db.session.commit()
            return marshal(offer, offer_fields), 200
        else:
            return {"message": "Offer not found"}, 404
    @jwt_required()
    @admin_required
    def delete(self, offer_id):
        offer = OfferModel.query.get(offer_id)
        if offer:
            db.session.delete(offer)
            db.session.commit()
            return {"message": "Offer deleted successfully"}, 204
        else:
            return {"message": "Offer not found"}, 404

