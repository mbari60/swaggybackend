from flask_restful import Resource, reqparse, fields, marshal
from models import NotificationModel, db
from datetime import datetime, timedelta

notification_fields = {
    "id": fields.Integer,
    "description": fields.String,
    "image_url": fields.String,
    "timeline": fields.Integer,
    "created_at": fields.DateTime(dt_format="iso8601"),
    "user_id": fields.Integer,
}

class NotificationResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('description', type=str, required=True, help="Description is required")
        self.parser.add_argument('image_url', type=str)
        self.parser.add_argument('timeline', type=int, default=60)

    def get(self, notification_id=None):
        if notification_id:
            notification = NotificationModel.query.get(notification_id)
            if notification:
                return marshal(notification, notification_fields), 200
            else:
                return {"message": "Notification not found"}, 404
        else:
            notifications = NotificationModel.query.all()
            if notifications:
                return marshal(notifications, notification_fields)
            else:
                return {"message": "No notifications available"}, 404

    def post(self):
        args = self.parser.parse_args()
        notification = NotificationModel(**args)
        db.session.add(notification)
        db.session.commit()
        return marshal(notification, notification_fields), 201

    def delete(self, notification_id):
        notification = NotificationModel.query.filter_by(id = notification_id).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return {"message": "Notification deleted successfully"}, 204
        else:
            return {"message": "Notification not found"}, 404
    
    def put(self, notification_id):
        args = self.parser.parse_args()
        notification = NotificationModel.query.get(notification_id)
        if notification:
            for key, value in args.items():
                setattr(notification, key, value)
            db.session.commit()
            return marshal(notification, notification_fields), 200
        else:
            return {"message": "notification not found"}, 404