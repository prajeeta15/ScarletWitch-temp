import torch
from torch import nn
from transformers import XLMRobertaModel


class XLMRobertaMPNet(nn.Module):
    def __init__(self, num_labels=11):
        super().__init__()
        self.xlm = XLMRobertaModel.from_pretrained("xlm-roberta-base")
        self.mpnet_fc = nn.Linear(768, self.xlm.config.hidden_size)
        self.classifier = nn.Linear(
            self.xlm.config.hidden_size * 2, num_labels)

    def forward(self, input_ids, attention_mask, mpnet_emb=None, labels=None):
        xlm_out = self.xlm(input_ids=input_ids,
                           attention_mask=attention_mask).pooler_output
        if mpnet_emb is not None:
            mpnet_proj = torch.relu(self.mpnet_fc(mpnet_emb))
            combined = torch.cat([xlm_out, mpnet_proj], dim=1)
        else:
            combined = xlm_out

        logits = self.classifier(combined)
        loss = None
        if labels is not None:
            loss = nn.CrossEntropyLoss()(logits, labels)
        return {"loss": loss, "logits": logits}
