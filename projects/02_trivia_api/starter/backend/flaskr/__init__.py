import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    @TODO: Delete the sample route after completing the TODOs
    '''

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    @app.route('/categories')
    def get_categories():
        categories = {category.id: category.type for category in Category.query.all()}

        return jsonify({
            'success': True,
            'categories': categories
        })

    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        current_questions = paginate(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = {category.id: category.type for category in Category.query.all()}

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(selection),
            'categories': categories,
            'currentCategory': ''
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        try:
            question.delete()
            return jsonify({
                'success': True
            })

        except:
            abort(422)

    '''
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions', methods=['POST'])
    def post_questions():
        body = request.get_json()

        search_term = body.get('searchTerm', None)

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        if search_term:
            return search_questions(request, search_term)

        elif new_question and new_answer and new_difficulty and new_category:
            return add_questions(new_question, new_answer, new_difficulty, new_category)

        else:
            abort(400)

    def add_questions(new_question, new_answer, new_difficulty, new_category):
        category = Category.query.get(new_category)
        if category is None:
            abort(400)

        try:
            question = Question(question=new_question,
                                answer=new_answer,
                                difficulty=new_difficulty,
                                category=new_category)
            question.insert()

            return jsonify({
                'success': True
            })

        except:
            abort(422)

    def search_questions(request, search_term):
        selection = Question.query \
            .filter(Question.question.ilike('%{}%'.format(search_term))) \
            .all()
        questions = paginate(request, selection)
        return jsonify({
            'success': True,
            'questions': questions,
            'totalQuestions': len(selection),
            'currentCategory': ''
        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(400)

        selection = Question.query.filter(Question.category == category_id)
        questions = paginate(request, selection)
        return jsonify({
            'success': True,
            'questions': questions,
            'totalQuestions': len(questions),
            'currentCategory': category.format()
        })

    @app.route('/quizzes', methods=['POST'])
    def post_quizzes():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if previous_questions is None or quiz_category is None:
            abort(400)

        category_id = int(quiz_category['id'])
        if Category.query.get(category_id):
            categories = Question.query \
                .filter(Question.category == category_id, Question.id.notin_(previous_questions)) \
                .all()
        else:
            categories = Question.query \
                .filter(Question.id.notin_(previous_questions)) \
                .all()

        return jsonify({
            'success': True,
            'question': random.choice(categories).format() if categories else ''
        })

    # ---
    # Error Handler
    # ---

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
