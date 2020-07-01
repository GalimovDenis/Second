from flask import make_response, abort
from config import db
from models import User, UserSchema, Ad


def read_all():
    """
    This function responds to a request for /api/users
    with the complete lists of users

    :return:    Json string of list of users
    """
    # Create the list of people from our data
    users = User.query.order_by(User.user_phone).all()

    # Serialize the data  for the response
    user_schema = UserSchema(many=True)
    data = user_schema.dump(users)
    return data


def read_one(user_id):
    """
    This function responds to a request for /api/users/{user_id}
    with one matching user from users

    :param user_id: Id of user to find
    :return:        User matching id
    """

    # Build the initial query
    user = (
        User.query.filter(User.user_id == user_id)
        .outerjoin(Ad)
        .one_or_none()
    )

    # Did we find a user?
    if user is not None:

        # Serialize the data for the response
        user_schema = UserSchema()
        data = user_schema.dump(user)
        return data

    # otherwise, nope, didn't find that user
    else:
        abort(404, f"User not found for Id: {user_id}")


def create(user):
    """
    This function creates a new user in the users structure
    based on the passed in user data

    :param user:    user to create in users structure
    :return:        201 on success, 4406 on person exists
    """
    user_phone = user.get("user_phone")

    existing_user = (
        User.query.filter(User.user_phone == user_phone)
        .one_or_none()
    )

    # Can we insert this user?
    if existing_user is None:

        # Create a person instance using the schema and thee passed in user
        schema = UserSchema()
        new_user = schema.load(user, session=db.session).data

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Serialize and return the newly created user in the response
        data = schema.dump(new_user).data

        return data, 201

    # Otherwise, nope, user exist already
    else:
        abort(409, f"User {user_phone} exists already")


def update(user_id, user):
    """
    This function updates an existing user in the users structure

    :param user_id:     Id of the user to update in the users structure
    :param user:        user to update
    :return:            updated user structure
    """

    # Get the user request from the db into session
    update_user = User.query.filter(User.user_id == user_id).one_or_none()

    # Did we find an existing user?
    if update_user is not None:

        # turn the passed in user into a db object
        schema = UserSchema()
        update = schema.load(user, session=db.session).data

        # Set the id to the person we want to update
        update.user_id = update_user.user_id

        # Merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # Return updated user in the response
        data = schema.dump(update_user).data

        return data, 200

    # otherwise, nope, didn't find that person
    else:
        abort(404, f"User not found for Id: {user_id}")


def delete(user_id):
    """
    This function deletes the user from the users structure

    :param user_id:     Id of the user to delete
    :return:            200 on successful delete, 404 if not found
    """

    # Get the person request
    user = User.query.filter(User.user_id == user_id).one_or_none()

    # Did we find the user?
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return make_response(f"User {user_id} deleted", 200)

    # Otherwise, nope, didn't find that user
    else:
        abort(404, f"User not found for Id: {user_id}")
