# routers/auth.py
import json
from datetime import datetime, timedelta
from functools import wraps
from types import SimpleNamespace

import jwt
from flask import Blueprint, request, jsonify, g, current_app
from injectors.connections import pg
from models.user import User
from sqlalchemy import select

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def create_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(
            seconds=current_app.config.get('JWT_TTL_SECONDS', 24 * 3600)
        ),
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET'],
        algorithm=current_app.config['JWT_ALGO'],
    )


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET'],
            algorithms=[current_app.config['JWT_ALGO']],
        )
    except jwt.PyJWTError:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', "")
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth.split(' ', 1)[1]
        payload = decode_token(token)
        if not payload or 'user_id' not in payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # 1) Попытка взять из Redis (если настроен)
        redis_client = getattr(current_app, 'redis', None)
        if redis_client:
            try:
                user_json = redis_client.get(f'token:{token}')
            except Exception:
                user_json = None

            if user_json:
                try:
                    # Redis возвращает bytes -> decode
                    if isinstance(user_json, (bytes, bytearray)):
                        user_json = user_json.decode('utf-8')
                    data = json.loads(user_json)
                    g.user = SimpleNamespace(**data)
                    return f(*args, **kwargs)
                except Exception:
                    # fallthrough -> попробуем БД
                    pass

        # 2) Fallback — получить пользователя из БД (без долгой транзакции)
        session = pg._pg()
        try:
            try:
                # короткая транзакция на чтение
                with session.begin():
                    user = session.execute(select(User).where(User.id == int(payload['user_id']))).scalar_one_or_none()
            except Exception:
                user = None

            if not user:
                return jsonify({'error': 'Unauthorized'}), 401

            # приводим к простому namespace чтобы остальной код работал (id, username)
            g.user = SimpleNamespace(id=int(user.id), username=user.username)
            return f(*args, **kwargs)
        finally:
            try:
                session.close()
            except Exception:
                pass

    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password or len(password) < 8:
        return jsonify({'error': 'invalid params'}), 400

    session = pg._pg()
    try:
        with session.begin():
            exists = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()
            if exists:
                return jsonify({'error': 'username exists'}), 400

            user = User(
                username=username,
                password_hash=User.hash_password(password),
            )
            session.add(user)
            session.flush()
            user_id = user.id
            user_name = user.username
    finally:
        try:
            session.close()
        except Exception:
            pass

    return jsonify({'id': user_id, 'username': user_name}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    session = pg._pg()
    try:
        with session.begin():
            user = session.execute(
                select(User).where(User.username == username)
            ).scalar_one_or_none()

        if not user or not user.verify_password(password):
            return jsonify({'error': 'invalid credentials'}), 401

        token = create_token(user.id)

        # Сохраняем в Redis, если есть
        redis_client = getattr(current_app, 'redis', None)
        if redis_client:
            try:
                key = f'token:{token}'
                payload = {'id': int(user.id), 'username': user.username}
                ttl = current_app.config.get('JWT_TTL_SECONDS', 24 * 3600)
                redis_client.set(key, json.dumps(payload), ex=ttl)
            except Exception:
                # если Redis недоступен — продолжаем без него
                pass

        return jsonify({
            'id': user.id,
            'username': user.username,
            'token': token,
        })

    finally:
        try:
            session.close()
        except Exception:
            pass


@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization', "")
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1]
        redis_client = getattr(current_app, 'redis', None)
        if redis_client:
            try:
                redis_client.delete(f'token:{token}')
            except Exception:
                pass

    return jsonify({'detail': 'logged out'}), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def me():
    return jsonify({
        'id': g.user.id,
        'username': g.user.username,
    })
