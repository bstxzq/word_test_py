import numpy as np
from transformers import BertTokenizer, BertModel
import re

class AnswerChecker:
    def __init__(self, tokenizer_path, model_path):
        # 初始化分词器和模型
        try:
            self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
            self.model = BertModel.from_pretrained(model_path)
        except Exception as e:
            print(f"Error initializing tokenizer or model: {e}")
            raise

    def get_sentence_embedding(self, sentence):
        # 获取句子的向量表示
        inputs = self.tokenizer(sentence, return_tensors='pt')
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()

    def cosine_similarity(self, a, b):
        # 计算余弦相似度
        a = np.ravel(a)  # 将 a 展平
        b = np.ravel(b)  # 将 b 展平
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def check_answer(self, user_answer, correct_answers):
        # 检查答案
        # 根据空格、逗号、分号、句点、顿号进行分词，并去除空字符串
        correct_answers_list = [ans for ans in re.split(r'[ ,;.\u3001]', correct_answers) if ans]

        user_embedding = self.get_sentence_embedding(user_answer)
        max_similarity = 0
        for correct_answer in correct_answers_list:
            correct_embedding = self.get_sentence_embedding(correct_answer)
            semantic_similarity = self.cosine_similarity(user_embedding, correct_embedding)
            if semantic_similarity > max_similarity:
                max_similarity = semantic_similarity
        return max_similarity
