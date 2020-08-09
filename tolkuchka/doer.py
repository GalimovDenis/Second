from flask import make_response, abort

from config import db
from tolkuchka.models import Doer, DoerSchema, Ad


def read_all():
    """
    This function responds to a request for /api/doers
    with the complete lists of doers

    :return:    Json string of list of doers
    """
    # Create the list of people from our data
    doers = Doer.query.order_by(Doer.doer_phone).all()

    # Serialize the data  for the response
    doer_schema = DoerSchema(many=True)
    data = doer_schema.dump(doers)
    return data


def read_one(doer_id):
    """
    This function responds to a request for /api/users/{user_id}
    with one matching doer from users

    :param doer_id: Id of doer to find
    :return:        User matching id
    """

    # Build the initial query
    doer = (
        Doer.query.filter(Doer.doer_id == doer_id)
        .outerjoin(Ad)
        .one_or_none()
    )

    # Did we find a doer?
    if doer is not None:

        # Serialize the data for the response
        doer_schema = DoerSchema()
        data = doer_schema.dump(doer)
        return data

    # otherwise, nope, didn't find that doer
    else:
        abort(404, f"User not found for Id: {doer_id}")


def create(doer):
    """
    This function creates a new user in the users structure
    based on the passed in user data

    :param doer:    user to create in users structure
    :return:        201 on success, 4406 on person exists
    """
    doer_phone = doer.get("doer_phone")

    existing_doer = (
        Doer.query.filter(Doer.doer_phone == doer_phone)
        .one_or_none()
    )

    # Can we insert this user?
    if existing_doer is None:

        # Create a person instance using the schema and thee passed in user
        schema = DoerSchema()
        new_doer = schema.load(doer, session=db.session).data

        # Add the user to the database
        db.session.add(new_doer)
        db.session.commit()

        # Serialize and return the newly created user in the response
        data = schema.dump(new_doer).data

        return data, 201

    # Otherwise, nope, user exist already
    else:
        abort(409, f"Doer {doer_phone} exists already")


def update(doer_id, doer):
    """
    This function updates an existing user in the users structure

    :param doer_id:     Id of the user to update in the users structure
    :param doer:        user to update
    :return:            updated user structure
    """

    # Get the user request from the db into session
    update_doer = Doer.query.filter(Doer.doer_id == doer_id).one_or_none()

    # Did we find an existing user?
    if update_doer is not None:

        # turn the passed in user into a db object
        schema = DoerSchema()
        update = schema.load(doer, session=db.session).data

        # Set the id to the person we want to update
        update.doer_id = update_doer.doer_id

        # Merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # Return updated user in the response
        data = schema.dump(update_doer).data

        return data, 200

    # otherwise, nope, didn't find that person
    else:
        abort(404, f"Doer not found for Id: {doer_id}")


def delete(doer_id):
    """
    This function deletes the doer from the users structure

    :param doer_id:     Id of the doer to delete
    :return:            200 on successful delete, 404 if not found
    """

    # Get the person request
    doer = Doer.query.filter(Doer.doer_id == doer_id).one_or_none()

    # Did we find the doer?
    if doer is not None:
        db.session.delete(doer)
        db.session.commit()
        return make_response(f"Doer {doer_id} deleted", 200)

    # Otherwise, nope, didn't find that doer
    else:
        abort(404, f"Doer not found for Id: {doer_id}")
