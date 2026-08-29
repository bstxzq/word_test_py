# word_test_py

基于 Flask 的**单词练习 Web 应用**（中文场景）。用户在浏览器中做单词/翻译练习，系统利用 BERT 中文词向量、MarianMT 英译中模型以及 Levenshtein / RapidFuzz 模糊匹配来判定答案，并记录错题、练习配置等。

## 功能特性

- 用户登录与会话管理（Flask-Login + SQLAlchemy）
- 单词练习（拼写 / 翻译）
- 答案模糊匹配校对（rapidfuzz / Levenshtein）
- 错题本（mistakes）记录与回顾
- 练习参数配置（configure_practice）
- 练习结果展示（result）

## 技术栈

| 类别 | 技术 |
| --- | --- |
| Web 框架 | Flask 3.0.3 |
| 数据库 / ORM | SQLAlchemy 2.0 + Flask-Migrate (Alembic) |
| 认证 | Flask-Login |
| 中文语义 | transformers (`bert-base-chinese`) |
| 翻译 | transformers (`Helsinki-NLP/opus-mt-en-zh`, MarianMT) |
| 模糊匹配 | rapidfuzz / python-Levenshtein |
| 运行入口 | `run.py`（监听 `127.0.0.1:5000`） |

## 目录结构

```
word_test_py/
├── run.py                 # 启动入口，本地 5000 端口
├── model_download.py      # 下载并缓存 BERT / MarianMT 模型
├── requirements.txt       # 依赖清单
├── .gitignore
├── AnswerChecker/         # 答案校对模块
└── word_test/             # Flask 应用包
    ├── __init__.py        # app 工厂
    ├── models.py          # 数据模型
    ├── routes.py          # 路由
    └── templates/         # 页面模板
        ├── home.html
        ├── login.html
        ├── practice.html
        ├── configure_practice.html
        ├── mistakes.html
        └── result.html
```

## 安装

```bash
git clone https://github.com/bstxzq/word_test_py.git
cd word_test_py
python -m venv .venv && source .venv/bin/activate   # 可选
pip install -r requirements.txt
```

> 依赖较多（含 `torch`、`transformers`），建议使用 Python 3.10+ 的虚拟环境。

## 准备模型

`model_download.py` 会下载并缓存以下模型到本地目录：

- `./bert-base-chinese-model` 与 `./bert-base-chinese-tokenizer`（BERT 中文）
- `./local_marian_en_zh`（MarianMT 英译中，含 `GenerationConfig`）

```bash
python model_download.py
```

## 运行

```bash
python run.py
# 浏览器打开 http://127.0.0.1:5000
```

## 注意事项

- 仓库已忽略 `.idea/`、`instance/`（数据库）、`words.csv`、模型目录等本地文件。
- 首次运行如需初始化数据库，可结合 Flask-Migrate（`flask db`）完成迁移。
- 本仓库原为个人练习项目，提交信息与文档较简略，欢迎按需补充。
