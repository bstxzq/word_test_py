from transformers import BertTokenizer, BertModel
from transformers import MarianMTModel, MarianTokenizer, GenerationConfig

# 模型和分词器的名称
model_name = 'bert-base-chinese'
# 下载并保存分词器
tokenizer = BertTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained('./bert-base-chinese-tokenizer')
# 下载并保存BertModel模型
model = BertModel.from_pretrained(model_name)
model.save_pretrained('./bert-base-chinese-model')

# 下载并保存arianMTModel模型和tokenizer
model_name = "Helsinki-NLP/opus-mt-en-zh"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)
model.save_pretrained('./local_marian_en_zh')
tokenizer.save_pretrained('./local_marian_en_zh')

# 创建或更新 GenerationConfig 文件
generation_config = GenerationConfig(
    max_length=512,
    num_beams=4,
    bad_words_ids=[[tokenizer.pad_token_id]],
    forced_eos_token_id=tokenizer.eos_token_id,
)
generation_config.save_pretrained('./local_marian_en_zh')