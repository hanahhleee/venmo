from datetime import datetime
import json

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(error, code=404):
    return json.dumps({"success": False, "error": error}), code


@app.route("/")
@app.route("/api/users/")
def get_users():
    return success_response(DB.get_all_users())


@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    if not name:
        return failure_response("Missing required field: name", 400)
    elif not username:
        return failure_response("Missing required field: username", 400)
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    user["transactions"] = []
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        transactions = DB.get_transactions_of_user(user_id)
        if transactions:
            for x in transactions:
                if "accepted" in x:
                    if x["accepted"] == 1:
                        x["accepted"] = True
                    elif x.get("accepted") == 0:
                        x["accepted"] = False
            user["transactions"] = transactions
        return success_response(user)
    return failure_response("User not found")


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if not user:
        return failure_response("User not found")
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")
    if sender_id is None or receiver_id is None or amount is None:
        if sender_id is None:
            return failure_response("Missing required field: sender_id", 400)
        if receiver_id is None:
            return failure_response("Missing required field: receiver_id", 400)
        if amount is None:
            return failure_response("Missing required field: amount", 400)
    user1 = DB.get_user_by_id(sender_id)
    user2 = DB.get_user_by_id(receiver_id)
    if user1 is None or user2 is None:
        return failure_response("User not found")
    elif accepted is not None and body["accepted"] == True:
        if amount > 0 and amount <= user1["balance"]:
            now = datetime.now()
            timestamp = now.strftime("%H:%M")
            transaction_id = DB.insert_transaction(
                timestamp, sender_id, receiver_id, amount, message, accepted)
            transaction = DB.get_transaction_by_id(transaction_id)
            if transaction is None:
                return failure_response("Transaction could not be created")
            elif transaction is not None:
                transaction["accepted"] = True
                DB.update_user_by_id(
                    transaction["sender_id"], user1["balance"]-transaction["amount"])
                DB.update_user_by_id(
                    transaction["receiver_id"], user2["balance"]+transaction["amount"])
                return success_response(transaction)
        elif amount > user1["balance"]:
            return failure_response("Invalid amount", 400)
    elif accepted is None:
        now = datetime.now()
        timestamp = now.strftime("%H:%M")
        transaction_id = DB.insert_transaction(
            timestamp, sender_id, receiver_id, amount, message, accepted)
        transaction = DB.get_transaction_by_id(transaction_id)
        if transaction is None:
            return failure_response("Transaction could not be created")
        elif transaction is not None:
            return success_response(transaction)
    return failure_response("Invalid input in field accepted")


@app.route("/api/transaction/<int:transaction_id>/", methods=["POST"])
def accept_payment_request(transaction_id):
    body = json.loads(request.data)
    accepted = body.get("accepted")
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("Transaction not found")
    user1 = DB.get_user_by_id(transaction["sender_id"])
    user2 = DB.get_user_by_id(transaction["receiver_id"])
    tacc = transaction.get("accepted")
    if tacc is None and accepted is not None:
        if body["accepted"] == True:
            if transaction["amount"] > 0 and transaction["amount"] <= user1["balance"]:
                transaction["accepted"] = True
                now = datetime.now()
                timestamp = now.strftime("%H:%M")
                DB.update_transaction_by_id(
                    transaction_id, timestamp, accepted)
                DB.update_user_by_id(
                    transaction["sender_id"], user1["balance"]-transaction["amount"])
                DB.update_user_by_id(
                    transaction["receiver_id"], user2["balance"]+transaction["amount"])
                return success_response(transaction)
            elif transaction["amount"] > user1["balance"]:
                return failure_response("Insuffient funds", 400)
        elif body["accepted"] == False:
            transaction["accepted"] = False
            now = datetime.now()
            timestamp = now.strftime("%H:%M")
            DB.update_transaction_by_id(transaction_id, timestamp, accepted)
            return success_response(transaction)
    elif tacc is not None:
        return failure_response("Transaction has already been accepted or denied")
    return failure_response("Missing required field: accepted", 400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
