from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_bcrypt import generate_password_hash , check_password_hash
from sqlalchemy import func, event
from wtforms.validators import ValidationError


db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=False)
    merit_points = db.Column(db.Integer, default=0)
    
    orders = db.relationship('OrderModel', backref='user', lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship('NotificationModel', backref='user', lazy=True)
    feedbacks = db.relationship('FeedbackModel', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def update_password(self, new_password):
        self.password = generate_password_hash(new_password)
        db.session.commit()

    def to_json(self):
        return {
            "id": self.id,
            "role": self.role
        }


    def __repr__(self):
        return f"<UserModel {self.name}>"

@event.listens_for(UserModel.phone, 'set')
def validate_phone(target, value, oldvalue, initiator):
    if value:
        if value.startswith('07') or value.startswith('01'):
            if len(value) != 10:
                raise ValidationError({"message": "invalid phone number format", "status": "fail"}, 400)
        elif value.startswith('+254'):
            if len(value) != 13 or not value[4:].isdigit():
                raise ValidationError({"message": "invalid phone number format", "status": "fail"}, 400)

class ProductModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    stock_quantity = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String)
    insta_url = db.Column(db.String, nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    def __init__(self, name, description, price , stock_quantity, category, image_url, rating=None , insta_url = None):
        self.name = name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
        self.image_url = image_url
        self.insta_url = insta_url
        self.rating = rating

    def __repr__(self):
        return f"<ProductModel {self.name}>"

@event.listens_for(ProductModel.rating, 'set')
def validate_rating(target, value, oldvalue, initiator):
    if value is not None:
        return max(0, min(value, 5))
    return None

class OrderModel(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_amount = db.Column(db.Integer)
    status = db.Column(db.Boolean, default=False)
    
    # Remove product_id from the OrderModel
    
    # Instead of having a single product_id column, create a relationship
    # with ProductModel through a many-to-many relationship table
    order_items = db.relationship('OrderItemModel', backref='order', lazy=True, cascade="all, delete-orphan")


class OrderItemModel(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)
    
    # Establish relationship with ProductModel
    product = db.relationship('ProductModel', backref='ordered_items')


    
class NotificationModel(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    image_url = db.Column(db.String(255))
    timeline = db.Column(db.Integer, default=60)  
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def delete_expired_notifications(cls):
        expired_notifications = cls.query.filter(cls.timeline > 0).filter(
            func.utcnow() > (cls.created_at + timedelta(minutes=cls.timeline))
        ).all()
        for notification in expired_notifications:
            db.session.delete(notification)
        db.session.commit()

class OfferModel(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey('users.id'))
    offer_name = db.Column(db.String(100))
    description = db.Column(db.String)
    previous_price = db.Column(db.Integer, nullable=True)
    offer_price = db.Column(db.Integer)
    timeline = db.Column(db.Integer, default=60)
    image_url = db.Column(db.String)
    insta_url = db.Column(db.String, nullable=True)
    slots_limit = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    rating = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<OfferModel {self.name}>"
    

    @classmethod
    def delete_expired_offers(cls):
        expired_offers = cls.query.filter(cls.timeline > 0).filter(
            func.utcnow() > (cls.created_at + timedelta(minutes=cls.timeline))
        ).all()
        for offer in expired_offers:
            db.session.delete(offer)
            db.session.commit()

@event.listens_for(OfferModel.rating, 'set')
def validate_offer_rating(target, value, oldvalue, initiator):
        if value is not None:
            return max(0, min(value, 5))
        return None

class FeedbackModel(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String,nullable=False)
    comment = db.Column(db.String)
    rating = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    
    def __repr__(self):
        return f"<FeedbackModel {self.name}>"
    
    @classmethod
    def delete_old_feedbacks(cls):
        six_hours_ago = func.utcnow() - timedelta(hours=6)
        cls.query.filter(cls.created_at < six_hours_ago).delete()
        db.session.commit()

@event.listens_for(FeedbackModel.rating, 'set')
def validate_feedback_rating(target, value, oldvalue, initiator):
        if value is not None:
            return max(0, min(value, 5))
        return None

class UserOfferModel(db.Model):
    __tablename__ = 'user_offers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'))

    user = db.relationship('UserModel', backref='user_offers')
    offer = db.relationship('OfferModel', backref='user_offers')