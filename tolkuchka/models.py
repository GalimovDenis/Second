from datetime import datetime

from marshmallow import fields

from config import db, ma


class Rubric(db.Model):
    __tablename__ = "rubric"
    rubric_id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(32))
    rubric_marks = db.Column(db.String(10))
    rubric_parent = db.Column(db.Integer)


class Doer(db.Model):
    __tablename__ = "doer"
    doer_id = db.Column(db.Integer, primary_key=True)
    doer_phone = db.Column(db.String(50))

    ads = db.relationship(
        "Ad",
        backref="user",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Ad.ad_timestamp)",
    )


class Ad(db.Model):
    __tablename__ = "ad"
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_text = db.Column(db.String(512), nullable=False)
    ad_rubric = db.Column(db.Integer)
    ad_frame = db.Column(db.Integer, default=0)
    ad_owner = db.Column(db.Integer, db.ForeignKey("doer.doer_id"))
    ad_issuer = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    ad_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow()
    )


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20))
    user_mail = db.Column(db.String(30), unique=True)
    user_hash = db.Column(db.String)


class RubricAdDoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rubric
        load_instance = True

    ads = fields.Nested(lambda: AdSchema(exclude=("rubric",)), default=None)


class AdSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ad
        load_instance = True

    user = fields.Nested(lambda: DoerSchema(exclude=("ads",)), default=None)


class DoerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doer
        load_instance = True

    ads = fields.Nested(AdSchema, default=[], many=True)


class RubricSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rubric
        load_schema = True
