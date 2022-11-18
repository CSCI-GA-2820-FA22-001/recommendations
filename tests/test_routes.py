"""
Recommendations API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from service import app
from service.models import db, init_db, Recommendation
from service.common import status  # HTTP Status Codes
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=R0904
class TestRecommendationServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _create_recommendation(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test recommendation"
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        logging.debug("Response: %s", new_recommendation)
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(new_recommendation["recommendation_id"], test_recommendation.recommendation_id)
        self.assertEqual(new_recommendation["recommendation_name"], test_recommendation.recommendation_name)
        self.assertEqual(new_recommendation["type"], test_recommendation.type.name)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["name"], test_recommendation.name)
        self.assertEqual(new_recommendation["recommendation_id"], test_recommendation.recommendation_id)
        self.assertEqual(new_recommendation["recommendation_name"], test_recommendation.recommendation_name)
        self.assertEqual(new_recommendation["type"], test_recommendation.type.name)

    def test_update_recommendation(self):
        """Updating a recommendation should work"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        new_recommendation["name"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update_recommendation = response.get_json()
        self.assertEqual(update_recommendation["name"], "unknown")

    def test_like_dislike_recommendation(self):
        """Liking and Unliking a recommendation should work"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update_recommendation = response.get_json()
        self.assertEqual(update_recommendation["number_of_likes"], 1)
        response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}/dislike")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update_recommendation = response.get_json()
        self.assertEqual(update_recommendation["number_of_likes"], 0)

    def test_get_rec_list(self):
        """It should Get a list of Recommendations"""
        self._create_recommendation(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_recommendations(self):
        """It should Get a single recommendations"""
        # get the id of a recommendations
        test_recommendations = self._create_recommendation(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendations.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_recommendations.name)

    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendation(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_rec_list_by_name(self):
        """It should Query Recommendations by name"""
        recs = self._create_recommendation(10)
        test_name = recs[0].name
        print(test_name)
        name_recs = [rec for rec in recs if rec.name == test_name]
        response = self.client.get(
            BASE_URL,
            query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_recs))
        # check the data just to be sure
        for rec in data:
            self.assertEqual(rec["name"], test_name)

    def test_query_rec_list_by_type(self):
        """It should Query Recommendations by type"""
        recs = self._create_recommendation(10)
        test_type = recs[0].type
        print(test_type)
        type_recs = [rec for rec in recs if rec.type == test_type]
        response = self.client.get(
            BASE_URL,
            query_string=f"type={quote_plus(test_type.name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(type_recs))
        # check the data just to be sure
        for rec in data:
            self.assertEqual(rec["type"], test_type.name)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_rec_no_data(self):
        """It should not Create a rec with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rec_no_content_type(self):
        """It should not Create a rec with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_rec_bad_content_type(self):
        """It should not Create a rec with bad content type"""
        response = self.client.post(BASE_URL, headers={'Content-Type': 'application/xml'})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_rec_not_found(self):
        """It should not Get a recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_update_recommendation_no_correct_id(self):
        """It should not get a recommendation that does not exist"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        response = self.client.put(f"{BASE_URL}/{12}", json=new_recommendation)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dislike_recommendation(self):
        """Unliking a recommendation with 0 likes shouldn't work"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        response = self.client.put(f"{BASE_URL}/{new_recommendation['id']}/dislike")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_dislike_recommendation_no_correct_id(self):
        """It should not glike/dislike a recommendation that does not exist"""
        response = self.client.put(f"{BASE_URL}/{0}/like")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.put(f"{BASE_URL}/{0}/dislike")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")
