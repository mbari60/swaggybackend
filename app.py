import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_migrate import Migrate
from flask_restful import Api 
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from models import db 

# the resources to create endpoints
from resources.users import userSchema,Login,user_fields

from resources.feedback import FeedbackResource
from resources.offers import OfferResource
from resources.products import ProductResource
from resources.notifications import NotificationResource 
from resources.offerbookings import UserOfferResource

from resources.orders import create_order, cancel_order, get_all_orders
from resources.passwords import reset_password, redeem_merit_points, change_password , order_delivered , get_profile

from admin.myusers import adminUsers


app = Flask(__name__)

CORS(app)
api = Api(app)
bcrypt = Bcrypt(app)
JWTManager(app)

#secret key for the app 
app.secret_key = os.environ.get('APP_SECRET_KEY')

#database and error handling setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# app.config['SQLALCHEMY_DATABASE_URI'] =   'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BUNDLE_ERRORS'] = True


db.init_app(app)
migration = Migrate(app, db)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Setup for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)


#defining the routes
api.add_resource(adminUsers, '/users')
# api.add_resource(adminUsers, '/users/<int:user_id>/<string:action>')

api.add_resource(userSchema, '/registration', '/registration/<int:id>')
api.add_resource(Login, '/login')

api.add_resource(ProductResource, '/products', '/products/<int:product_id>')

api.add_resource(FeedbackResource, '/feedbacks', '/feedbacks/<int:id>')
api.add_resource(OfferResource, '/offers', '/offers/<int:offer_id>')
api.add_resource(NotificationResource, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(UserOfferResource, '/offerbookings')

# api.add_resource(OrderResource, '/orders','/orders/<int:order_id>')

#order endpoints 
app.add_url_rule('/orders', 'create_order', create_order, methods=['POST'])
app.add_url_rule('/orders/<int:order_id>', 'cancel_order', cancel_order, methods=['DELETE'])
app.add_url_rule('/orders', 'get_all_orders', get_all_orders, methods=['GET'])

#password endpoints
app.add_url_rule('/profile', 'get_profile', get_profile, methods=['GET'])
app.add_url_rule('/resetpassword/<int:id>', 'reset_password', reset_password, methods=['PUT'])
app.add_url_rule('/redeemmeritpoints', 'redeem_merit_points', redeem_merit_points, methods=['PUT'])
app.add_url_rule('/changepassword', 'change_password', change_password, methods=['PUT'])
app.add_url_rule('/deliverydone/<int:order_id>', 'order_delivered', order_delivered, methods=['POST'])



if __name__ == '__main__':
    app.run(debug=False)
 