from transformers import XLMRobertaTokenizer
import torch
from ai_model.mpnet_encoder import mpnet_encode
from backend.ai_model.xlm_roberta_model import XLMRobertaMPNet

tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
model = XLMRobertaMPNet(num_labels=11)
model.load_state_dict(torch.load("./xlm_roberta_elmo_model/pytorch_model.bin"))
model.eval()


def predict_threat_level(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    mpnet_vec = mpnet_encode([text])[0].unsqueeze(0)

    with torch.no_grad():
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            mpnet_emb=mpnet_vec
        )
        logits = outputs["logits"]
        return int(torch.argmax(logits, dim=1))
