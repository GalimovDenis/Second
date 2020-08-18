from flask import make_response, abort
from flask_login import login_required

from config import db
from models import Rubric, RubricSchema, Ad


@login_required
def read_all():
    """
    This function responds to a request for /rubrics
    with the complete lists of rubric

    :return:    json string of tree of rubric
    """

    # Create the ONE big object rubric from our data, we need just ONE.
    rubric = Rubric.query.filter(Rubric.rubric_id == 1).all()

    # Serialize the data for the response
    rubric_schema = RubricSchema(many=True)

    data = rubric_schema.dump(rubric)

    return data


@login_required
def read_one(rubric_id):
    """
    This function responds to a request for /rubric/{rubric_id}
    with one matching rubric from rubrics

    :param rubric_id:   Id of the rubric to find
    :return:            rubric matching id
    """
    # Build the initial query
    rubric = (
        Rubric.query.filter(Rubric.rubric_id == rubric_id)
            .outerjoin(Ad)
            .one_or_none()

    )

    # Did we find a rubric?
    if rubric is not None:

        # Serialize the data for the response
        rubric_schema = RubricSchema()
        data = rubric_schema.dump(rubric)
        return data

    # otherwise, nope, didn't find that rubric
    else:
        abort(404, f"Rubric not found for Id: {rubric_id}")


@login_required
def create(rubric):
    """
    This function creates a new rubric in the rubrics structure
    based on the passed in rubric data

    :param rubric:  rubric to create in rubrics structure
    :return:        201 on success, 406 on rubric exists
    """
    rubric_parent = rubric.get("rubric_parent")
    rubric_name = rubric.get("rubric_name")

    existing_rubric = (
        Rubric.query.filter(Rubric.rubric_parent == rubric_parent)
            .filter(Rubric.rubric_name == rubric_name)
            .one_or_none()
    )

    # Can we insert the rubric?
    if existing_rubric is None:

        # Create a rubric instance using the schema and passed in rubric
        schema = RubricSchema()
        new_rubric = schema.load(rubric, session=db.session).data

        # Add the rubric to the database
        db.session.add(new_rubric)
        db.session.commit()

        # Serialize and return the newly created rubric in the response
        data = schema.dump(new_rubric).data

        return data, 201

    # Otherwise, nope, rubric exists already
    else:
        abort(409, f"Rubric {rubric_name} in {rubric_parent} exists already")


@login_required
def update(rubric_id, rubric):
    """
    This function updates an existing rubric in the rubric structure

    :param rubric_id:       Id of the rubric to update in the rubric structure
    :param rubric:          rubric to update
    :return:                updated rubric structure
    """
    # Get the requested rubric from the db into session
    update_rubric = Rubric.query.filter(
        Rubric.rubric_id == rubric_id
    ).one_or_none()

    # Did we find an existing rubric?
    if update_rubric is not None:

        # turn the passed in rubric into a db object
        schema = RubricSchema()
        update = schema.load(rubric, session=db.session).data

        # Set the id to the rubric we want to update
        update.rubric_id = update_rubric.rubric_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated rubric in the response
        data = schema.dump(update_rubric).data

        return data, 200

    # Otherwise, nope, didn't find that rubric
    else:
        abort(404, f"Rubric not found for Id: {rubric_id}")


@login_required
def delete(rubric_id):
    """
    This function deletes a rubric from the rubric structure

    :param rubric_id:   Id of the rubric to delete
    :return:            200 on successful delete, 404 if not found
    """

    # Get the rubric requested
    rubric = Rubric.query.filter(Rubric.rubric_id == rubric_id).one_or_none()

    # Did we find a rubric?
    if rubric is not None:
        db.session.delete()
        db.session.commit()
        return make_response(f"Rubric {rubric_id} deleted", 200)

    # Otherwise, nope, didn't find that rubric
    else:
        abort(404, f"Rubric not found for Id: {rubric_id}")
