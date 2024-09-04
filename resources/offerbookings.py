from flask import request, render_template
from flask_restful import Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserModel, OfferModel, UserOfferModel, db
from flask_mail import Message
# from app import mail  # Ensure your app is correctly configured with Flask-Mail

user_offer_fields = {
    "id": fields.Integer,
    "user_id": fields.Integer,
    "username": fields.String(attribute=lambda user_id: UserModel.query.get(user_id).username if user_id else None),
    "offer_id": fields.Integer,
    "offer_name": fields.String(attribute=lambda offer_id: OfferModel.query.get(offer_id).offer_name if offer_id else None),
}

class UserOfferResource(Resource):
    offer_parser = reqparse.RequestParser()
    offer_parser.add_argument('offer_id', type=int, required=True, help="Offer ID is required")

    @jwt_required()
    def post(self):
        args = self.offer_parser.parse_args()
        args['user_id'] = get_jwt_identity()

        # Check if the user has already booked this offer
        existing_booking = UserOfferModel.query.filter_by(user_id=args['user_id'], offer_id=args['offer_id']).first()
        if existing_booking:
            return {"message": "You have already booked this offer"}, 400

        user_offer = UserOfferModel(**args)

        # Fetch user and offer details
        user = UserModel.query.filter_by(id=args['user_id']).first()
        offer = OfferModel.query.filter_by(id=args['offer_id']).first()

        if not offer or offer.slots_limit <= 0:
            return {"message": "All offer products have been purchased, try your luck next time"}, 400

        if user and offer:
            offer.slots_limit -= 1
            db.session.commit()
            send_offerbookingconfirmation_email(user, offer)
            send_adminbooking_email(user, offer)
            db.session.add(user_offer)
            db.session.commit()
            return {
                "message": "Offer purchase has been received and will be acted upon within the next hours",
                "status": "success"
            }, 200

        return {"message": "Only registered users can make this offer purchase", "status": "fail"}, 400


def send_offerbookingconfirmation_email(user, offer):
    from app import mail 
    msg = Message(
        'Offer Booking Confirmation Email',
        sender='kevinmbari60@gmail.com',
        recipients=[user.email]
    )
    msg.html = render_template('offer_booking_confirmation.html', user=user, offer=offer)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully'}, 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {'message': 'Failed to send email'}, 500

def send_adminbooking_email(user, offer):
    from app import mail 
    admin_email = 'kevinmbari60@gmail.com'
    msg = Message(
        'New Offer Purchase',
        sender=admin_email,
        recipients=[admin_email]
    )
    msg.html = render_template('new_offer_booking_notification.html', user=user, offer=offer)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully'}, 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return {'message': 'Failed to send email'}, 500
