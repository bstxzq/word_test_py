# routes.py
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_required, login_user, logout_user, current_user
from word_test import app, login_manager,db
from word_test.models import User,Word, MistakeBook,WordLabel
import bcrypt

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
        number_of_words = request.form['number_of_words']

        # 可以将这些设置保存在session或数据库中
        session['practice_type'] = practice_type
        session['word_label_id'] = word_label_id
        session['number_of_words'] = number_of_words

        # 重定向到练习页面
        return redirect(url_for('practice'))

    # 如果是GET请求，显示配置页面
    word_labels = WordLabel.query.all()  # 从数据库获取所有标签
    print("Retrieved word labels:", word_labels)  # 添加打印语句
    return render_template('configure_practice.html', word_labels=word_labels)

@app.route('/practice')
@login_required
def practice():
    # get模式，从session或数据库获取用户设置
    practice_type = session.get('practice_type')
    #word_label_id = session.get('word_label_id')
    number_of_words = session.get('number_of_words', 10)

    # 根据设置从数据库中获取单词
    # 使用join来连接Word和WordLabel，然后根据WordLabel的id进行过滤
    words_query = Word.query.order_by(db.func.random()).limit(number_of_words)
   # 将Word对象转换为字典
    words = [word.to_dict() for word in words_query.all()]
    session['words'] = words
    # 渲染练习页面
    return render_template('practice.html', words=words, practice_type=practice_type)


@app.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    if request.method == 'POST':
        # 根据提交结果判断答题情况
        user_answers = {}
        for key, value in request.form.items():
            if key.startswith('answer-'):
                word_id = key.split('-')[1]  # 提取单词的ID
                user_answers[word_id] = value  # 将答案添加到字典中

        words = session.get('words')
        practice_type = session.get('practice_type')
        score = 0
        correct_count = 0
        incorrect_answers = {}

        if practice_type == "english_to_chinese":
            correct_answers = {str(item['id']): item['translation'] for item in words}
            for word_id, user_answer in user_answers.items():
                correct_answer = correct_answers.get(word_id)
                if user_answer in correct_answer:
                    score += 1
                    correct_count += 1
                else:
                    if word_id not in incorrect_answers:
                        incorrect_answers[word_id] = []
                    incorrect_answers[word_id].append(user_answer)

        elif practice_type == "chinese_to_english":
            correct_answers = {str(item['id']): item['word'] for item in words}
            for word_id, user_answer in user_answers.items():
                correct_answer = correct_answers.get(word_id)
                if user_answer.lower() == correct_answer.lower():
                    score += 1
                    correct_count += 1
                else:
                    if word_id not in incorrect_answers:
                        incorrect_answers[word_id] = []
                    incorrect_answers[word_id].append(user_answer)

        total_questions = len(words)
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        data = []
        for index, word in enumerate(words, start=1):
            word_id = str(word['id'])
            word_text = f"{word['word']} ({word['part_of_speech']})"
            user_answer = user_answers.get(word_id, '未回答')
            correct_answer = correct_answers.get(word_id, 'N/A')
            is_correct = user_answer in correct_answer if word_id in user_answers else False
            # 更新错题本
            mistake_entry = MistakeBook.query.filter_by(user_id=current_user.id, word_id=word['id']).first()
            if not mistake_entry:
                mistake_entry = MistakeBook(user_id=current_user.id, word_id=word['id'], incorrect_answers=0,
                                            correct_answers=0)
                db.session.add(mistake_entry)

            if is_correct:
                mistake_entry.correct_answers += 1
            else:
                mistake_entry.incorrect_answers += 1
            db.session.commit()
            # 在循环体内添加到data列表
            data.append({
                'index': index,
                'word_text': word_text,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'correct_count': mistake_entry.correct_answers,
                'incorrect_count': mistake_entry.incorrect_answers
            })

        return render_template('result.html', total_questions=total_questions, score=score, percentage=percentage,
                               correct_count=correct_count, data=data)


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

