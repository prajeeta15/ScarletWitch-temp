import datetime
import json
import pandas as pd
import torch
import os
import matplotlib.pyplot as plt
from transformers import XLMRobertaTokenizer, TrainingArguments, Trainer
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from backend.ai_model.xlm_roberta_model import XLMRobertaMPNet
from ai_model.mpnet_encoder import mpnet_encode

# Load dataset
df = pd.read_csv("large_darkweb_threat_dataset.csv")
df["label"] = df["final_score"].round().astype(int)

# Split data
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["synthetic_text"].tolist(), df["label"].tolist(), test_size=0.1, random_state=42
)

# Tokenizer
tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")


class ThreatDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(
            texts, truncation=True, padding=True, return_tensors="pt")
        self.labels = torch.tensor(labels)
        self.mpnet = mpnet_encode(texts)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        item["mpnet_emb"] = self.mpnet[idx]
        return item

    def __len__(self):
        return len(self.labels)


# Datasets
train_dataset = ThreatDataset(train_texts, train_labels)
val_dataset = ThreatDataset(val_texts, val_labels)

# Model
model = XLMRobertaMPNet(num_labels=11)

training_args = TrainingArguments(
    output_dir="./xlm_roberta_elmo_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=2
)


def custom_collator(features):
    batch = {
        "input_ids": torch.stack([f["input_ids"] for f in features]),
        "attention_mask": torch.stack([f["attention_mask"] for f in features]),
        "labels": torch.stack([f["labels"] for f in features]),
        "mpnet_emb": torch.stack([f["mpnet_emb"] for f in features])
    }
    return batch


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=custom_collator
)

trainer.train()
trainer.save_model("./xlm_roberta_elmo_model")
tokenizer.save_pretrained("./xlm_roberta_elmo_model")

# ===============================
# DAILY HIGH RISK LINK EXPORTER
# ===============================


SCRAPED_DATA_FILE = "backend/scraped_data.json"
EXPORT_FILE = f"backend/export/high_risk_links_{datetime.date.today()}.csv"

os.makedirs("backend/export", exist_ok=True)

try:
    with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    high_risk = df[df["score"] >= 8]  # Customize threshold

    high_risk[["url", "score", "topic", "timestamp"]].to_csv(
        EXPORT_FILE, index=False)
    print(f"✅ Exported high-risk links to: {EXPORT_FILE}")
except Exception as e:
    print(f"⚠️ Failed to export high-risk links: {e}")

# ===============================
# SCORING DASHBOARD (After 7 Days)
# ===============================

try:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)

    # Weekly score trend
    weekly = df.resample("D").mean(numeric_only=True)
    weekly[["score"]].plot(
        title="📊 Threat Score Trend (Daily Average)", figsize=(12, 6), color='red')
    plt.xlabel("Date")
    plt.ylabel("Average Threat Score")
    plt.grid()
    plt.tight_layout()
    plt.savefig("backend/export/threat_score_weekly.png")
    print("📈 Dashboard chart saved to backend/export/threat_score_weekly.png")
except Exception as e:
    print(f"⚠️ Dashboard generation failed: {e}")
