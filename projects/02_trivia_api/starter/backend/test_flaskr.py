import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('gerardo:123456@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_when_get_categories_then_200(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertEqual({'1': 'Science',
                          '2': 'Art',
                          '3': 'Geography',
                          '4': 'History',
                          '5': 'Entertainment',
                          '6': 'Sports'}, data['categories'])

    def test_when_get_questions_paginated_200(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(19, data['totalQuestions'])
        self.assertEqual({'1': 'Science',
                          '2': 'Art',
                          '3': 'Geography',
                          '4': 'History',
                          '5': 'Entertainment',
                          '6': 'Sports'}, data['categories'])
        self.assertEqual('', data['currentCategory'])

    def test_when_get_questions_paginated_404(self):
        res = self.client().get('/questions?page=99')
        data = json.loads(res.data)

        self.assertEqual(404, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])

    def test_when_delete_questions_then_200(self):
        new_question = Question(question='How many planets are in the solar system?',
                                answer='8',
                                difficulty=1,
                                category=1)
        new_question.insert()
        question_id = new_question.id
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertEqual(None, question)

    def test_when_delete_questions_then_404(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(404, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])

    def test_when_post_questions_add_then_200(self):
        res = self.client().post('/questions', json={'question': 'How many planets are in the solar system?',
                                                     'answer': '8',
                                                     'difficulty': 1,
                                                     'category': 1})
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        question = Question.query.filter(Question.question == 'How many planets are in the solar system?').one_or_none()
        question.delete()

    def test_when_post_questions_add_then_400(self):
        res = self.client().post('/questions', json={'question': 'How many planets are in the solar system?',
                                                     'answer': '8',
                                                     'difficulty': 1,
                                                     'category': 0})
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])

    def test_when_post_questions_search_then_200(self):
        res = self.client().post('/questions', json={'searchTerm': 'Peanut Butter'})
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(1, data['totalQuestions'])
        self.assertEqual('', data['currentCategory'])

    def test_when_post_questions_search_then_400(self):
        res = self.client().post('/questions', json={'searchTerm': None})
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])

    def test_when_get_questions_by_category_then_200(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(4, data['totalQuestions'])
        self.assertEqual('Art', data['currentCategory']['type'])

    def test_when_get_questions_by_category_then_400(self):
        res = self.client().get('/categories/0/questions')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])

    def test_when_post_quizzes_then_200(self):
        res = self.client().post('/quizzes', json={'previous_questions': '',
                                                   'quiz_category': {
                                                       'type': 'Science',
                                                       'id': 1
                                                   }})
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(True, data['success'])
        self.assertTrue(data['question'])

    def test_when_post_quizzes_then_400(self):
        res = self.client().post('/quizzes', json={'previous_questions': '',
                                                   'quiz_category': None})
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertTrue(data['message'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
