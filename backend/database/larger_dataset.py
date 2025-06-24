import pandas as pd
import random

topic_map = {
    "Hacking": ["account takeover", "phishing", "data breach", "credential stuffing", "zero-day exploit"],
    "Drugs": ["marijuana", "lsd", "cocaine", "ecstasy", "opioids"],
    "Financial Fraud": ["credit card dump", "paypal fraud", "crypto wallet theft", "skimming", "fake bank sites"],
    "Weapons": ["firearms", "explosives", "knives", "ammo smuggling"],
    "Malware/Ransomware": ["ransomware", "trojans", "keyloggers", "stealer malware", "botnets"],
    "Other": ["fake ids", "child exploitation", "spy tools", "illegal porn"]
}

templates = [
    "Found a dark web post discussing {sub} related to {act}.",
    "User offering services for {sub} under the {act} category.",
    "Detected conversation about {sub} in a {act} section of a darknet forum.",
    "Marketplace listing indicates {sub} activities categorized under {act}.",
    "Onion domain hosted a thread on {sub} within the {act} community."
]

rows = []
random.seed(42)
for _ in range(3000):
    topic = random.choice(list(topic_map.keys()))
    sub = random.choice(topic_map[topic])
    act = topic
    text = random.choice(templates).format(sub=sub, act=act)

    true_score = round(random.uniform(2, 10), 2)
    bert_score = round(true_score + random.uniform(-1, 1), 2)
    gpt_score = round((bert_score + true_score) / 2 +
                      random.uniform(-0.5, 0.5), 2)
    final_score = round((gpt_score + random.uniform(-0.3, 0.3)), 2)
    final_score = max(0, min(10, final_score))

    rows.append({
        "activity": act,
        "sub-activity": sub,
        "synthetic_text": text,
        "illicit_score": true_score,
        "topic": topic,
        "bert_score": bert_score,
        "gpt_score": gpt_score,
        "final_score": final_score
    })

df = pd.DataFrame(rows)
df.to_csv("large_darkweb_threat_dataset.csv", index=False)
print("✅ File saved as 'large_darkweb_threat_dataset.csv'")
