from marshmallow import fields
from sqlalchemy import text
from sqlalchemy.orm import relationship

from config import db, ma


# marshmallow.exceptions.ValidationError:
#   {'rub_ads': {0: {'ad_doers': {0: {'doer_phone': ['Unknown field.'], 'doer_name': ['Unknown field.']}}},...
# in case [Doer] <- [association] -> [Ad]
# https://github.com/marshmallow-code/marshmallow/issues/1579

#   Implementation of
#
#  / [Doer] >-(@property)-> [AssocDoerToAd] --> [Ad] \  -> [Rubric] <-> [Rubric] (Recursion)
# <                                                   >
#  \ [Doer] <-- [AssocAdToDoer] <-(@property)-< [Ad] /  -> [User]
#


class AssocDoerToAd(db.Model):
    __tablename__ = 'assoc_doer_to_ad'
    ad_id = db.Column(db.Integer, primary_key=True)
    doer_id = db.Column(db.Integer, db.ForeignKey('doer.doer_id'))


class AssocAdToDoer(db.Model):
    __tablename__ = 'assoc_ad_to_doer'
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.ad_id'))
    doer_id = db.Column(db.Integer, primary_key=True)


class Doer(db.Model):
    __tablename__ = "doer"
    doer_id = db.Column(db.Integer, primary_key=True)
    doer_phone = db.Column(db.String(50), unique=True)
    doer_name = db.Column(db.String(50))

    @property
    def assoc_to_ad(self):
        return db.object_session(self).query(AssocDoerToAd)\
            .with_parent(self)\
            .filter(AssocDoerToAd.doer_id == self.doer_id).all()

    ads = db.relationship("AssocDoerToAd")


class Ad(db.Model):
    __tablename__ = "ad"
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_text = db.Column(db.String(512), nullable=False)
    ad_rubric = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"))
    ad_frame = db.Column(db.String(10))
    ad_issue = db.Column(db.Integer, default=4)
    ad_comment = db.Column(db.String(512))
    ad_issuer = db.Column(db.String(20), db.ForeignKey("user.username"))    # , default=current_user.username)
    ad_update = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    @property
    def assoc_to_doer(self):
        return db.object_session(self).query(Ad).with_parent(self).filter().all()

    ad_doers = db.relationship("AssocAdToDoer")


class Rubric(db.Model):
    __tablename__ = "rubric"
    rubric_id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(32))
    rubric_marks = db.Column(db.String(10))
    rubric_parent = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"))
    children = relationship("Rubric")


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

    rub_ads = fields.List(fields.Nested(lambda: AdDoerSchema()))


class AdDoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ad
        partial = True
        load_instance = True
        dateformat = '%d.%m.%Y'
        datetimeformat = '%d.%m.%Y %H:%M'

    ad_doers = fields.Nested(lambda: AssocAdToDoerSchema(), default=None)


class AssocAdToDoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AssocAdToDoer
        load_instance = True

    ad_doers = fields.List(fields.Nested(lambda: DoerAdSchema(exclude=("ads",)), default=None))


class DoerAdSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doer
        load_instance = True

    ads = fields.Nested(lambda: AdDoerSchema(exclude=("ad_doers",)), default=None)


class RubricSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rubric
        load_schema = True

    rub_ads = fields.List(fields.Nested(lambda: RubricSchema()))


# @event.listens_for(Doer, 'before_insert')
# def check_doers_dublicate(mapper, connection, target):
#     get_existing_doer = Doer.query.filter(Doer.doer_phone == target.doer_phone).one_or_none()
#     if get_existing_doer:
#         target.doer_id = get_existing_doer.doer_id
#
#         print(1)
