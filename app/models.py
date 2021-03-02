# coding: utf-8
from app.enums import AVATAR_PATH_SEVER, DEFAULT_AVATAR
from app.extensions import db
from flask_jwt_extended import decode_token, get_jwt_identity, get_raw_jwt
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from app.utils import send_error, get_timestamp_now


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.String(50), primary_key=True)
    group_name = db.Column(db.String(100), default="Group Chat")
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())

    messages = db.relationship('Message', cascade="all,delete")
    group_user = db.relationship('GroupUser', cascade="all,delete")

    def to_json(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "created_date": self.created_date,
            "modified_date": self.modified_date
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "group_name": o.group_name,
                "created_date": o.created_date,
                "modified_date": o.modified_date
            }
            items.append(item)
        return items

    @classmethod
    def get_all(cls, page_number=1, page_size=10):
        return cls.query.order_by(cls.created_date).paginate(page=page_number, per_page=page_size).items

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    pub_key = db.Column(TEXT, nullable=False)
    gender = db.Column(db.Boolean, default=0)
    display_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    address = db.Column(db.String(255))
    login_failed_attempts = db.Column(db.SmallInteger, default=0)
    force_change_password = db.Column(db.Boolean, default=0)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    modified_date_password = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    avatar_path = db.Column(db.String(255), default=AVATAR_PATH_SEVER + DEFAULT_AVATAR)

    messages = db.relationship('Message', cascade="all,delete")

    def get_password_age(self):
        return int((get_timestamp_now() - self.modified_date_password) / 86400)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "force_change_password": self.force_change_password,
            "created_date": self.created_date,
            "avatar_path": self.avatar_path
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "username": o.username,
                "display_name": o.display_name,
                "force_change_password": o.force_change_password,
                "created_date": o.created_date,
                "avatar_path": o.avatar_path
            }
            items.append(item)
        return items

    @classmethod
    def get_all(cls, page_number=1, page_size=10):
        return cls.query.order_by(cls.username).paginate(page=page_number, per_page=page_size).items

    @classmethod
    def get_current_user(cls):
        return cls.query.get(get_jwt_identity())

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)


class GroupUser(db.Model):
    __tablename__ = 'group_user'

    user_id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    group_id = db.Column(db.ForeignKey('groups.id'), primary_key=True)

    @classmethod
    def get_by_group_id(cls, group_id):
        return cls.query.filter_by(group_id=group_id).first()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.String(50), primary_key=True)
    message_hash = db.Column(TEXT)
    sender_id = db.Column(db.ForeignKey('users.id'))
    group_id = db.Column(db.ForeignKey('groups.id'))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())

    def to_json(self):
        return {
            "id": self.id,
            "message_hash": self.message_hash,
            "sender_id": self.sender_id,
            "group_id": self.group_id,
            "created_date": self.created_date
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "message_hash": o.message_hash,
                "sender_id": o.sender_id,
                "group_id": o.group_id,
                "created_date": o.created_date
            }
            items.append(item)
        return items

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def get_messages(cls, group_id, page_number=1, page_size=10):
        return cls.query.filter_by(group_id=group_id).order_by(
            cls.created_date.desc()).paginate(page=page_number, per_page=page_size).items


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(INTEGER(unsigned=True), nullable=False)

    @staticmethod
    def add_token_to_database(encoded_token, user_identity):
        """
        Adds a new token to the database. It is not revoked when it is added.
        :param encoded_token:
        :param user_identity:
        """
        decoded_token = decode_token(encoded_token)
        jti = decoded_token['jti']
        token_type = decoded_token['type']
        expires = decoded_token['exp']
        revoked = False

        db_token = Token(
            jti=jti,
            token_type=token_type,
            user_identity=user_identity,
            expires=expires,
            revoked=revoked,
        )
        db.session.add(db_token)
        db.session.commit()

    @staticmethod
    def is_token_revoked(decoded_token):
        """
        Checks if the given token is revoked or not. Because we are adding all the
        tokens that we create into this database, if the token is not present
        in the database we are going to consider it revoked, as we don't know where
        it was created.
        """
        jti = decoded_token['jti']
        try:
            token = Token.query.filter_by(jti=jti).one()
            return token.revoked
        except Exception:
            return True

    @staticmethod
    def revoke_token(jti):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database
        """
        try:
            token = Token.query.filter_by(jti=jti).first()
            token.revoked = True
            db.session.commit()
        except Exception as ex:
            return send_error(message=str(ex))

    @staticmethod
    def revoke_all_token(users_identity):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database.
        Set token Revoked flag is False to revoke this token.
        Args:
            users_identity: list or string, require
                list users id or user_id. Used to query all token of the user on the database
        """
        try:
            if type(users_identity) is not list:
                # convert user_id to list user_ids
                users_identity = [users_identity]

            tokens = Token.query.filter(Token.user_identity.in_(users_identity), Token.revoked is False).all()

            for token in tokens:
                token.revoked = True
            db.session.commit()
        except Exception as ex:
            return send_error(message=str(ex))

    @staticmethod
    def revoke_all_token2(users_identity):
        """
        Revokes all token of the given user except current token. Raises a TokenNotFound error if the token does
        not exist in the database.
        Set token Revoked flag is False to revoke this token.
        Args:
            users_identity: user id
        """
        jti = get_raw_jwt()['jti']
        try:
            tokens = Token.query.filter(Token.user_identity == users_identity, Token.revoked is False,
                                        Token.jti != jti).all()
            for token in tokens:
                token.revoked = True
            db.session.commit()
        except Exception as ex:
            return send_error(message=str(ex))

    @staticmethod
    def prune_database():
        """
        Delete tokens that have expired from the database.
        How (and if) you call this is entirely up you. You could expose it to an
        endpoint that only administrators could call, you could run it as a cron,
        set it up with flask cli, etc.
        """
        now_in_seconds = get_timestamp_now()
        Token.query.filter(Token.expires < now_in_seconds).delete()
        db.session.commit()
