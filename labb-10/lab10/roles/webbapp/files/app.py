import json

import pymysql
from flask import Flask, render_template_string

app = Flask(__name__)


@app.get("/")
def index():
    with open("/etc/labbapp/config.json", encoding="utf-8") as file:
        config = json.load(file)

    connection = pymysql.connect(
        host=config["db_host"],
        port=config["db_port"],
        user=config["db_user"],
        password=config["db_password"],
        database=config["db_name"],
        charset="utf8mb4",
        connect_timeout=5,
        read_timeout=5,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, message FROM messages ORDER BY id")
            messages = cursor.fetchall()
    finally:
        connection.close()

    return render_template_string(
        """<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>Labb 10</title>
</head>
<body>
    <h1>Labb 10 – Flask och MariaDB</h1>
    <p>Databas: {{ db_name }} på {{ db_host }}</p>
    <ul>
    {% for id, message in messages %}
        <li>{{ message }}</li>
    {% endfor %}
    </ul>
</body>
</html>""",
        messages=messages,
        db_name=config["db_name"],
        db_host=config["db_host"],
    )
