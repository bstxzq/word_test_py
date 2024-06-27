from transformers import BertTokenizer, BertModel

# 模型和分词器的名称
model_name = 'bert-base-chinese'

# 下载并保存分词器
tokenizer = BertTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained('./bert-base-chinese-tokenizer')

# 下载并保存模型
model = BertModel.from_pretrained(model_name)
model.save_pretrained('./bert-base-chinese-model')
