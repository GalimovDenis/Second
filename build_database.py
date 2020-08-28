from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import ForeignKeyConstraint

from config import db, app
from models import RubricSchema, Rubric
from resourses.Rubrics import RUBRICS_JSON
from resourses.Test_data_Ads import RUBRIC_ADS_DOERS


@compiles(ForeignKeyConstraint, "mysql")
def process(element, compiler, **kw):
    element.deferrable = element.initially = element.match = None
    return compiler.visit_foreign_key_constraint(element, **kw)


engine_MySQL = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
engine_MySQL.execute("SET GLOBAL group_concat_max_len = 100000;")
engine_MySQL.execute("SET GLOBAL foreign_key_checks = 0;")
db.drop_all()
#
db.create_all()
engine_MySQL.execute("insert into user(`username`, `password`, `authenticated`) "
                     "value ('admin', '$2b$12$7cLh2Ruv/RMmYNAaaDU5o.z8XNPNNSY.0MU3zlhMzqFbQ2DxyDjWa', 0);")

# engine_MySQL.execute("INSERT INTO tolkuchka.rubric (rubric_id, rubric_name, rubric_marks, rubric_parent_id) VALUES(1, 'ROOT', '', null);")

# engine_MySQL.execute("INSERT INTO tolkuchka.rubric (rubric_id, rubric_parent_id, rubric_name,
# rubric_marks) VALUES"+RUBRICS+";")

schema = RubricSchema()
el = schema.load(RUBRICS_JSON, session=db.session)
db.session.merge(el)
db.session.flush()
db.session.commit()
for child_json in RUBRICS_JSON.get("rubric_children"):
    child = schema.load(child_json, session=db.session)
    root = db.session.query(Rubric).filter(Rubric.rubric_id == el.rubric_id).one_or_none()
    child.rubric_parent_id = root.rubric_id
    db.session.merge(child)
    db.session.flush()
    db.session.commit()
    if child_json.get("rubric_children"):
        for grand_child_json in child_json.get("rubric_children"):
            grand_child = schema.load(grand_child_json, session=db.session)
            grand_child.rubric_parent_id = child.rubric_id
            db.session.merge(grand_child)
            db.session.flush()
            db.session.commit()
            if grand_child_json.get("rubric_children"):
                for grand_grand_child_json in grand_child_json.get("rubric_children"):
                    grand_grand_child = schema.load(grand_grand_child_json, session=db.session)
                    grand_grand_child.rubric_parent_id = grand_child.rubric_id
                    db.session.merge(grand_grand_child)
                    db.session.flush()
                    db.session.commit()

engine_MySQL.execute("SET GLOBAL foreign_key_checks = 1;")

for rubric_json in RUBRIC_ADS_DOERS:
    schemaAd = RubricSchema()
    data_rubric = schema.load(rubric_json, session=db.session)
    rubric = db.session.query(Rubric).filter(Rubric.rubric_id == data_rubric.rubric_id).one_or_none()
    db.session.merge(data_rubric)
    db.session.flush()
    db.session.commit()



