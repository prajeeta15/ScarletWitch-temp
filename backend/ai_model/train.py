import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import re

# Load dataset


def load_dataset():
    try:
        df = pd.read_excel(
            "C:/Users/Prajeeta/Documents/GitHub/dark-web-intelligence/backend/data/darkweb_dataset.xlsx", sheet_name=0)

        # Drop unnecessary columns
        if "activity" in df.columns:
            # Drop 'activity' column explicitly
            df = df.drop(columns=["activity"])

        # Drop rows where "sub-activity" or "illicit score" is missing
        df = df.dropna(subset=["sub-activity", "illicit score"])

        # Ensure "illicit score" is numeric (integer)
        df["illicit score"] = pd.to_numeric(
            df["illicit score"], errors="coerce")
        df = df.dropna(subset=["illicit score"])
        df["illicit score"] = df["illicit score"].astype(int)

        # Normalize whitespace to single spaces in "sub-activity"
        df["sub-activity"] = df["sub-activity"].astype(
            str).apply(lambda x: re.sub(r"\s+", " ", x.strip()))

        # Rename columns for model compatibility
        df = df.rename(columns={"sub-activity": "text",
                       "illicit score": "label"})

        # Convert to Hugging Face dataset
        dataset = Dataset.from_pandas(df)
        return dataset
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        exit(1)  # Exit script if dataset loading fails


# Initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenization function


def tokenize_function(examples):
    encoding = tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        return_tensors="np",  # Ensure correct format
        add_special_tokens=True
    )
    encoding["label"] = examples["label"]  # Ensure labels are retained
    return encoding


# Load and preprocess dataset
dataset = load_dataset()
tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=[
                                "text"])  # Remove original text column

# Initialize model
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Train the model
try:
    trainer.train(resume_from_checkpoint=True)  # Resume if interrupted
    model.save_pretrained("./bert_darkweb_model")
    tokenizer.save_pretrained("./bert_darkweb_model")
    print("✅ Training complete! Model saved in ./bert_darkweb_model")
except Exception as e:
    print(f"❌ Error during training: {e}")
