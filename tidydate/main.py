from __future__ import absolute_import, print_function, unicode_literals

from app import views


if __name__ == '__main__':
    views.app.run(debug=True)