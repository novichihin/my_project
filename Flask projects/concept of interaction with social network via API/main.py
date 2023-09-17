from flask import Flask, request, jsonify
from matplotlib import pyplot as plt
import re

app = Flask(__name__)

users = []
emails_list = []
posts = []
pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"


@app.route("/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    your_id = len(users) + 1
    if not first_name or not last_name or not email:
        return jsonify({"error": "Некорректные данные"})
    if re.match(pattern, email) is None:
        return jsonify({"error": "Почта некорректна"})
    if email in emails_list:
        return jsonify({"error": "Почта уже использована"})
    emails_list.append(email)
    new_data = {
        "id": your_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "posts": [],
        "total_reactions": 0,
    }
    users.append(new_data)
    return jsonify(new_data)


@app.route(f"/users/<int:id>", methods=["GET"])
def get_users_data(id):
    if id in [x["id"] for x in users]:
        return jsonify(users[id - 1])
    return jsonify({"error": "Некорректный индекс"})


@app.route("/posts/create", methods=["POST"])
def post_create():
    data = request.get_json()
    author_id = data["author_id"]
    text = data["text"]
    if not text or not author_id:
        return jsonify({"error": "Некорректные данные"})
    post_id = len(posts) + 1
    users[author_id - 1]["posts"].append(post_id)
    output_data = {"id": post_id, "author_id": author_id, "text": text, "reactions": []}
    posts.append(output_data)
    return jsonify(output_data)


@app.route(f"/posts/<int:post_id>", methods=["GET"])
def get_post_data(post_id):
    if post_id in [x["id"] for x in posts]:
        return jsonify(posts[post_id - 1])
    return jsonify({"error": "Некорректный индекс"})


@app.route("/posts/<int:post_id>/reaction", methods=["POST"])
def create_reaction(post_id):
    if post_id in [x["id"] for x in posts]:
        data = request.get_json()
        reaction = data["reaction"]
        posts[post_id - 1]["reactions"].append(reaction)
        user_id = posts[post_id - 1]["author_id"]
        users[user_id - 1]["total_reactions"] += 1
        return jsonify({"message": "accepted"})
    else:
        return jsonify({"error": "Некорректный индекс"})


@app.route("/users/<int:user_id>/posts", methods=["GET"])
def show_users_posts(user_id):
    if user_id in [x["id"] for x in users]:
        data = request.get_json()
        posts_ids = users[user_id - 1]["posts"]
        all_posts = [posts[i] for i in posts_ids]
        if data["sort"] == "asc":
            all_posts.sort(key=lambda x: len(x["reactions"]))
        elif data["sort"] == "desc":
            all_posts.sort(key=lambda x: len(x["reactions"]), reverse=True)
        return jsonify(all_posts)


@app.route("/users/leaderboard", methods=["GET"])
def show_leaderboard():
    data = request.get_json()
    type = data["type"]
    if type == "list":
        sort = data["sort"]
        if sort == "asc":
            users.sort(key=lambda x: x["total_reactions"])
        elif sort == "desc":
            users.sort(key=lambda x: x["total_reactions"], reverse=True)
        leaderboard = [x for x in users]
        return jsonify(leaderboard)

    elif type == "graph":
        names = [x["first_name"] for x in users]
        values = [x["total_reactions"] for x in users]
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
