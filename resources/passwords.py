from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserModel, db , OrderModel
from admin.onlyadmin import admin_required
from resources.users import user_fields
from flask_restful import marshal

@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = UserModel.query.filter_by(id = current_user).all()
    return marshal(user, user_fields), 200

# Reset Password
@admin_required
@jwt_required()
def reset_password(id=None):
    data = request.json
    user_id = get_jwt_identity()

    if id:  # Admin resetting a user's password
        admin = UserModel.query.filter_by(id=user_id).first()
        if admin and admin.role == 'admin':
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            new_password = data.get('password')
            user.update_password(new_password)
            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"error": "Admin access required"}), 403

    # User resetting their own password
    email = data.get('email')
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_password = data.get('new_password')
    user.update_password(new_password)
    return jsonify({"message": "Password reset successfully"}), 200

# Redeem Merit Points
@jwt_required()
def redeem_merit_points():
    data = request.json
    user_id = get_jwt_identity()
    points_to_redeem = data.get('points')

    user = UserModel.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.merit_points < points_to_redeem:
        return jsonify({"message": "Insufficient merit points"}), 400

    user.merit_points -= points_to_redeem
    db.session.commit()
    return jsonify({"message": "Merit points redeemed successfully"}), 200

# Change Password
@jwt_required()
def change_password():
    data = request.json
    user_id = get_jwt_identity()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user = UserModel.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(old_password):
        return jsonify({"error": "Incorrect old password"}), 400

    user.update_password(new_password)
    return jsonify({"message": "Password changed successfully"}), 200

@jwt_required()
@admin_required
def order_delivered(order_id):
    order = OrderModel.query.filter_by(id=order_id).first()
    if order:
        order.status = True
        db.session.commit()
        return {"message":"Successfully delivered" , "status":"Success"},200
    return {'message': 'failed to mark as delivered' , "status":"fail"}, 400

