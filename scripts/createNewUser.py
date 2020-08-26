#!/usr/bin/env python
"""Create a new admin user able to view the /reports endpoint."""
import sys
from getpass import getpass

from past.builtins import raw_input

from config import app, bc
from models import User, db


def main():
    """Main entry point for script."""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if User.query.all():
            print('A user already exists! Create another? (y/n):'),
            create = raw_input()
            if create == 'n':
                return

        print('Enter username address: ')
        username = raw_input()
        password = getpass()
        assert password == getpass('Password (again):')

        user = User(username=username, password=bc.generate_password_hash(password))
        db.session.as_unique(user)
        db.session.commit()
        print('User added.')


if __name__ == '__main__':
    sys.exit(main())
