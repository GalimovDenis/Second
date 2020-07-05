from flask import make_response, abort
from config import db
from models import Ad, AdSchema, User, Rubric


def read_all():
    """
    This function responds to a request from /api/user/ads
    with the complete list of ads, sorted by ad date

    :return:       json list of all Ad for all users
    """
    ads = Ad.query.order_by(db.desc(Ad.ad_timestamp)).all()

    ad_schema = AdSchema(many=True)
    data = ad_schema.dump(ads)
    return data


def read_one(user_id, ad_id):
    """
    This function responds to a request for
    /api/user/{user_id}/ads/{ad_id}
    with one matching ad for the associated user

    :param user_id:     Id of user the ad is related to
    :param ad_id:       Id of the ad
    :return:            json string of ad contents
    """
    ad = (
        Ad.query.join(User, User.user_id == Ad.ad_owner)
        .filter(User.user_id == user_id)
        .filter(Ad.ad_id == ad_id)
        .one_or_none()
    )

    if ad is not None:
        ad_schema = AdSchema()
        data = ad_schema.dump(ad).data
        return data

    else:
        abort(404, f"Ad not found for Id: {ad_id}")


def create(user_id, rubric_id, ad):
    """
    This function creates a new ad in the rubric related to the passed in user id

    :param user_id:     Id of the user the ad is related to
    :param ad:          The JSON containing the ad data
    :param rubric_id:   Id of the rubric the ad is related to
    :return:            data and 201 on success
    """

    # Get the parent user
    user = User.query.filter(User.user_id == user_id).one_or_none()

    # Was a user found?
    if user is None:
        abort(404, f"User not found for Id: {user_id}")

    # Get the related rubric
    rubric = Rubric.query.filter(Rubric.rubric_id == rubric_id).one_or_none()

    # Was a rubric found?
    if rubric is None:
        abort(404, f"Rubric not found for Id: {rubric_id}")

    # Create a ad schema instance
    schema = AdSchema()
    new_ad = schema.load(ad, session=db.session).data

    # Add the ad to the user, rubric and database
    user.ads.append(new_ad)
    rubric.ads.append(new_ad)
    db.session.commit()

    # Serialize and return the newly created ad in the response
    data = schema.dump(new_ad).data

    return data, 201


def update(user_id, rubric_id, ad_id, ad):
    """
    This function updates an existing ad related to the passed in user id and rubric id

    :param user_id:     Id of the user the ad is related to
    :param rubric_id:   Id of the rubric the ad is related to
    :param ad_id:       Id of the ad to update
    :param ad:          The JSON containing the ad data
    :return:            200 on success
    """
    update_ad = (
        Ad.query.filter(User.user_id == user_id)
        .filter(Rubric.rubric_id == rubric_id)
        .filter(Ad.ad_id == ad_id)
        .one_or_none()
    )

    # Did we find an existing ad?
    if update_ad is not None:

        # turn the passed in ad into a db object
        schema = AdSchema()
        update = schema.load(ad, session=db.session).data

        # Set the id's to the ad we want to update
        update.user_id = update_ad.user_id
        update.ad_id = update_ad.ad_id
        update.rubric_id = update_ad.rubric_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated ad in the response
        data = schema.dump(update_ad).data

        return data, 200

    else:
        abort(404, f"Ad not found for Id: {ad_id}")


def delete(user_id, rubric_id, ad_id):
    """
    This function deletes a ad from the ad structure

    :param rubric_id:   Id of the rubric the ad is related to
    :param user_id:     Id of the user the ad is related to
    :param ad_id:       Id of the ad to delete
    :return:            200 on successful delete, 404 if not found
    """

    # Get the ad request
    ad = (
        Ad.query.filter(User.user_id == user_id)
        .filter(Ad.ad_id == ad_id)
        .filter(Rubric.rubric_id == rubric_id)
        .one_or_none()
    )

    # Did we find a ad?
    if ad is not None:
        db.session.delete(ad)
        db.session.commit()
        return make_response(
            "Ad {note_id} deleted".format(ad_id=ad_id), 200
        )

    # Otherwise, nope, didn't find that ad
    else:
        abort(404, f"Ad not found for Id: {ad_id}")
