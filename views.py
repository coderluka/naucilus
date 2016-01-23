import datetime
from flask import render_template, redirect, url_for, flash
from flask_peewee.utils import get_object_or_404, object_list
from app import app
from auth import auth
from models import User, Message, Relationship

#demo route....................................................[WORKING][DESIGN BUGS]
@app.route('/demo')
def demo():
	return render_template('demo.html')

#home route....................................................[WORKING][DONE]
@app.route('/')
@auth.login_required
def index():
	return render_template('index.html')

#login route....................................................[WORKING][DONE]

#about route
@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	msg = Message("",
                  sender="",
                  recipients=[""])
	return render_template('contact.html')

#profile route....................................................[WORKING][SECURED]

@app.route('/profile/')
@auth.login_required
def private_timeline():
    user = auth.get_logged_in_user()

    messages = Message.select().where(Message.user << user.following()).order_by(Message.pub_date.desc())
    return object_list('profile.html',
			messages,
			'message_list',
			course_1_name='jhdsjhdjs',
			progress='50',
			course_1_description='opis opis opis',
			)

#notes route....................................................[IN PROGRESS][DESIGN BUGS]


#course route....................................................[WORKING]
@app.route('/photoshop')
@auth.login_required
def coursePS():
	return render_template('CoursePhotoshop.html',
				course_name='Photoshop',
				course_description='Opis kursa...',
				CourseSegment_name='etwas?...',
				video_description='lekcija opis',
				course_info='info o kursu',)

#course route....................................................[WORKING]
@app.route('/html')
@auth.login_required
def courseHTML():
	return render_template('CourseHTML.html',
				course_name='HyperTextMarkupLanguage',
				course_description='Opis kursa...',
				CourseSegment_name='etwas?...',
				video_description='lekcija opis',
				course_info='info o kursu',)

#forum timeline route....................................................[WORKING][DESIGN]
@app.route('/forum')
def public_timeline():
    messages = Message.select().order_by(Message.pub_date.desc())
    return object_list('forum.html', messages, 'message_list')

#register route....................................................[IN PROGRESS][!!!][DESIGN BUGS]
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and request.form['username']:
        try:
            user = User.select().where(User.username==request.form['username']).get()
            flash('That username is already taken')
        except User.DoesNotExist:
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                join_date=datetime.datetime.now()
            )
            user.set_password(request.form['password'])
            user.save()

            auth.login_user(user)
            return redirect(url_for('accounts/login'))

    return render_template('register.html')

#friend list....................................................[NOT YET]
@app.route('/following')
@auth.login_required
def following():
    user = auth.get_logged_in_user()
    return object_list('user_following.html', user.following(), 'user_list')

#badges-AchievementSystem-backpack.................................[IN PROGRESS][DESIGN]

@app.route('/badges')
@auth.login_required
def badges():
	#badges = Badges.select().order_by(Badges.badgeslevel)
	#return object_list('badges_list.html', badges, 'badges_list')
	return render_template('badges_list.html')

#list all users....................................................[NOT YET][FIX] Everyone can see, who is logdon
@app.route('/users')
def user_list():
    users = User.select().order_by(User.username)
    return object_list('user_list.html', users, 'user_list')

#particular user "profile"....................................................[WORKING][DESIGN][FIX]
@app.route('/users/<username>')
def user_detail(username):
    user = get_object_or_404(User, User.username==username)
    messages = user.message_set.order_by(Message.pub_date.desc())
    return object_list('user_detail.html', messages, 'message_list', person=user)

#follow particular user....................................................[NOT YET]
@app.route('/users/<username>/follow/', methods=['POST'])
@auth.login_required
def user_follow(username):
    user = get_object_or_404(User, User.username==username)
    Relationship.get_or_create(
        from_user=auth.get_logged_in_user(),
        to_user=user,
    )
    flash('You are now following %s' % user.username)
    return redirect(url_for('user_detail', username=user.username))

#unfollow particular user....................................................[NOT YET]
@app.route('/users/<username>/unfollow', methods=['POST'])
@auth.login_required
def user_unfollow(username):
    user = get_object_or_404(User, User.username==username)
    Relationship.delete().where(
        Relationship.from_user==auth.get_logged_in_user(),
        Relationship.to_user==user,
    ).execute()
    flash('You are no longer following %s' % user.username)
    return redirect(url_for('user_detail', username=user.username))

#post something....................................................[NOT YET][DESIGN]
@app.route('/post', methods=['GET', 'POST'])
@auth.login_required
def create():
    user = auth.get_logged_in_user()
    if request.method == 'POST' and request.form['content']:
        message = Message.create(
            user=user,
            content=request.form['content'],
        )
        flash('Your post has been created')
        return redirect(url_for('user_detail', username=user.username))

    return render_template('create.html')

#edit some post....................................................[NOT YET][DESIGN]
@app.route('/edit/<int:message_id>/', methods=['GET', 'POST'])
@auth.login_required
def edit(message_id):
    user = auth.get_logged_in_user()
    message = get_object_or_404(Message, Message.user==user, Message.id==message_id)
    if request.method == 'POST' and request.form['content']:
        message.content = request.form['content']
        message.save()
        flash('Your changes were saved')
        return redirect(url_for('user_detail', username=user.username))

    return render_template('edit.html', message=message)
