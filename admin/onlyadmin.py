from functools import wraps
from flask_jwt_extended import get_jwt_identity
from models import UserModel

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=current_user_id).first()
        if not user or user.role != 'admin':
            return {"message": "Admins only!"}, 403
        return fn(*args, **kwargs)

    return wrapper