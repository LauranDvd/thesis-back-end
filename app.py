from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/proof', methods=['GET'])
def proof():
    theorem = request.args.get("theorem")
    if not theorem:
        return jsonify({"error": "No theorem provided"}), 400

    return jsonify({"message": f"You've sent: {theorem}"})


if __name__ == '__main__':
    app.run()
