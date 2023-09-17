from flask import Flask, request, jsonify
from matplotlib import pyplot as plt
import re

app = Flask(__name__)

users = []
emails_list = []
contests_list = []
pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"


@app.route("/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    sport = data["sport"]
    your_id = len(users) + 1
    if not first_name or not last_name or not email or not sport:
        return jsonify({"error": "Некорректные данные"})
    if re.match(pattern, email) is None:
        return jsonify({"error": "Почта некорректна"})
    if email in emails_list:
        return jsonify({"error": "Почта уже использована"})
    new_data = {
        "id": your_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "contests": [],
    }
    users.append(new_data)
    return jsonify(new_data)


@app.route(f"/users/<int:id>", methods=["GET"])
def get_users_data(id):
    if id in [x["id"] for x in users]:
        return jsonify(users[id - 1])
    return jsonify({"error": "Некорректный индекс"})


@app.route("/contests/create", methods=["POST"])
def contests_create():
    data = request.get_json()
    name = data["name"]
    sport = data["sport"]
    participants = data["participants"]
    if not name or not sport or not participants:
        return jsonify({"error": "Некорректные данные"})
    contest_id = len(contests_list) + 1
    for man in participants:
        users[man - 1]["contests"].append(contest_id)
    output_data = {
        "id": contest_id,
        "name": name,
        "sport": sport,
        "status": "STARTED",
        "participants": participants,
        "winner": "Соревнования еще идут",
    }
    contests_list.append(output_data)
    return jsonify(output_data)


@app.route(f"/contests/<int:contest_id>", methods=["GET"])
def get_contest_data(contest_id):
    if contest_id in [x["id"] for x in contests_list]:
        return jsonify(contests_list[contest_id - 1])
    return jsonify({"error": "Некорректный индекс"})


@app.route("/contests/<int:contest_id>/finish", methods=["POST"])
def finish_contest(contest_id):
    if contest_id in [x["id"] for x in contests_list]:
        data = request.get_json()
        winner = data["winner"]
        if not winner:
            return jsonify({"error": "Некорректные данные"})
        contests_list[contest_id - 1]["status"] = "FINISHED"
        contests_list[contest_id - 1]["winner"] = winner
        return jsonify(contests_list[contest_id - 1])
    return jsonify({"error": "Некорректный индекс"})


@app.route("/users/<int:user_id>/contests", methods=["GET"])
def users_contests(user_id):
    if user_id in [x["id"] for x in users]:
        data = users[user_id - 1]
        contests = []
        for contest in data["contests"]:
            contests.append(contests_list[contest - 1])
        return jsonify(contests)
    return jsonify({"error": "Некорректный индекс"})


@app.route("/users/leaderboard", methods=["GET"])
def show_leaderboard():
    data = request.get_json()
    type = data["type"]
    if type == "table":
        sort = data["sort"]
        if sort == "asc":
            users.sort(key=lambda x: len(x["contests"]))
        elif sort == "desc":
            users.sort(key=lambda x: len(x["contests"]), reverse=True)
        leaderboard = [x for x in users]
        return jsonify(leaderboard)

    elif type == "graph":
        names = [x["first_name"] for x in users]
        values = [len(x["contests"]) for x in users]
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot()
        ax.hist(values, bins=len(names))
        ax.grid()
        plt.savefig("leaders.jpg")
        return "<img src='leaders.jpg'>"
    else:
        return jsonify({"error": "Некорректные данные"})


if __name__ == "__main__":
    app.run(debug=True, port="5000")
