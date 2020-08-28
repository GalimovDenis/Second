from datetime import date, timedelta

from flask import make_response, abort
from flask_login import login_required

from config import db, DAYS_SHOW_AD
from models import Ad, AdSchema, Rubric


@login_required
def read_all(from_date=date.today()-timedelta(days=DAYS_SHOW_AD), issue=0):
    """
    Return all ad from db changing during time specified in app_var DAYS_SHOW_AD
     and count of issues more than 0 by default
    :param from_date: oldest date to show ad changed
    :param issue: count of issue of ad
    :return: json of ad in AdSchema format
    """
    ads = Ad.query.filter(Ad.ad_update >= from_date)\
                  .filter(Ad.ad_issue >= issue)\
                  .order_by(db.desc(Ad.ad_update)).all()

    ad_schema = AdSchema(many=True)
    data = ad_schema.dump(ads)
    return data


@login_required
def read_one(ad_id):
    """
    This function returns one ad or 404 if not found

    :param ad_id:       Id of the ad
    :return:            json string of ad contents
    """
    ad = Ad.query.filter(Ad.ad_id == ad_id).one_or_none()

    if ad is not None:
        ad_schema = AdSchema()
        data = ad_schema.dump(ad).data
        return data

    else:
        abort(404, f"Ad not found for Id: {ad_id}")


@login_required
def create(rubric_id, ad: Ad):
    """
    This function creates a new ad in the rubric related to the passed in ad_doers id

    :param ad:          The JSON containing the ad data
    :param rubric_id:   Id of the rubric the ad is related to
    :return:            data and 201 on success
    """

    # Get the related rubric
    rubric = Rubric.query.filter(Rubric.rubric_id == rubric_id).one_or_none()

    # Was a rubric found?
    if rubric is None:
        abort(404, f"Rubric not found for Id: {rubric_id}")

    # Create a ad schema instance
    schema = AdSchema()
    new_ad = schema.load(ad, session=db.session)

    # Add the ad to the ad_doers, rubric and database
    rubric.ads.append(new_ad)
    db.session.commit()

    # Serialize and return the newly created ad in the response
    data = schema.dump(new_ad).data

    return data, 201


@login_required
def update(rubric_id, ad_id, ad: Ad):
    """
    This function updates an existing ad related to the passed in user id and rubric id

    :param rubric_id:   Id of the rubric the ad is related to
    :param ad_id:       Id of the ad to update
    :param ad:          The JSON containing the ad data
    :return:            200 on success
    """
    update_ad = Ad.query.filter(Rubric.rubric_id == rubric_id).filter(Ad.ad_id == ad_id).one_or_none()

    # Did we find an existing ad?
    if update_ad is not None:

        # turn the passed in ad into a db object
        schema = AdSchema()
        update = schema.load(ad, session=db.session)

        # Set the id's to the ad we want to update
        update.doer_id = update_ad.doer_id
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


@login_required
def delete(ad_id):
    """
    This function deletes a ad from the ad structure

    :param ad_id:       Id of the ad to delete
    :return:            200 on successful delete, 404 if not found
    """

    # Get the ad request
    ad = Ad.query.filter(Ad.ad_id == ad_id).one_or_none()

    # Did we find a ad?
    if ad is not None:
        db.session.delete()
        db.session.commit()
        return make_response(
            "Ad {ad_id} deleted".format(ad_id=ad_id), 200
        )

    # Otherwise, nope, didn't find that ad
    else:
        abort(404, f"Ad not found for Id: {ad_id}")
