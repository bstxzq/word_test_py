# models.py
from flask_login import UserMixin
from word_test import db

# 多对多关系中间表
word_label_association = db.Table('word_label_association',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('word_labels.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    password_salt = db.Column(db.String(29), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class WordLabel(db.Model):
    __tablename__ = 'word_labels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    words = db.relationship('Word', secondary=word_label_association, back_populates='labels')

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    labels = db.relationship('WordLabel', secondary=word_label_association, back_populates='words')
    part_of_speech = db.Column(db.String(10), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'translation': self.translation,
            'part_of_speech': self.part_of_speech
            # 如果需要，可以添加更多字段
        }


class MistakeBook(db.Model):
    __tablename__ = 'mistake_books'  # 修改表名使其更符合命名规则
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    incorrect_answers = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
