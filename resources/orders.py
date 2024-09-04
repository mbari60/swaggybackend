from flask import request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from models import UserModel, ProductModel, OrderModel, OrderItemModel, db
from admin.onlyadmin import admin_required
# Creating an  Order
@jwt_required()
def create_order():
    data = request.json
    user_id = get_jwt_identity()

    if not 'user_id' or 'order_items' not in data:
        return jsonify({'message': 'User ID and order items are required'}), 400

    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    order_items = data['order_items']
    total_amount = 0
    for item in order_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')

        product = ProductModel.query.get(product_id)
        if not product:
            return jsonify({'message': f'Product with ID {product_id} not found'}), 404

        unit_price = product.price
        total_amount += unit_price * quantity

    order = OrderModel(user_id=user_id, total_amount=total_amount)
    db.session.add(order)
    db.session.commit()

    for item in order_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')
        unit_price = ProductModel.query.get(product_id).price

        order_item = OrderItemModel(order_id=order.id, product_id=product_id, quantity=quantity, unit_price=unit_price)
        db.session.add(order_item)

    send_orderconfimation_email(user, order)
    send_admin_neworder_email(user, order)
    user.merit_points += 1
    db.session.commit()

    return jsonify({'message': 'Order created successfully', 'order_id': order.id, 'total_amount': total_amount}), 201

# Cancel Order
def cancel_order(order_id):
    order = OrderModel.query.get(order_id)

    if not order:
        return jsonify({'message': 'Order not found'}), 404

    current_user_id = request.json.get('user_id')
    if order.user_id != current_user_id:
        return jsonify({'message': 'You are not authorized to cancel this order'}), 403

    user = UserModel.query.filter_by(id=current_user_id).first()
    OrderItemModel.query.filter_by(order_id=order_id).delete()

    # send_order_cancellation_email_to_user(user, order)
    # send_order_cancellation_email_to_admin(user, order)

    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Order canceled successfully', "status": "success"}), 200

# Get All Orders
@jwt_required()
@admin_required
def get_all_orders():
    orders = OrderModel.query.all()
    order_list = []
    for order in orders:
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'status': order.status,
            'order_items': []
        }

        order_items = OrderItemModel.query.filter_by(order_id=order.id).all()
        for item in order_items:
            product = ProductModel.query.get(item.product_id)
            if product:
                order_data['order_items'].append({
                    'product_id': item.product_id,
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price
                })

        order_list.append(order_data)

    return jsonify(order_list), 200

# Email Functions
def send_admin_neworder_email(user, order):
    from app import mail
    msg = Message('Order purchased Confirmation Email', sender='kevinmbari60@gmail.com', recipients=[user.email])
    msg.html = render_template('order_confirmation_user.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status": "success"}, 200
    except:
        return {'message': 'Failed to send email', "status": "fail"}, 500

def send_orderconfimation_email(user, order):
    from app import mail
    admin_email ='kevinmbari600@gmail.com'
    msg = Message('Order purchased Confirmation Email', sender='kevinmbari60@gmail.com', recipients=[admin_email])
    msg.html = render_template('new_order_notification_admin.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status": "success"}, 200
    except:
        return {'message': 'Failed to send email', "status": "fail"}, 500

def send_order_cancellation_email_to_user(user, order):
    from app import mail
    msg = Message('Order Cancellation Notification', sender='your_email@example.com', recipients=[user.email])
    msg.html = render_template('order_cancellation_notification_user.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 500
    
def send_order_cancellation_email_to_admin(user, order):
    from app import mail
    admin_email = 'kevinmbari600@gmail.com'
    msg = Message('New Order Cancellation Notification', sender='your_email@example.com', recipients=[admin_email])
    msg.html = render_template('order_cancellation_notification_admin.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 400   
