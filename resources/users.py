from flask_restful import Resource, fields, reqparse , marshal
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import UserModel, db

user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "phone": fields.String,
    "email": fields.String,
    "role": fields.String,
    "is_active": fields.Boolean,
    "merit_points": fields.Integer,
}


class userSchema(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('username', required=True, type=str, help="Enter the username")
    user_parser.add_argument('phone', required=True, type=str, help="Enter the phone number")
    user_parser.add_argument('email', required=True, type=str, help="Enter the email")
    user_parser.add_argument('password', required=True, type=str, help="Enter the password")
    user_parser.add_argument('role', required=False, type=str, help="Enter the role")
    user_parser.add_argument('is_active', required=False, type=bool, help="Enter the active status")
    user_parser.add_argument('merit_points', required=False, type=int, help="Enter the merit points")

    @jwt_required()
    def get(self, id):
        # we are using identity to get a specific user
        if id:
            user = UserModel.query.filter_by(id=id).first()
            if user:
                return marshal(user, user_fields)
            return {"message": "User not found", "status": "fail"}, 400
        
        current_user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id = current_user_id).first()
        if user:
           return marshal(user, user_fields)
        return {"message":"user not found", "status":"fail"}, 400

    def post(self):
        user_data = userSchema.user_parser.parse_args()
        user_data['password'] = generate_password_hash(user_data['password']).decode('utf-8')
        #check phone number format
        if not ((user_data['phone'].isdigit() and len(user_data['phone']) == 10 and 
             (user_data['phone'].startswith('01') or user_data['phone'].startswith('07'))) or 
            (user_data['phone'].startswith('+254') and len(user_data['phone']) == 13 and 
             user_data['phone'][4] == '7')):
         return {"message": "Invalid phone number format", "status": "fail"}, 400

        # Check if phone number already exists
        if UserModel.query.filter_by(phone=user_data['phone']).first():
            return {"message": "Phone number already exists", "status": "fail"}, 400

        if UserModel.query.filter_by(username=user_data['username']).first():
            return {"message": "username already exists", "status": "fail"}, 400

        # Check if email already exists
        if UserModel.query.filter_by(email=user_data['email']).first():
            return {"message": "Email already exists", "status": "fail"}, 400

        new_user = UserModel(**user_data)

        try:
            db.session.add(new_user)
            db.session.commit()

            db.session.refresh(new_user)
            user_json = new_user.to_json()

            access_token = create_access_token(identity=user_json['id'])
            refresh_token = create_refresh_token(identity=user_json['id'])

            return {
                "message": "Account created successfully",
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_json
            }, 201

        except Exception as e:
             print(f"Error: {e}")
             return {"message": "Failed to register user", "status": "fail"}, 500

    @jwt_required()
    def delete(self,id=None):
        current_user_id = get_jwt_identity()
        user = UserModel.query.get(current_user_id)
        if user and user.role == 'admin':
            user = UserModel.query.filter_by(id = id).first()
            try:
                db.session.delete(user)
                db.session.commit()
                return {"message": "Account deleted successfully"}, 200
            except Exception as e:
                return {"message": str(e)}, 500
        elif user:
            try:
                db.session.delete(user)
                db.session.commit()
                return {"message": "Account deleted successfully"}, 200
            except Exception as e:
                return {"message": str(e)}, 500
            
        return {"message": "User not found"}, 404


class Login(Resource):
    user_parser = reqparse.RequestParser()
    user_parser.add_argument('identifier', required=True, type=str, help="Enter email or username")
    user_parser.add_argument('password', required=True, type=str, help="Enter password")

    def post(self):
        data = Login.user_parser.parse_args()
        identifier = data['identifier']
        password = data['password']

        # Try to find the user by email or username 
        user = UserModel.query.filter((UserModel.email == identifier) | (UserModel.username == identifier)).first()

        if user:
            if check_password_hash(user.password, password):
                user_json = user.to_json()
                access_token = create_access_token(identity=user_json['id'])
                refresh_token = create_refresh_token(identity=user_json['id'])
                return {
                    "message": "Login successful",
                    "status": "success",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user_json
                }, 200
            else:
                return {"message": "Invalid email/username or password", "status": "fail"}, 401
        else:
            return {"message": "Invalid email/username or password", "status": "fail"}, 401

