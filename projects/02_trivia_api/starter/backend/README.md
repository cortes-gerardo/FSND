# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Local Development
#### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

#### Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

### Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference
### Getting Started
#### Base URL
This project is intended to be run locally on `http://127.0.0.1:5000/`

### Errors
Errors are returned as a JSON object in the following format
```json
{
    "success": false,
    "error": 400,
    "message": "bad request"
}
```
The API returns five error types on a failed request
- 400 bad request
- 404 resource not found
- 405 method not allowed
- 422 unprocessable
- 500 internal server error

### Resource endpoint library
#### GET /categories
- Create a GET endpoint to get questions based on category. 
- Request Arguments: The category id to filter the category as an URL parameter and the page integer as a parameter `page=1`
- Returns: An object with a success flag as `true`, a list of paginated questions, number of total questions of the selected category as an integer, and the current category as an object.
```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

#### GET /categories/{id}/questions
- Create a GET endpoint to get questions based on category. 
- Request Arguments: The category id to filter the category as an URL parameter and the page integer as a parameter `page=1`
- Returns: An object with a success flag as `true` a list of paginated questions, number of total questions of the selected category as integer, and the current category as object.
```json
{
  "success": true,
  "currentCategory": {
    "id": 1,
    "type": "Science"
  },
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    }
  ],
  "totalQuestions": 3
}
```

#### GET /questions
- Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, the number of total questions, the current category, categories. 
- Request Arguments: The page integer as a parameter `page=1`
- Returns: An object with a success flag as `true`, a list of paginated questions, number of total questions as an integer, current category as an object, and a dictionary of all categories.
```json
{
  "success": true,
  "questions": [...],
  "totalQuestions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": ""
}
```

#### DELETE /questions/{id}
- An endpoint to DELETE question using a question ID. 
- Request Arguments: The question Id to be deleted
- Returns: An object with a success flag as `true`
```json
{
  "success": true
}
```

#### POST /questions
- The POST has two behavior depending on the body:


- An endpoint to POST a new question, which will require the question and answer as text, category, and difficulty score. 
- Request Body: an object with the question and answer as text, the difficulty ranked from 1 to 5, and the category id,
```json
{
  "question": "How many planets are in the solar system?",
  "answer": "8",
  "difficulty": 2,
  "category": 1
}
```
- Returns: An object with a success flag as `true`
```json
{
  "success": true
}
```


- A POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
- Request Body: An object with the search term
```json
{
  "searchTerm": "Peanut Butter"
}
```
- Returns: An object with a success flag as `true`, a list of paginated questions, number of total questions of the selected category as an integer, and the current category as an object.
```json
{
  "success": true,
  "currentCategory": {
    "id": 1,
    "type": "Science"
  },
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    }
  ],
  "totalQuestions": 3
}
```

#### POST /quizzes
- A POST endpoint to get questions to play the quiz. This endpoint takes a category and previous question parameters and returns random questions within the given category if provided, and that is not one of the previous questions. 
- Request Arguments: None
- Request Body: An object with an array of the id of previous questions, and a category object if there is a selected category.
```json
{
  "previous_questions": [22,20],
  "quiz_category": {
    "type": "Science",
    "id": "1"
  }
}
```
- Returns: An object with a success flag as `true`, and the current question object.
```json
{
  "success": true,
  "question": {
    "answer": "Alexander Fleming",
    "category": 1,
    "difficulty": 3,
    "id": 21,
    "question": "Who discovered penicillin?"
  }
}
```

## Authors
[Gerardo Cortes Oquendo](mailto:gerardo.cortes.o@gmail.com)

## Acknowledgements
To Udacity and the [original code](https://github.com/udacity/FSND/tree/master/projects/02_trivia_api/starter)