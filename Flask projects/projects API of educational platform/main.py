from flask import Flask, request, jsonify
import random as r
from matplotlib import pyplot as plt
from math import prod
app = Flask(__name__)

users = []
list_expressions = []
list_questions = []


@app.route("/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    phone = data["phone"]
    email = data["email"]
    your_score = 0
    your_id = len(users) + 1
    if not first_name or not last_name or not phone or not email:
        return jsonify({"error": "Некорректные данные"})
    if "@" not in email:
        return jsonify({"error": "Почта некорректна"})
    if len(phone) != 11 and phone[0] != "8":
        return jsonify({"error": "Номер некорректен"})
    new_data = {
        "id": your_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "score": your_score,
    }
    users.append(new_data)
    return jsonify(new_data)


@app.route(f"/users/<int:id>", methods=["GET"])
def get_users_data(id):
    return users[id - 1]


@app.route("/math/expression", methods=["GET"])
def math_expression():
    data = request.get_json()
    count_nums = data["count_nums"]
    operation = data["operation"]
    maximum = data["max"]
    minimum = data["min"]
    if not count_nums or not minimum or not minimum or not operation:
        return jsonify({"error": "Данные некорректны"})
    nums = [r.randint(minimum, maximum) for x in range(count_nums)]
    output_data = {
        "id": len(list_expressions) + 1,
        "operation": operation,
    }
    for i in range(count_nums):
        output_data[f"value{i + 1}"] = nums[i]
    input_data = output_data.copy()
    if operation == "+":
        input_data["answer"] = sum(nums)
    if operation == "*":
        input_data["answer"] = prod(nums)
    if operation == "-":
        temp = nums[0]
        for i in range(1,len(nums)):
            temp -= nums[i]
        input_data["answer"] = temp
    list_expressions.append(input_data)
    return jsonify(output_data)


@app.route("/math/<int:expression_id>/solve", methods=["POST"])
def solving_expression(expression_id):
    data = request.get_json()
    user_id = data["user_id"]
    user_answer = data["user_answer"]
    if not user_answer or not user_id:
        return jsonify({"error": "Данные некорректны"})
    if user_answer == list_expressions[expression_id - 1]["answer"]:
        result = "Успех"
        users[user_id - 1]["score"] += 1
    else:
        result = "Неправда"
    output_data = {"expression_id": expression_id, "result": result, "reward": 1}
    return jsonify(output_data)


@app.route("/questions/create", methods=["POST"])
def creating_question():
    data = request.get_json()
    type = data["type"]
    if type == "ONE-ANSWER":
        question_id = len(list_questions) + 1
        output_data = {
            "id": question_id,
            "title": data["title"],
            "description": data["description"],
            "type": data["type"],
            "answer": data["answer"],
        }
        list_questions.append(output_data)
        return jsonify(output_data)
    if type == "MULTIPLE-CHOICE":
        question_id = len(list_questions) + 1
        output_data = {
            "id": question_id,
            "title": data["title"],
            "description": data["description"],
            "type": data["type"],
            "choices": data["choices"],
            "answer": data["answer"],
        }
        list_questions.append(output_data)
        return jsonify(output_data)


@app.route("/questions/random", methods=["GET"])
def random_question():
    cur_question = r.choice(list_questions)
    output_data = {"question_id": cur_question["id"], "reward": 1}
    return jsonify(output_data)


@app.route("/questions/<int:question_id>/solve", methods=["POST"])
def solve_question(question_id):
    data = request.get_json()
    user_id = data["user_id"]
    user_answer = data["user_answer"]
    if not user_answer or not user_id:
        return jsonify({"error": "Данные некорректны"})
    if user_answer == list_questions[question_id - 1]["answer"]:
        result = "Успех"
        users[user_id - 1]["score"] += 1
    else:
        result = "Неправда"
    output_data = {"question_id": question_id, "result": result, "reward": 1}
    return jsonify(output_data)

@app.route("/users/leaderboard", methods = ["GET"])
def show_leaderboard():
    data = request.get_json()
    type = data["type"]
    users.sort(key = lambda x: x["score"], reverse = True)
    if type == "table":
        leaderboard = []
        for x in users:
            temp = {
                "first_name": x["first_name"],
                "last_name": x["last_name"],
                "score": x["score"]
            }
            leaderboard.append(temp)
        return jsonify(leaderboard)
    elif type == "graph":
        names = [x["first_name"] for x in users]
        values = [x["score"] for x in users]
        plt.bar(names, values)
        plt.savefig("leaders.jpg")
        return "<img src='leaders.jpg'>"


if __name__ == "__main__":
    app.run(debug=True, port="5000")
