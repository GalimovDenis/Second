from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import ForeignKeyConstraint

from config import db, app
from models import RubricAdDoerSchema
from resourses.Rubrics import RUBRICS
from resourses.Test_data_Ads import RUBRIC_ADS_DOERS


@compiles(ForeignKeyConstraint, "mysql")
def process(element, compiler, **kw):
    element.deferrable = element.initially = element.match = None
    return compiler.visit_foreign_key_constraint(element, **kw)


engine_MySQL = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
engine_MySQL.execute("SET GLOBAL group_concat_max_len = 100000;")
engine_MySQL.execute("SET GLOBAL foreign_key_checks = 0;")
db.drop_all()
engine_MySQL.execute("SET GLOBAL foreign_key_checks = 1;")
db.create_all()
engine_MySQL.execute("insert into user(`username`, `password`, `authenticated`) "
                     "value ('admin', '$2b$12$7cLh2Ruv/RMmYNAaaDU5o.z8XNPNNSY.0MU3zlhMzqFbQ2DxyDjWa', 0);")

engine_MySQL.execute("INSERT INTO tolkuchka.rubric (rubric_id, rubric_name, rubric_marks, rubric_parent_id) "
                     "VALUES (1, 'ROOT', '', null);")

engine_MySQL.execute("INSERT INTO tolkuchka.rubric (rubric_id, rubric_parent_id, rubric_name, rubric_marks) VALUES"+RUBRICS+";")

for rub in RUBRIC_ADS_DOERS:
    schema = RubricAdDoerSchema()
    el = schema.load(rub, session=db.session)
    db.session.merge(el)
    db.session.flush()
    db.session.commit()
    # for ad in rub.get("rub_ads"):
    #     schema1 = AdSchema()
    #     el_ad = schema1.load(ad, session=db.session)
    #     db.session.add(el_ad)
    #     db.session.commit()
    #     # for doer in ad.get("ad_doers"):
        #     schema2 = DoerAdSchema()
        #     el_doer = schema2.load(doer, session=db.session)
        #     db.session.add(el_doer)
    db.session.flush()
    db.session.commit()
