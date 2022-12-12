"""
My Service

Describe what your service does here
"""

from flask import jsonify, request
from flask_restx import api, Resource, fields, reqparse
from service.models import Recommendation, RecommendationType
from .common import status  # HTTP Status Codes


# Import Flask application
from . import app, api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


create_model = api.model(
    'Recommendation',
    {
        'name': fields.String(required=True, 
                                            description='The name of the recommendation'), 
        'recommendation_id': fields.Integer(required=True, 
                                            description='The id of the recommended product'), 
        'recommendation_name': fields.String(required=True, 
                                            description='The name of the recommended product'), 
        'number_of_likes': fields.Integer(required=False, 
                                            description='The number of likes of the recommendation'), 
        'type': fields.String(enum=RecommendationType._member_names_,
                                            description='The type of the recommendation'), 
    }
)

recommendation_model = api.inherit(
    'RecommendationModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    }
)

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    'id', type=int, location='args',required=False, help='List recommendations by id')
recommendation_args.add_argument(
    'name', type=str,location='args',required=False, help='List recommendations by name')
recommendation_args.add_argument(
    'type', type=int, location='args',required=False, help='List recommendations by type')
recommendation_args.add_argument(
    'number_of_likes', type=int, required=False, help='List recommendations by number_of_likes')
recommendation_args.add_argument(
    'recommendation_id', type=int, required=False, help='List recommendations by recommendation_id')
recommendation_args.add_argument(
    'recommendation_name', type=str, required=False, help='List recommendations by recommendation_name')

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/{recommendation_id}
######################################################################

@api.route('/recommendations/<int:recommendation_id>', strict_slashes=False)
@api.param('recommendation_id',"The recommendation id")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single recommendation
    GET /recommendation{id} - Returns a Pet with the id
    PUT /recommendation{id} - Update a Pet with the id
    DELETE /recommendation{id} -  Deletes a Pet with the id
    """
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
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
        return recommendation.serialize(), status.HTTP_200_OK

    @api.doc('update_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted data was not valid')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a recommendation

        This endpoint will update a recommendation based the body that is posted
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
        location_url = api.url_for(
                                RecommendationResource,
                                recommendation_id=recommendation.id, _external=True)
        return message, status.HTTP_200_OK, {"Location": location_url}

    @api.doc('delete_recommendations')
    @api.response(204, 'Recommendation deleted')
    def delete(self, recommendation_id):
        """
        Delete a recommendation

        This endpoint will delete a recommendation based the id specified in the path
        """
        app.logger.info(
        "Request to delete recommendation with id: %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if recommendation:
            recommendation.delete()
        app.logger.info(
            "Recommendation with ID [%s] delete complete.", recommendation_id)
        return "", status.HTTP_204_NO_CONTENT


@api.route('/recommendations', strict_slashes=False)
@api.param('recommendation_id', "The recommendation id")
class RecommendationCollection(Resource):
    """
    RecommendationCollection class

    Allows the manipulation of all of your Recommendations
    GET /recommendations - Returns a list all of the Recommendations
    POST /recommendations - creates a new Recommendation record in the database
    """
    @api.doc('list_recommendations')
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
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
        app.logger.info(results)
        return results, status.HTTP_200_OK

    @api.doc('create_recommendations')
    @api.response(201, 'Recommendation created successfully')
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
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
        location_url = api.url_for(
            RecommendationResource,
            recommendation_id=recommendation.id, _external=True)
        app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}


@api.route('/recommendations/<int:recommendation_id>/like', strict_slashes=False)
@api.param('recommendation_id',"The recommendation id")
class RecommendationLikeResource(Resource):
    """
    RecommendationLikeResource class

    Allows the manipulation of a single recommendation
    PUT /recommendation{id}/like - Update a Pet with the id
    """
    @api.doc('like_recommendation')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a recommendation

        This endpoint will update a recommendation based the body that is posted
        """
        app.logger.info(
        "Request to like recommendation with id: %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if recommendation is None:
            abort(status.HTTP_404_NOT_FOUND,
                f"Recommendation id {recommendation_id} does not exist")
        recommendation.like()
        message = recommendation.serialize()
        app.logger.info("Recommendation with ID [%s] liked.", recommendation_id)
        location_url = api.url_for(RecommendationResource,
                            recommendation_id=recommendation.id, _external=True)
        return message, status.HTTP_200_OK, {"Location": location_url}

@api.route('/recommendations/<int:recommendation_id>/dislike', strict_slashes=False)
@api.param('recommendation_id',"The recommendation id")
class RecommendationDislikeResource(Resource):
    """
    RecommendationLikeResource class
    """
    @api.doc('dislike_recommendation')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a recommendation

        This endpoint will update a recommendation based the body that is posted
        """
        app.logger.info(
        "Request to dislike recommendation with id: %s", recommendation_id)
        recommendation = Recommendation.find(recommendation_id)
        if recommendation is None:
            abort(status.HTTP_404_NOT_FOUND,
                f"Recommendation id {recommendation_id} does not exist")
        recommendation.dislike()
        message = recommendation.serialize()
        app.logger.info("Recommendation with ID [%s] disliked.", recommendation_id)
        location_url = api.url_for(RecommendationResource,
                            recommendation_id=recommendation.id, _external=True)
        return message, status.HTTP_200_OK, {"Location": location_url}

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

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
