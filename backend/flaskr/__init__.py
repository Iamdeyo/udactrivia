import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagenation(request, data):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted = [ d.format() for d in data ]

    return formatted[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    @app.route('/categories')
    def get_categories():
        data = {}
        categories = Category.query.order_by('id').all()

        for category in categories:
            data[category.id] = category.type

        return jsonify({
            "categories": data
        })

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by('id').all()
        formatted_questions = pagenation(request, questions)

        if len(formatted_questions) < 1:
            abort(404)

        #  Get all the categories
        data = {}
        categories = Category.query.order_by('id').all()
        for category in categories:
            data[category.id] = category.type


        return jsonify({
                "questions": formatted_questions,
                "totalQuestions": len(questions),
                "categories": data,
                "currentCategory": "All"
            })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success' : True
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question(): 
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            if len(answer) > 0 or len(question) > 0:
                question = Question(question=question, answer=answer, category=category, difficulty=difficulty)

                question.insert()
                return jsonify({
                'success' : True
                })
            else:
                abort(400)
        except:
            abort(422)
        

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """



    @app.route('/questions/search', methods=['POST'])
    def search():
        try:
            body = request.get_json()
            searchTerm = body.get('searchTerm', None)

            question = Question.query.filter(Question.question.ilike("%" + searchTerm + "%")).all()

            questions = pagenation(request, question)

            return jsonify({
            "questions": questions,
            "totalQuestions": len(question),
            "currentCategory": "All"
            })
        except:
            abort(422)

        

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/categories/<int:id>/questions')
    def get_by_category(id):
        category = Category.query.filter(Category.id == id).one_or_none()

        if category is  None:
            return abort(422)

        question = Question.query.filter(Question.category == id).all()
        questions = pagenation(request, question)

        return jsonify({
            "questions": questions,
            "totalQuestions": len(question),
            "currentCategory": category.type
        })
            
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        try:              
            # get the questions by category
            if quiz_category['id'] == 0:
                # get all when quiz_category = all
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == quiz_category['id']).all()

            formatted_questions = [ q.format() for q in questions ]
            question = []
            # get each questions and sorting out previous questions
            for fq in formatted_questions:    
                if previous_questions.__contains__(fq.get('id')) == False:
                    question.append(fq)
        
            total_questions = len(question)

            # check if no question is left
            if total_questions < 1:
                quiz_question = ''
            else:
                # generating a random question selection
                randomNumber = random.randint(0, (total_questions - 1))
                print(question[randomNumber])
                quiz_question = question[randomNumber]

            return jsonify({
                "question": quiz_question
                })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """


    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({
            'success': False,
            'error' : 400,
            'message' : 'Bad Request'
        }), 400)

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
            'success': False,
            'error' : 404,
            'message' : 'Resource Not Found'
        }), 404)

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return (jsonify({
            'success': False,
            'error' : 422,
            'message' : 'Unprocessable Entity'
        }), 422)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return (jsonify({
            'success': False,
            'error' : 500,
            'message' : 'Internal Server Error'
        }), 500)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

