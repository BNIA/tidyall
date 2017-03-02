#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""views

This file contains the endpoints for rendering the interface and implementing
the backend modules
"""

from __future__ import absolute_import, print_function, unicode_literals
from os import path

from flask import jsonify, render_template, request
from werkzeug import secure_filename

from .config import allowed_file, app, UPLOAD_FOLDER
from .context import modules  # pylint: disable=unused-import
from modules import tidyall


@app.route('/')
def index():
    """Renders the index

    Args:
        None

    Returns:
        rendered template of "index.html"
    """
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handles the uploaded file

    Args:
        None

    Returns:
        if POST: return upload success response
    """

    if request.method == "POST":

        file = request.files["file"]

        if file and allowed_file(file.filename):

            app.file_name = secure_filename(file.filename)
            file.save(path.join(UPLOAD_FOLDER, app.file_name))

            app.df = tidyall.TidyAll(
                path.join(UPLOAD_FOLDER, app.file_name),
                debug=True
            )

            response = {"received": True, "file_name": app.file_name}

            return jsonify(response)


@app.route("/<file_name>", methods=["GET", "POST"])
def parse_date(file_name):
    """Parses the uploaded file

    Args:
        file_name (`str`): path of the uploaded file

    Returns:
        if POST: (`str`): status of parsing file
        if GET: (`list` of `str`): list of column names in file in rendered
                template of "params.html"
    """

    if request.method == "POST":

        response = request.form.to_dict()
        print("LOOOOOOOOOOOOOOOOOOOOOK", response, response.keys())
        app.df.set_col(response)

        del response["column"]
        print("LOOOOOOOOOOOOOOOOOOOOOK", response, response.keys())
        app.df.set_opt(response.keys())

        status_payload = "success" if app.df.download() else "fail"

        return render_template("status.html", status=status_payload)

    if app.df:
        return render_template(
            "params.html",
            cols=app.df.get_cols(),
            opts={
                "Date": "date",
                "BlockNLot": "blocknlot"
            }
        )

    return render_template("params.html")


@app.route("/exit")
def shutdown():
    """Calls the destructor and shuts down server

    Args:
        None

    Returns:
        (`str`): Server shutdown message
    """

    # ensures the destructor is called before shutting down
    del app.df

    werkzeug_server = request.environ.get("werkzeug.server.shutdown")
    if not werkzeug_server:
        raise RuntimeError("Not running with the Werkzeug Server")

    werkzeug_server()

    return "Server shutting down..."