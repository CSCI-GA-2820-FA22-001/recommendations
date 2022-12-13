import requests
from behave import given
from compare import expect


@given('the following recommendations')
def step_impl(context):
    """ Delete all Recommendations and load new ones """
    # List all of the recommendations and delete them one by one
    rest_endpoint = context.BASE_URL + '/api/recommendations'
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for recommendation in context.resp.json():
        context.resp = requests.delete(rest_endpoint + '/' + str(recommendation['id']))
        expect(context.resp.status_code).to_equal(204)
    # load the database with the new recommendations
    for row in context.table:
        payload = {
            "name": row['name'],
            "product_id": row['product_id'],
            "recommendation_id": row['recommendation_id'],
            "recommendation_name": row['recommendation_name'],
            "type": row['type'],
            "number_of_likes": row['number_of_likes']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
