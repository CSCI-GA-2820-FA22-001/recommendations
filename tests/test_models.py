"""
Test cases for Recommendations Model

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Recommendation, RecommendationType, DataValidationError, db
from service import app
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Recommendations   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name


class TestRecommendationModel(unittest.TestCase):
    """ Test Cases for Recommendation Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_recommendation(self):
        """It should Create a Recommendation and assert that it exists"""
        recommendation = Recommendation(
                                        name="prodA", recommendation_id=2,
                                        recommendation_name="prodB",
                                        type=RecommendationType.CROSSSELL,
                                        number_of_likes=2)
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.name, "prodA")
        self.assertEqual(recommendation.recommendation_id, 2)
        self.assertEqual(recommendation.recommendation_name, "prodB")
        self.assertEqual(recommendation.type, RecommendationType.CROSSSELL)
        self.assertEqual(recommendation.number_of_likes, 2)

    def test_add_a_recommendation(self):
        """It should Create a recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(
                                        name="prodA", recommendation_id=2,
                                        recommendation_name="prodB",
                                        type=RecommendationType.CROSSSELL,
                                        number_of_likes=2)
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_read_a_recommendation(self):
        """It should Read a recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None  
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        # Fetch it back
        found_recommendation = Recommendation.find(recommendation.id)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(found_recommendation.name, recommendation.name)
        self.assertEqual(found_recommendation.recommendation_id, recommendation.recommendation_id)

    def test_update_a_recommendation(self):
        """It should Update a recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None  # pylint: disable=invalid-name
        recommendation.create()
        logging.debug(recommendation)
        self.assertIsNotNone(recommendation.id)
        # Change it an save it
        recommendation.number_of_likes = 10
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.number_of_likes, 10)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].number_of_likes, 10)

    def test_update_no_id(self):
        """It should not Update a recommendation with no id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_like_and_dislike_no_id(self):
        """It should not LIke or dislike a recommendation with no id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.like)
        self.assertRaises(DataValidationError, recommendation.dislike)

    def test_like_and_dislike_rec(self):
        """It should increment the number_of_likes"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        recommendation.like()
        self.assertEqual(recommendation.number_of_likes, 1)
        recommendation.dislike()
        self.assertEqual(recommendation.number_of_likes, 0)

    def test_dislike_at_zero(self):
        """It should not dislike a recommendation that is at 0 likes"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        self.assertRaises(DataValidationError, recommendation.dislike)

    def test_delete_a_recommendation(self):
        """It should Delete a recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(recommendation.all()), 0)

    def test_list_all_recommendations(self):
        """It should List all recommendations in the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        # Create 5 recommendations
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        # See if we get back 5 recommendations
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 5)

    def test_serialize_a_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], recommendation.name)
        self.assertIn("recommendation_id", data)
        self.assertEqual(data["recommendation_id"], recommendation.recommendation_id)
        self.assertIn("recommendation_name", data)
        self.assertEqual(data["recommendation_name"], recommendation.recommendation_name)
        self.assertIn("type", data)
        self.assertEqual(data["type"], recommendation.type.name)
        self.assertIn("number_of_likes", data)
        self.assertEqual(data["number_of_likes"], recommendation.number_of_likes)

    def test_deserialize_a_recommendation(self):
        """It should de-serialize a recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.name, data["name"])
        self.assertEqual(recommendation.recommendation_id, data["recommendation_id"])
        self.assertEqual(recommendation.recommendation_name, data["recommendation_name"])
        self.assertEqual(recommendation.type.name, data["type"])
        self.assertEqual(recommendation.number_of_likes, data["number_of_likes"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a recommendation with missing data"""
        data = {"id": 1, "name": "prodA", "number_of_likes": 3}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_type(self):
        """It should not deserialize a bad type attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["type"] = "sell"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_find_recommendation(self):
        """It should Find a recommendation by ID"""
        recommendations = RecommendationFactory.create_batch(5)
        for recommendation in recommendations:
            recommendation.create()
        logging.debug(recommendations)
        # make sure they got saved
        self.assertEqual(len(Recommendation.all()), 5)
        # find the 2nd recommendation in the list
        recommendation = Recommendation.find(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(recommendation.name, recommendations[1].name)
        self.assertEqual(recommendation.recommendation_id, recommendations[1].recommendation_id)
        self.assertEqual(recommendation.recommendation_name, recommendations[1].recommendation_name)
        self.assertEqual(recommendation.type, recommendations[1].type)
        self.assertEqual(recommendation.number_of_likes, recommendations[1].number_of_likes)

    def test_find_by_type(self):
        """It should Find recommendations by type"""
        recommendations = RecommendationFactory.create_batch(10)
        for recommendation in recommendations:
            recommendation.create()
        recommendation_type = recommendations[0].type
        count = len([recommendation for recommendation in recommendations if recommendation.type == recommendation_type])
        found = Recommendation.find_by_type(recommendation_type)
        self.assertEqual(found.count(), count)
        for recommendation in found:
            self.assertEqual(recommendation.type, recommendation_type)

    def test_find_by_name(self):
        """It should Find a recommendation by Name"""
        recommendations = RecommendationFactory.create_batch(5)
        for recommendation in recommendations:
            recommendation.create()
        name = recommendations[0].name
        found = Recommendation.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].id, recommendations[0].id)
        self.assertEqual(found[0].name, recommendations[0].name)
        self.assertEqual(found[0].recommendation_id, recommendations[0].recommendation_id)
        self.assertEqual(found[0].recommendation_name, recommendations[0].recommendation_name)
        self.assertEqual(found[0].type, recommendations[0].type)
        self.assertEqual(found[0].number_of_likes, recommendations[0].number_of_likes)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        recommendations = RecommendationFactory.create_batch(3)
        for recommendation in recommendations:
            recommendation.create()

        recommendation = Recommendation.find_or_404(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(recommendation.name, recommendations[1].name)
        self.assertEqual(recommendation.recommendation_id, recommendations[1].recommendation_id)
        self.assertEqual(recommendation.recommendation_name, recommendations[1].recommendation_name)
        self.assertEqual(recommendation.type, recommendations[1].type)
        self.assertEqual(recommendation.number_of_likes, recommendations[1].number_of_likes)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Recommendation.find_or_404, 0)
