"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.models import Recommendation, RecommendationType
from .common import status  # HTTP Status Codes
from flask_restx import Api, Resource, fields, reqparse, inputs

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")

# Define the model so that the docs reflect what can be sent
api = Api(app, 
        version='1.0.0', 
        title='Recommendation REST API Service',
        description='This is a Recommendation server.',
        default='recommendations',
        default_label='Recommendation operations',
        doc='/apidocs',
        prefix='/api'
        )

create_model = api.model(
    'Recommendation',
    {
        'recommendation_name': fields.String(required=True,
            description='The name of the recommendation'),
        'recommendation_type': fields.String(required=True,
            description='The type of the recommendation'),
        'recommendation_description': fields.String(required=True,
            description='The description of the recommendation'),
        'recommendation_url': fields.String(required=True,
            description='The url of the recommendation'),
        'recommendation_image_url': fields.String(required=True,
            description='The image url of the recommendation')
    }
)

Recommendation_model = api.inherit(
    'Recommendation',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
            description='The unique id assigned internally by service'),
    }
)

#query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument('id', type=int, required=False, help='List recommendations by id')
recommendation_args.add_argument('name', type=str, required=False, help='List recommendations by name')

######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route('/recommendations/<int:id>')
@api.param('id', 'The Recommendation identifier')
@api.response(404, 'Recommendation not found')
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendations{id} - Returns a Recommendation with the id
    PUT /recommendations{id} - Update a Recommendation with the id
    DELETE /recommendations{id} -  Deletes a Recommendation with the id
    """
    
    #------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.marshal_with(Recommendation_model)
    def get(self, id):
        """
        Retrieve a single Recommendation

        This endpoint will return a Recommendation based on it's id
        """
        app.logger.info("Request for recommendation with id: %s", id)
        recommendation = Recommendation.find(id)
        if not recommendation:
            api.abort(status.HTTP_404_NOT_FOUND, f"Recommendation with id '{id}' was not found.")
        app.logger.info("Returning recommendation: %s", recommendation.recommendation_name)
        return recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('update_recommendations')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(Recommendation_model)
    @api.marshal_with(Recommendation_model, code=200)
    def put(self, id):
        """
        Update a Recommendation

        This endpoint will update a Recommendation based the body that is posted
        """
        app.logger.info("Request to update recommendation with id: %s", id)
        check_content_type("application/json")
        recommendation = Recommendation.find(id)
        if not recommendation:
            api.abort(status.HTTP_404_NOT_FOUND, f"Recommendation with id '{id}' was not found.")
        recommendation.deserialize(request.get_json())
        recommendation.id = id
        recommendation.save()
        app.logger.info("Recommendation with ID [%s] updated.", id)
        return recommendation.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    #------------------------------------------------------------------
    @api.doc('delete_recommendations')
    @api.response(204, 'Recommendation deleted')
    def delete(self, id):
        """
        Delete a Recommendation

        This endpoint will delete a Recommendation based the id specified in the path
        """
        app.logger.info("Request to delete recommendation with id: %s", id)
        recommendation = Recommendation.find(id)
        if recommendation:
            recommendation.delete()
        return '', status.HTTP_204_NO_CONTENT


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
# LIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def like_recommendation(recommendation_id):
    """
    Like a Recommendation
    This endpoint will increment a Recommendation like counter based the id specified in the path
    """
    app.logger.info("Request to like recommendation with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if recommendation is None:
        abort(status.HTTP_404_NOT_FOUND, f"Recommendation id {recommendation_id} does not exist")
    recommendation.like()
    message = recommendation.serialize()
    app.logger.info("Recommendation with ID [%s] liked.", recommendation_id)
    location_url = url_for("get_recommendations", recommendation_id=recommendation.id, _external=True)
    return jsonify(message), status.HTTP_200_OK, {"Location": location_url}


######################################################################
# DISLIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/dislike", methods=["PUT"])
def dislike_recommendation(recommendation_id):
    """
    Like a Recommendation
    This endpoint will decrement a Recommendation like counter based the id specified in the path
    """
    app.logger.info("Request to like recommendation with id: %s", recommendation_id)
    recommendation = Recommendation.find(recommendation_id)
    if recommendation is None:
        abort(status.HTTP_404_NOT_FOUND, f"Recommendation id {recommendation_id} does not exist")
    recommendation.dislike()
    message = recommendation.serialize()
    app.logger.info("Recommendation with ID [%s] liked.", recommendation_id)
    location_url = url_for("get_recommendations", recommendation_id=recommendation.id, _external=True)
    return jsonify(message), status.HTTP_200_OK, {"Location": location_url}


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


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK
