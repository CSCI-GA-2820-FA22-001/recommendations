"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.models import Recommendation, RecommendationType
from .common import status  # HTTP Status Codes

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendations REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for(
        "get_recommendations",
        recommendation_id=recommendation.id, _external=True)

    app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# LIST ALL recommendations
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for Recommendations list")
    recs = []
    name = request.args.get("name")
    type_string = request.args.get("type")
    if name:
        app.logger.info("Filtering recommendations by name=%s", name)
        recs = Recommendation.find_by_name(name)
    elif type_string:
        app.logger.info("Filtering recommendations by type=%s", type_string)
        recommendation_type = RecommendationType[type_string]
        recs = Recommendation.find_by_type(recommendation_type)
    else:
        recs = Recommendation.all()

    results = [rec.serialize() for rec in recs]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  READ RECOMMENDATIONS
######################################################################

@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendations(recommendation_id):
    """
    Retrieve a single recommendation
    This endpoint will return a recommendations based on it's id
    """
    app.logger.info("Request for recommendations with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
                status.HTTP_404_NOT_FOUND,
                f"recommendations with id '{recommendation_id}' was not found.")
    app.logger.info("Returning recommendation: %s", recommendation.recommendation_name)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to update recommendation with id: %s", recommendation_id)
    check_content_type("application/json")
    recommendation = Recommendation.find(recommendation_id)
    if recommendation is None:
        abort(status.HTTP_404_NOT_FOUND, f"Recommendation id {recommendation_id} does not exist")
    recommendation.deserialize(request.get_json())
    recommendation.update()
    message = recommendation.serialize()
    app.logger.info("Recommendation with ID [%s] updated.", recommendation_id)
    location_url = url_for(
                            "get_recommendations",
                            recommendation_id=recommendation.id, _external=True)
    return jsonify(message), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendation(recommendation_id):
    """
    Delete a Recommendation
    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if recommendation:
        recommendation.delete()

    app.logger.info("Recommendation with ID [%s] delete complete.", recommendation_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK
