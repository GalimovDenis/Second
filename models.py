from marshmallow import fields, pre_load
from sqlalchemy import text

from config import db, ma

# marshmallow.exceptions.ValidationError:
#   {'rub_ads': {0: {'ad_doers': {0: {'doer_phone': ['Unknown field.'], 'doer_name': ['Unknown field.']}}},...
# in case [Doer] <- [association] -> [Ad]
# error deserialization objects with relationship 'many-to-many'
# https://github.com/marshmallow-code/marshmallow/issues/1579

#   Implementation of
#
# [Doer] <-- assoc_ad_doer --> [Ad]  --> [Rubric] <-> [Rubric] (Recursion)
#                                |
#                                V
#                              [User]


assoc_ad_doer = db.Table('assoc_ad_doer', db.metadata,
                         db.Column('ad_id', db.Integer, db.ForeignKey('ad.ad_id')),
                         db.Column('doer_phone', db.Integer, db.ForeignKey('doer.doer_phone'))
                         )


class Doer(db.Model):
    __tablename__ = "doer"
    doer_phone = db.Column(db.String(50), primary_key=True)
    doer_name = db.Column(db.String(50))

#    ads = db.relationship("Ad", secondary=assoc_ad_doer)


class Ad(db.Model):
    __tablename__ = "ad"
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_text = db.Column(db.String(512), nullable=False)
    ad_rubric_id = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"))
    ad_frame = db.Column(db.String(10))
    ad_issue = db.Column(db.Integer, default=4)
    ad_comment = db.Column(db.String(512))
    ad_issuer = db.Column(db.String(20), db.ForeignKey("user.username"))  # , default=current_user.username)
    ad_update = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    # ad_rubric = db.relationship("Rubric")
    ad_doers = db.relationship("Doer", secondary=assoc_ad_doer)


class Rubric(db.Model):
    __tablename__ = "rubric"
    rubric_id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(32))
    rubric_marks = db.Column(db.String(10))
    rubric_parent_id = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"), default=0)
    rubric_parent = db.relationship("Rubric")

    rub_ads = db.relationship("Ad")


class User(db.Model):
    __tablename__ = "user"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(200))
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satify Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class RubricAdDoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rubric
        load_instance = True

    rub_ads = fields.List(fields.Nested(lambda: AdSchema()))

    @pre_load
    def get_exist_id(self, in_data, **kwargs):
        if hasattr(in_data, 'rubric_parent_id'):
            get_id = db.session.query(Rubric)\
                .filter(Rubric.rubric_parent_id == in_data["rubric_parent_id"])\
                .filter(Rubric.rubric_name == in_data["rubric_name"])\
                .one_or_none()
            if get_id:
                in_data["rubric_id"] = get_id.rubric_id
        return in_data


class AdSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ad
        partial = True
        load_instance = True
        dateformat = '%d.%m.%Y'
        datetimeformat = '%d.%m.%Y %H:%M'

    ad_doers = fields.List(fields.Nested(lambda: DoerSchema(), default=None))

    @pre_load
    def get_rubric_id(self, in_data, **kwargs):
        id = in_data
        return id


class DoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doer
        load_instance = True

    ads = fields.List(fields.Nested(lambda: AdSchema(exclude=("ad_doers",)), default=None))

    @pre_load
    def get_exist_id(self, in_data, **kwargs):
        get_id = db.session.query(Doer).filter(Doer.doer_phone == in_data["doer_phone"]).one_or_none()
        if get_id:
            in_data["doer_id"] = get_id.doer_id
        return in_data
