# routes.py
from flask import render_template, request, redirect, url_for, flash,session,jsonify
from flask_login import login_required, login_user, logout_user, current_user
from word_test import app, login_manager,db
from word_test.models import User,Word, MistakeBook,WordLabel
import bcrypt
from AnswerChecker import AnswerChecker
import re
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # 检查当前用户是否已登录
    if current_user.is_authenticated:
        # 如果已登录，重定向到主页
        return redirect(url_for('home'))
    else:
        # 如果未登录，重定向到登录页面
        return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    # 这里添加首页的内容
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 从数据库中查询用户
        user = User.query.filter_by(username=username).first()
        print(user)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # 如果用户名和密码正确，用户应该被标记为已登录并重定向到主页
            login_user(user)
            return redirect(url_for('home'))
        else:
            # 如果用户名或密码错误，显示错误消息
            flash('用户名或密码错误')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/configure_practice', methods=['GET', 'POST'])
@login_required
def configure_practice():
    if request.method == 'POST':
        # 获取用户设置
        practice_type = request.form['practice_type']
        word_label_id = request.form['word_label']
        practice_mistake_book = 'practice_mistake_book' in request.form
        number_of_words = request.form['number_of_words']

        # 可以将这些设置保存在session或数据库中
        session['practice_type'] = practice_type
        session['word_label_id'] = word_label_id
        session['number_of_words'] = number_of_words
        session['practice_mistake_book'] = practice_mistake_book

        # 重定向到练习页面
        return redirect(url_for('practice'))

    # 如果是GET请求，显示配置页面
    word_labels = WordLabel.query.all()  # 从数据库获取所有标签
    return render_template('configure_practice.html', word_labels=word_labels)

@app.route('/practice')
@login_required
def practice():
    practice_type = session.get('practice_type')
    number_of_words = int(session.get('number_of_words', 10))
    practice_mistake_book = session.get('practice_mistake_book', False)

    if practice_mistake_book:
        mistake_entries = MistakeBook.query.filter_by(user_id=current_user.id).order_by(db.func.random()).limit(number_of_words).all()
        word_ids = [entry.word_id for entry in mistake_entries]
        words_query = Word.query.filter(Word.id.in_(word_ids)).all()
    else:
        words_query = Word.query.order_by(db.func.random()).limit(number_of_words)

    words = [word.to_dict() for word in words_query]
    session['words'] = words

    return render_template('practice.html', words=words, practice_type=practice_type)

@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    data = request.get_json()
    word_id = data.get('word_id')
    user_answer = data.get('user_answer')

    word = Word.query.get(word_id)
    practice_type = session.get('practice_type')

    def clean_answer(answer):
        # 去除括号及其内容，然后去除首尾空格
        cleaned_answer = re.sub(r'\([^)]*\)', '', answer).strip()
        return cleaned_answer

    if practice_type == "english_to_chinese":
        correct_answers = [clean_answer(answer) for answer in re.split(r'[,;\s.、，；。]', word.translation)]
        checker = AnswerChecker('./bert-base-chinese-tokenizer', './bert-base-chinese-model')
        is_correct = False

        for correct_answer in correct_answers:
            similarity = checker.cosine_similarity(checker.get_sentence_embedding(user_answer), checker.get_sentence_embedding(correct_answer))
            print(user_answer,correct_answer,similarity)
            if similarity > 0.79:
                is_correct = True
                break

    elif practice_type == "chinese_to_english":
        correct_answers = [clean_answer(answer) for answer in re.split(r'[,;\s.、，；。]', word.word)]
        is_correct = any(user_answer.lower() == correct_answer.lower() for correct_answer in correct_answers)
    else:
        return jsonify({'error': 'Invalid practice type'}), 400

    # 更新错题本
    mistake_entry = MistakeBook.query.filter_by(user_id=current_user.id, word_id=word.id).first()
    if not mistake_entry:
        mistake_entry = MistakeBook(user_id=current_user.id, word_id=word.id, incorrect_answers=0, correct_answers=0)
        db.session.add(mistake_entry)

    if is_correct:
        mistake_entry.correct_answers += 1
    else:
        mistake_entry.incorrect_answers += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating MistakeBook: {e}")

    # 返回 JSON 响应
    return jsonify({'correct': is_correct})

@app.route('/mistakes', methods=['GET'])
@login_required
def mistakes():
    # 查询当前用户的错题本数据
    user_mistakes = MistakeBook.query.filter_by(user_id=current_user.id).all()

    # 创建一个包含详细信息的错题列表
    mistakes_data = []
    for index, mistake in enumerate(user_mistakes, start=1):
        word = Word.query.get(mistake.word_id)
        mistakes_data.append({
            'index': index,
            'word': word.word,
            'part_of_speech': word.part_of_speech,
            'incorrect_answers': mistake.incorrect_answers,
            'correct_answers': mistake.correct_answers
        })

    # 渲染模板并传递数据
    return render_template('mistakes.html', mistakes=mistakes_data)

