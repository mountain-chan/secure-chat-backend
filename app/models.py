# coding: utf-8
from sqlalchemy import Index

from app.enums import AVATAR_PATH_SEVER, DEFAULT_AVATAR
from app.extensions import db
from flask_jwt_extended import decode_token, get_jwt_identity, get_raw_jwt
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from app.utils import send_error, get_timestamp_now


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), default="Group Chat")
    avatar_path = db.Column(db.String(255), default=AVATAR_PATH_SEVER + DEFAULT_AVATAR)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    modified_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())

    # messages = db.relationship('GroupMessage', cascade="all,delete")
    group_user = db.relationship('GroupUser', cascade="all,delete")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "avatar_path": self.avatar_path,
            "created_date": self.created_date,
            "modified_date": self.modified_date
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "name": o.name,
                "avatar_path": o.avatar_path,
                "created_date": o.created_date,
                "modified_date": o.modified_date
            }
            items.append(item)
        return items

    @classmethod
    def get_all(cls, page=1, page_size=10):
        return cls.query.order_by(cls.created_date).paginate(page=page, per_page=page_size, error_out=False).items

    @classmethod
    def get_groups_by_user(cls, page=1, page_size=10):
        return cls.query.join(GroupUser, GroupUser.group_id == cls.id) \
            .filter(GroupUser.user_id == get_jwt_identity()) \
            .order_by(cls.created_date) \
            .paginate(page=page, per_page=page_size, error_out=False).items

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
    test_message = db.Column(TEXT, default="test message")
    is_deleted = db.Column(db.Boolean, default=False)

    def get_password_age(self):
        return int((get_timestamp_now() - self.modified_date_password) / 86400)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "gender": self.gender,
            "force_change_password": self.force_change_password,
            "created_date": self.created_date,
            "avatar_path": self.avatar_path,
            "pub_key": self.pub_key
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "username": o.username,
                "display_name": o.display_name,
                "gender": o.gender,
                "force_change_password": o.force_change_password,
                "created_date": o.created_date,
                "avatar_path": o.avatar_path,
                "pub_key": o.pub_key
            }
            items.append(item)
        return items

    @classmethod
    def get_all(cls, page=1, page_size=10):
        return cls.query.filter_by(is_deleted=False).order_by(cls.username) \
            .paginate(page=page, per_page=page_size, error_out=False).items

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
        return cls.query.filter_by(group_id=group_id).all()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()


class Friend(db.Model):
    __tablename__ = 'friends'

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id'))
    friend_id = db.Column(db.ForeignKey('users.id'))
    group_id = db.Column(db.String(50), nullable=False)

    @classmethod
    def get_by_id(cls, _id):
        return cls.query.get(_id)

    @classmethod
    def check_friend(cls, friend_id):
        return cls.query.filter_by(user_id=get_jwt_identity(), friend_id=friend_id).first()

    @classmethod
    def get_friends(cls, user_id, page, page_size):
        objects = cls.query.filter(cls.user_id == user_id). \
            paginate(page=page, per_page=page_size, error_out=False).items
        friends_id = [obj.friend_id for obj in objects]
        friends = User.query.filter(User.id.in_(friends_id)).all()
        return User.many_to_json(friends)


class Message(db.Model):
    __tablename__ = 'messages'
    __table_args__ = (
        Index('index_get', 'group_id', 'created_date'),
    )
    # TODO oder_by desc filed created_date

    id = db.Column(db.String(50), primary_key=True)
    sender_id = db.Column(db.ForeignKey('users.id'))
    receiver_id = db.Column(db.ForeignKey('users.id'))
    group_id = db.Column(db.String(50), nullable=False)
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    seen = db.Column(db.Boolean, default=False)

    message_user = db.relationship('UserMessage', cascade="all,delete")

    @staticmethod
    def to_json(obj):
        return {
            "id": obj.Message.id,
            "message": obj.message,
            "sender_id": obj.Message.sender_id,
            "receiver_id": obj.Message.receiver_id,
            "created_date": obj.Message.created_date,
            "seen": obj.Message.seen
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for obj in objects:
            item = {
                "id": obj.Message.id,
                "message": obj.message,
                "sender_id": obj.Message.sender_id,
                "receiver_id": obj.Message.receiver_id,
                "created_date": obj.Message.created_date,
                "seen": obj.Message.seen
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
    def get_list_chats(cls):
        current_user_id = get_jwt_identity()
        objects = cls.query.filter((cls.sender_id == current_user_id) | (cls.receiver_id == current_user_id)) \
            .group_by(cls.group_id).all()
        friends_id = []
        for obj in objects:
            friends_id.append(obj.sender_id) if obj.sender_id != current_user_id else friends_id.append(obj.receiver_id)
        friends = User.query.filter(User.id.in_(friends_id)).all()
        return User.many_to_json(friends)

    @classmethod
    def get_messages(cls, group_id, page=1, page_size=10):
        return cls.query.filter_by(group_id=group_id) \
            .add_columns(UserMessage.message) \
            .join(UserMessage, cls.id == UserMessage.message_id) \
            .filter(UserMessage.user_id == get_jwt_identity()) \
            .order_by(cls.created_date.desc()).paginate(page=page, per_page=page_size, error_out=False).items


class UserMessage(db.Model):
    __tablename__ = 'user_messages'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(TEXT)
    user_id = db.Column(db.ForeignKey('users.id'))
    message_id = db.Column(db.ForeignKey('messages.id'))

    def to_json(self):
        return {
            "id": self.id,
            "message": self.message,
            "user_id": self.user_id,
            "message_id": self.message_id
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "message": o.message,
                "user_id": o.user_id,
                "message_id": o.message_id
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
    def get_message(cls, user_id, message_id):
        return cls.query.filter_by(user_id=user_id, message_id=message_id).first()


class GroupMessage(db.Model):
    __tablename__ = 'group_messages'

    id = db.Column(db.String(50), primary_key=True)
    sender_id = db.Column(db.ForeignKey('users.id'))
    group_id = db.Column(db.ForeignKey('groups.id'))
    created_date = db.Column(INTEGER(unsigned=True), default=get_timestamp_now())
    message_user = db.relationship('UserMessageGroup', cascade="all,delete")

    @staticmethod
    def to_json(obj):
        return {
            "id": obj.GroupMessage.id,
            "sender_id": obj.GroupMessage.sender_id,
            "group_id": obj.GroupMessage.group_id,
            "created_date": obj.GroupMessage.created_date,
            "message": obj.message,
            "seen": obj.seen,
        }

    @staticmethod
    def many_to_json1(objects):
        items = []
        for obj in objects:
            item = {
                "id": obj.id,
                "sender_id": obj.sender_id,
                "group_id": obj.group_id,
                "created_date": obj.created_date
            }
            items.append(item)
        return items

    @staticmethod
    def many_to_json(objects):
        items = []
        for obj in objects:
            item = {
                "id": obj.GroupMessage.id,
                "message": obj.message,
                "sender_id": obj.GroupMessage.sender_id,
                "group_id": obj.GroupMessage.group_id,
                "created_date": obj.GroupMessage.created_date,
                "seen": obj.seen
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
    def get_messages(cls, group_id, page=1, page_size=10):
        return cls.query.filter_by(group_id=group_id) \
            .add_columns(UserMessageGroup.message) \
            .add_columns(UserMessageGroup.seen) \
            .join(UserMessageGroup, cls.id == UserMessageGroup.message_id) \
            .filter(UserMessageGroup.user_id == get_jwt_identity()) \
            .order_by(cls.created_date.desc()).paginate(page=page, per_page=page_size, error_out=False).items


class UserMessageGroup(db.Model):
    __tablename__ = 'user_messages_group'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(TEXT)
    user_id = db.Column(db.ForeignKey('users.id'))
    group_id = db.Column(db.ForeignKey('groups.id'))
    message_id = db.Column(db.ForeignKey('group_messages.id'))
    seen = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            "id": self.id,
            "message": self.message,
            "user_id": self.user_id,
            "message_id": self.message_id
        }

    @staticmethod
    def many_to_json(objects):
        items = []
        for o in objects:
            item = {
                "id": o.id,
                "message": o.message,
                "user_id": o.user_id,
                "message_id": o.message_id
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
    def get_message(cls, user_id, message_id):
        return cls.query.filter_by(user_id=user_id, message_id=message_id).first()


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
        token = Token.query.filter_by(jti=jti).first()
        if token:
            return token.revoked
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

            tokens = Token.query.filter(Token.user_identity.in_(users_identity), Token.revoked == False).all()

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
            tokens = Token.query.filter(Token.user_identity == users_identity, Token.revoked == False,
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
