# __author__: Litong "Leighton" Dong
# continuing personal projects
# involving RESTful API, PostgreSQL database, machine learning and statistics

# import packages
from flask import Flask, request
import psycopg2
import json
import numpy as np
from sklearn import linear_model
from sklearn.preprocessing import Imputer


# create Flask instance
# since there is only one API in this package
# using "__name__" is fine
# if in the future, there are more applications
# location must be defined
# app = Flask('yourapplication')
# app = Flask(__name__.split('.')[0])
app = Flask(__name__)


# Phase 1
# Basic statistics of star ratings
# must have city as a parameter
# can have attribute as parameter

# define url route and possible request methods
@app.route('/yelp/starstats/<mycity>', methods=['GET'])
# define function
def starstats(mycity):
    """starstats a function, computing mean and standard deviation of star
    ratings

    Args:
        mycity (string): the city user given
    
    Returns:
        body (json or string): a json file containing basic statistics or
                                a string says error

    """

    # if there is a attribute parameter
    if 'attribute_key' in request.args:
        # extract the key and value of the URL parameter
        # user-defined "attribute" feature of yelp data
        attribute_key = request.args['attribute_key']
        attribute_value = request.args['attribute_value']
        attribute = attribute_key + ' = ' + attribute_value

        # construct sql query for PostgreSQL database
        sql = 'select stars from yelp where attributes #>> ' + attribute_key +\
            ' = ' + attribute_value + " and city = '" + mycity + "';"

    # if there is no attribute parameter
    else:
        # construct sql query for PostgreSQL database
        sql = "select stars from yelp where city = '" + mycity + "';"
        attribute = 'Not Specified'

    # define web request method
    if request.method == 'GET':

        # PostgreSQL database parameters
        dsn = 'host=localhost dbname=yelp'
        # PostgreSQL database connection
        conn = psycopg2.connect(dsn)
        # PostgreSQL database execution cursor
        cur = conn.cursor()

        # display sql query on server
        print 'Querying: ', sql
        # try execute sql query
        try:
            cur.execute(sql)
        # except errors
        except psycopg2.Error as e:
            # construct error output
            out = {'error_code': e.pgcode, 'error_msg': e.pgerror}
            body = json.dumps(out)
            # return error
            return body + '\n'

        # obtain rows of the return table
        rows = cur.fetchall()
        # declare empty list to store star ratings
        star_list = []

        # go through each row in the return table from PostgreSQL
        for row in rows:
            # append all the star ratings to the list
            star_list.append(float(row[0]))

        # PostgreSQL databse connection commit and close
        conn.commit()
        cur.close()
        conn.close()

        # find the mean and standard deviation of the star rating list
        # if list is not empty
        if star_list:
            # round number to two significant digits
            avg = round(np.mean(star_list), 2)
            std = round(np.std(star_list), 2)
        else:
            avg = 'NA'
            std = 'NA'

        # construct output json file
        out = {'city': mycity, 'attribute': attribute, 'avg_stars': avg,
               'std_stars': std}
        body = json.dumps(out)

    # if request method is not GET, output error
    else:
        body = 'error'
    # return
    return body + '\n'


# Phase 2
# variables retrieval from the database
# must have variable as a parameter
# can have json variable as parameter

# define route and possible request methods
@app.route('/yelp/variables/<variable>', methods=['GET'])
# define function
def get_variables(variable):
    """get_variables a function, retrieving all labels of a variable

    Args:
        variable (string): the variable user given
    
    Returns:
        body (json or string): a json file containing a list of strings or
                                a string says error

    """
    # define a dictionary describing the type of each variable in the database
    # whether it is a json document or a standard relational database type
    variable_type_dic = {'attributes': 'json', 'city': 'standard'}

    # when the input variable has json type in the database
    if variable_type_dic[variable] == 'json':

        # if there is an attribute parameter
        # which is a string of variable/variables
        # and it does not contain the final layer
        # it will return all possible keys of the next layer
        if 'attribute' in request.args:
            # construc sql query for PostgreSQL database
            sql = 'select distinct json_object_keys(col1) from (select json_' \
                'extract_path(' + variable + ', ' + request.args['attribute'] \
                + ') col1 from yelp) as foo;'
        # if there is a full attribute parameter
        # which is a string of variable/variables
        # it will return all possible values of the full key
        elif 'attribute_key' in request.args:
            # construc sql query for PostgreSQL database
            sql = 'select distinct col1 from (select json_extract_path_text(' \
                + variable + ', ' + request.args['attribute_key'] + ') col1 ' \
                'from yelp) as foo;'
        # if there is no attribute parameter
        else:
            # construct sql query for PostgreSQL database
            sql = 'select distinct json_object_keys(' + variable + ') from '  \
                'yelp;'
    else:
        # construct sql query for PostgreSQL database
        sql = 'select distinct ' + variable + ' from yelp;'

    # define web request method
    if request.method == 'GET':

        # PostgreSQL database parameters
        dsn = 'host=localhost dbname=yelp'
        # PostgreSQL database connection
        conn = psycopg2.connect(dsn)
        # PostgreSQL database execution cursor
        cur = conn.cursor()

        # display sql query on server
        print 'Querying: ', sql
        # try execute sql query
        try:
            cur.execute(sql)
        # except errors
        except psycopg2.Error as e:
            # construct error output
            out = {'error_code': e.pgcode, 'error_msg': e.pgerror}
            body = json.dumps(out)
            # return error
            return body + '\n'
        
        # obtain rows of the return table
        rows = cur.fetchall()
        # declare an empty list to store variables
        distinct_variables = []

        # go through each row in the return table from PostgreSQL
        for row in rows:
            # append all the variables to the list
            distinct_variables.append(row[0])

        # PostgreSQL database connection commit and close
        conn.commit()
        cur.close()
        conn.close()

        # construct output json file
        out = {variable: distinct_variables}
        body = json.dumps(out)

    # if request method is not GET, output error
    else:
        body = 'error'
    # return
    return body + '\n'


# Phase 3 (ongoing phase)
# Basic machine learning on star ratings, number of reviews and price range
# using linear regression
# must have city as parameter
# can have attribute as parameter

# define url route and possible request methods
@app.route('/yelp/linear_regression/<mycity>', methods=['GET', 'POST'])
# define function
def linear_regression(mycity):
    """starstats a function, computing mean and standard deviation of star
    ratings

    Args:
        mycity (string): the city user given
    
    Returns:
        body (json or string): a json file containing basic statistics or
                                a string says error

    """

    target = 'stars'
    features = "review_count, attributes#>>'{Price Range}'"

    # if there is a attribute parameter
    if 'attribute_key' in request.args:
        # extract the key and value of the URL parameter
        # user-defined "attribute" feature of yelp data)
        attribute_key = request.args['attribute_key']
        attribute_value = request.args['attribute_value']

        # construct sql query for PostgreSQL database
        sql = 'select ' + target + ' , ' + features + ' from yelp where '     \
            'attributes #>> ' + attribute_key + ' = ' + attribute_value +     \
            " and city = '" + mycity + "';"
        attribute = attribute_key + ' = ' + attribute_value

    # if there is no attribute parameter
    else:
        # construc sql query for PostgreSQL database
        sql = 'select ' + target + ', ' + features + ' from yelp where city '\
            "= '" + mycity + "';"
        attribute = 'Not Specified'

    # PostgreSQL database parameters
    dsn = 'host=localhost dbname=yelp'
    # PostgreSQL database connection
    conn = psycopg2.connect(dsn)
    # PostgreSQL database execution cursor
    cur = conn.cursor()

    print 'Querying: ', sql
    # try execute sql query
    try:
        cur.execute(sql)
    # except errors
    except psycopg2.Error as e:
        out = {'error_code': e.pgcode, 'error_msg': e.pgerror}
        body = json.dumps(out)

        return body + '\n'

    rows = cur.fetchall()

    y = []
    X = []

    # go through each row in the return table from PostgreSQL
    for row in rows:
        # create target and feature arrays
        y.append(float(row[0]))
        row_array = [int(row[1]), int(row[2]) if row[2] is not None else 'NaN']
        X.append(row_array)

    # PostgreSQL databse connection commit and close
    conn.commit()
    cur.close()
    conn.close()

    # define web request method
    if request.method == 'GET':
        if X:
            imp = Imputer(missing_values='NaN', strategy='median', axis=0)
            X = imp.fit_transform(X)

            # Create linear regression object
            regr = linear_model.LinearRegression()

            # Train the model using the training sets
            regr.fit(X, y)

            # The coefficients
            num_review_coef = round(regr.coef_[0], 5)
            price_range_coef = round(regr.coef_[1], 5)
            MSE = round(sum((regr.predict(X)-np.array(y))**2), 3)
            R_sqr = round(regr.score(X, y), 6)
            intersept = round(regr.intercept_, 5)

            equation = 'stars = ' + str(intersept) + ' + (' +                 \
                str(num_review_coef) + ') * review count + (' +               \
                str(price_range_coef) + ') * price range'

            # construct output json file
            out = {'city': mycity, 'attribute': attribute,
                   'equation': equation, 'mean square error': MSE,
                   'R-square': R_sqr}
            body = json.dumps(out)

        else:
            # construct output json file
            out = {'city': mycity, 'attribute': attribute, 'equation': 'NA',
                   'mean square error': 'NA', 'R-square': 'NA'}
            body = json.dumps(out)

    elif request.method == 'POST':
        test_data = request.data
        print type(test_data)
        print test_data

       # if X:
       #      imp = Imputer(missing_values='NaN', strategy='median', axis=0)
       #      X = imp.fit_transform(X)

       #      # Create linear regression object
       #      regr = linear_model.LinearRegression()

       #      # Train the model using the training sets
       #      regr.fit(X, y)

       #      prediction = regr.predict(test_data)
       #      # construct output json file
       #      out = {'city': mycity, 'attribute': attribute, 'prediction': prediction}
       #      body = json.dumps(out)
        
       #  else:
       #      # construct output json file
       #      out = {'city': mycity, 'attribute': attribute, 'prediction': 'NA'}
       #      body = json.dumps(out)

        body = 'post'

    else:
        body = 'error'

    return body + '\n'



if __name__ == '__main__':
    app.debug = True
    app.run()



