from datetime import date
from config import db, ma
from marshmallow import fields


class Rubric(db.Model):
    __tablename__ = "rubric"
    rubric_id = db.Column(db.Integer, primary_key=True)
    rubric_name = db.Column(db.String(32))
    rubric_marks = db.Column(db.String(10))
    rubric_parent = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"))


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_phone = db.Column(db.String(50))

    ads = db.relationship(
        "Ad",
        backref="user",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Ad.ad_date)",
    )


class Ad(db.Model):
    __tablename__ = "ad"
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_text = db.Column(db.String(512), nullable=False)
    ad_rubric = db.Column(db.Integer, db.ForeignKey("rubric.rubric_id"))
    ad_frame = db.Column(db.Integer, default=0)
    ad_owner = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    ad_date = db.Column(
        db.Date, default=date.today(), onupdate=date.today()
    )


class AdSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Ad
        sqla_session = db.session

    user = fields.Nested("AdUserSchema", default=None)
    rubric = fields.Nested("AdRubricSchema", default=None)


class AdRubricSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    rubric_id = fields.Int()
    rubric_name = fields.Str()
    rubric_marks = fields.Bool()
    rubric_parent = fields.Int()


class AdUserSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    user_id = fields.Int()
    user_phone = fields.Str()


class UserSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = User
        sqla_session = db.session

    ads = fields.Nested("UserAdSchema", default=[], many=True)


class UserAdSchema(ma.ModelSchema):
    def __init_subclass__(cls, **kwargs):
        super().__init__(strict=True, **kwargs)

    ad_id = fields.Int()
    ad_text = fields.Str()
    ad_rubric = fields.Int()
    ad_frame = fields.Bool()
    ad_owner = fields.Int()
    ad_date = fields.Str()


class RubricSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    class Meta:
        model = Rubric
        sqla_session = db.session

    ads = fields.Nested("RubricAdSchema", default=[], many=True)


class RubricAdSchema(ma.ModelSchema):
    def __init__(self, **kwargs):
        super().__init__(strict=True, **kwargs)

    ad_id = fields.Int()
    ad_text = fields.Str()
    ad_rubric = fields.Int()
    ad_frame = fields.Bool()
    ad_owner = fields.Int()
    ad_date = fields.Str()
