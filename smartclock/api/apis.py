from smartclock import app, db
from flask import request, jsonify
from smartclock.model.models import User, Timesheet, user_schema, users_schema, timesheet_schema, timesheets_schema
from smartclock.utility.hash_password import hash_password
from datetime import datetime
from sqlalchemy import desc


# REST API Implementation
# create a timesheet
@app.route('/api/v1/timesheet', methods=['POST'])
def create_timesheet():
    date = request.json['date']
    todays_date = datetime.utcnow().date()
    clock_in_time = request.json['clock_in_time']
    clock_out_time = request.json['clock_out_time']
    is_clocked_in = request.json['is_clocked_in']
    user_id = request.json['user_id']
    new_timesheet = Timesheet(date=date, todays_date=todays_date, clock_in_time=clock_in_time,
                              clock_out_time=clock_out_time, is_clocked_in=is_clocked_in, user_id=user_id)
    db.session.add(new_timesheet)
    db.session.commit()
    return timesheet_schema.jsonify(new_timesheet)


# create a user
@app.route('/api/v1/user', methods=['POST'])
def create_user():
    username = request.json['username']
    password = request.json['password']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    is_approved = request.json['is_approved']
    is_admin = request.json['is_admin']
    confirmed = request.json['confirmed']
    timesheets = request.json['timesheets']

    hashed_password = hash_password(password)

    new_user = User(username=username, timesheets=timesheets, first_name=first_name, last_name=last_name, email=email,
                    is_admin=is_admin, is_approved=is_approved, password=hashed_password, confirmed=confirmed)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)


# with this command update any field of a user except id and password
# patch method
@app.route('/api/v1/user/patch/<username>', methods=['PATCH'])
def patch_anything(username):
    user = User.query.filter_by(username=username).first()
    if user:
        for key in request.json:
            if key == 'is_admin':
                user.is_admin = request.json[key]
            elif key == 'is_approved':
                user.is_approved = request.json[key]
            elif key == 'confirmed':
                user.confirmed = request.json[key]
            elif key == 'username':
                user.username = request.json[key]
            elif key == 'first_name':
                user.first_name = request.json[key]
            elif key == 'last_name':
                user.last_name = request.json[key]
            elif key == 'email':
                user.email = request.json[key]
            elif key == 'timesheets':
                user.timesheets = request.json[key]
        db.session.commit()
        return user_schema.jsonify(user)
    else:
        return jsonify("custom_message_error", "user doesn't exist with that given username")



# get all users
@app.route('/api/v1/users', methods=['GET'])
def get_users_all():
    users = User.query.all()
    result = users_schema.dump(users)
    return jsonify(result)


# get a user by its username
@app.route('/api/v1/users/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'custom_error': 'user does not exist'})
    return user_schema.jsonify(user)

# get a user by its id
@app.route('/api/v1/user/<int:uid>', methods=['GET'])
def get_user_by_id(uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'custom_error': 'user does not exist'})
    return user_schema.jsonify(user)



# get all timesheets
@app.route('/api/v1/timesheets', methods=['GET'])
def get_timesheets_all():
    all_timesheets = Timesheet.query.all()
    result = timesheets_schema.dump(all_timesheets)
    return jsonify(result)


# get a timesheet by its id
@app.route('/api/v1/timesheet/<int:uid>', methods=['GET'])
def get_timesheet_by_id(uid):
    timesheet = Timesheet.query.get_or_404(uid)
    if not timesheet:
        return jsonify({'message': 'timesheet does not exist'})
    return timesheet_schema.jsonify(timesheet)

# get all timesheets for a specific username
@app.route('/api/v1/timesheets/<string:username>', methods=['GET'])
def get_timesheets_by_username(username):
    user = User.query.filter_by(username=username).one_or_none()
    if user:
        if user.is_approved and not user.is_admin:
            timesheets = Timesheet.query.filter_by(user_id=user.id).all()
            if not timesheets:
                return jsonify({'custom_error': 'timesheets do not exist'})
            return timesheets_schema.jsonify(timesheets)
        else:
            return jsonify({'custom_error':'user role is invalid'})
    else:
        return jsonify({'custom_error':'username is invalid'})


# delete a user by username
@app.route('/api/v1/user/<username>', methods=['DELETE'])
def delete_user(username):
    user_to_be_deleted = User.query.filter_by(username=username).first()

    if not user_to_be_deleted:
        return jsonify({'message': 'user does not exist'})

    ts_of_that_user = Timesheet.query.filter_by(user_id=user_to_be_deleted.id).all()

    if len(ts_of_that_user) > 0:
        Timesheet.query.filter_by(user_id=user_to_be_deleted.id).delete()

    db.session.delete(user_to_be_deleted)
    db.session.commit()
    return user_schema.jsonify(user_to_be_deleted)


# delete a timesheet by id
@app.route('/api/v1/timesheet/<int:id>', methods=['DELETE'])
def delete_timesheet(id):
    ts = Timesheet.query.filter_by(id=id).first()
    if not ts:
        return jsonify({'message': 'timesheet does not exist'})
    db.session.delete(ts)
    db.session.commit()
    return timesheet_schema.jsonify(ts)


# custom function with patch method for api
@app.route('/api/v1/clock/<username>', methods=['GET'])
def clock_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'was not found'})
    if not user.is_approved and user.is_admin:
        return jsonify({'error': 'method impossible'})

    """
    # Logic
    if user has no timesheets [] => create one
    if user has timesheets:
        find last created timesheet by filtering date field AS that_row

        if that_row.is_clocked_in is True:
            that_row.clock_out_time = datetime.utcnow()
            that_row.is_clocked_in = False
            db.session.commit()
            return timesheet_schema.jsonify(that_row)

        else:
            new_stamp = Timesheet(is_clocked_in=True, clock_in_time=utcnow(), date=utcnow())
            db.session.add(new_stamp)
            db.session.commit()
            return timesheet_schema.jsonify(new_stamp)
    """

    if len(user.timesheets) == 0:
        new_stamp = Timesheet(is_clocked_in=True, clock_in_time=datetime.utcnow(), date=datetime.utcnow(),
                              user_id=user.id)
        db.session.add(new_stamp)
        db.session.commit()
        return timesheet_schema.jsonify(new_stamp)
    else:
        last_stamp = Timesheet.query.filter(Timesheet.user_id == user.id).order_by(desc(Timesheet.date)).limit(
            1).first()

        if last_stamp.is_clocked_in is True:
            last_stamp.clock_out_time = datetime.utcnow()
            last_stamp.is_clocked_in = False
            db.session.commit()
            return timesheet_schema.jsonify(last_stamp)
        else:
            new_stamp = Timesheet(is_clocked_in=True, clock_in_time=datetime.utcnow(), date=datetime.utcnow(),
                                  user_id=user.id)
            db.session.add(new_stamp)
            db.session.commit()
            return timesheet_schema.jsonify(new_stamp)

@app.route('/api/v1/clock_status/<username>', methods=['GET'])
def get_clock_bool(username):

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'was not found'})
    if not user.is_approved and user.is_admin:
        return jsonify({'error': 'method impossible'})

    if len(user.timesheets) == 0:
        return jsonify({'clock_status': False})

    last_stamp = Timesheet.query.filter(Timesheet.user_id == user.id).order_by(desc(Timesheet.date)).limit(1).first()

    if last_stamp.is_clocked_in is True:
        return jsonify({'clock_status': True,'last_time':last_stamp.clock_in_time})
    else:
        return jsonify({'clock_status': False})



