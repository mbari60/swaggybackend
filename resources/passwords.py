from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserModel, db , OrderModel
from admin.onlyadmin import admin_required
from resources.users import user_fields
from flask_restful import marshal
from flask_mail import Message

@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = UserModel.query.filter_by(id = current_user).all()
    return marshal(user, user_fields), 200

# Reset Password
@jwt_required()
@admin_required
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
    from app import mail
    order = OrderModel.query.filter_by(id=order_id).first()

    if order:
        user = UserModel.query.filter_by(id=order.user_id).first()
        if user and user.email:
            # Update order status
            order.status = True
            db.session.commit()

            # HTML email template with dynamic content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                        -webkit-font-smoothing: antialiased;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 40px auto;
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }}
                    .email-header {{
                        text-align: center;
                        background-color: #007bff;
                        color: white;
                        padding: 20px 0;
                        border-radius: 8px 8px 0 0;
                    }}
                    .email-header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .email-body {{
                        padding: 20px;
                        text-align: center;
                        color: #333333;
                    }}
                    .email-body p {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .email-footer {{
                        text-align: center;
                        margin-top: 40px;
                        color: #888888;
                        font-size: 12px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <h1>Order Delivered!</h1>
                    </div>
                    <div class="email-body">
                        <p>Dear {user.username},</p>
                        <p>Your order <strong>#{order.id}</strong> has been successfully delivered.</p>
                        <p>you have received 1 merit-point for shopping with us and you can redeem it later for cash or free delivery</p>
                        <p>Thank you for shopping with Swaggy Sphere! We hope you enjoy your purchase and look forward to serving you again.</p>
                        <a href="https://swagy-eosin.vercel.app/products" class="button">Keep Shopping</a>
                    </div>
                    <div class="email-footer">
                        &copy; 2024 Swaggy Sphere | All Rights Reserved
                    </div>
                </div>
            </body>
            </html>
            """

            # Send email to user
            msg = Message("Your Order Has Been Delivered!",
                          recipients=[user.email])
            msg.html = html_content  # Attach HTML content to the email

            try:
                mail.send(msg)
                return {"message": "Successfully delivered and email sent", "status": "Success"}, 200
            except Exception as e:
                return {"message": "Order delivered, but failed to send email", "status": "Partial Success"}, 200

        return {"message": "Successfully delivered", "status": "Success"}, 200

    return {'message': 'Failed to mark as delivered', "status": "Fail"}, 400


