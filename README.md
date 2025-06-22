# ScarletWitch - writing research paper on it. still working. 
Monitors dark web marketplaces for illicit activities and logs data while predicting for threats real-time



Copyright © 2025 Prajeeta Pal
All rights reserved.

This project and its contents are the exclusive property of Prajeeta Pal. Unauthorized copying, modification, distribution, or use of this software, in whole or in part, is strictly prohibited without explicit written permission from the owner.

This software is provided “as is,” without warranty of any kind, express or implied. The owner is not responsible for any misuse or legal consequences resulting from the use of this project.

For inquiries or licensing requests, contact: prajeetaacm@gmail.com

# Dark Web Threat Intelligence

## 📌 Project Overview
# currently writing a research paper for this.
ScarletWitch is an advanced system designed for real-time scraping, threat analysis, and classification of dark web content. The system leverages **web scraping, machine learning (NLP), and the Tor network** to detect and analyze potential cyber threats. The goal is to assist law enforcement agencies, cybersecurity professionals, and researchers in identifying malicious activities on the dark web.

# building on BlackWidow - check doc for research insights

## 🚀 Features
- **Real-time Web Scraping**: Scrapes content from `.onion` websites using the Tor network.
- **Threat Level Prediction**: Uses an **NLP-based deep learning model** (BERT) to classify content and assign threat levels (0-10).
- **Secure Networking**: Integrates **Tor proxy** for anonymous access.
- **Automated Data Storage**: Saves scraped content and threat scores in a structured database.
- **Scalable API**: Provides real-time threat analysis via a RESTful API.

## 🛠️ Technologies Used
- **Programming Language**: Python
- **Machine Learning Model**: using ElMo and GPT4 
- **Libraries & Frameworks**:
  - `requests`, `BeautifulSoup` (for web scraping)
  - `torch`, `transformers` (for NLP and model inference)
  - `stem` (for Tor network integration)
  - `Flask` (for API development)
  - `SQLite/PostgreSQL` (for data storage)
- **Networking**: Tor proxy (SOCKS5)

## 📂 Project Structure
```
📦 dark-web-intelligence
├── backend
│   ├── scraping
│   │   ├── scraper.py          # Web scraping script
│   │   ├── scraper_utils.py    # Helper functions for scraping
│   ├── ai_model
│   │   ├── train.py            # Model training script
│   │   ├── predict.py          # Threat level prediction script
│   ├── api
│   │   ├── app.py              # Flask API server
│   │   ├── routes.py           # API routes
│   ├── database
│   │   ├── db_setup.py         # Database initialization
│   │   ├── db_operations.py    # CRUD operations
├── config
│   ├── settings.json           # Configuration file
├── README.md                   # Project documentation
```

## ⚙️ Usage
- The **scraper** extracts dark web content and stores it in the database.
- The **API** provides an endpoint to query stored data and receive **real-time threat analysis**.
- **Threat scores** range from **0 (Safe) to 10 (High Risk)**.

![Screenshot 2025-03-05 103932](https://github.com/user-attachments/assets/6ad5ab4d-9edc-4f0c-9807-6a1b7044f911)
![Screenshot 2025-03-03 202936](https://github.com/user-attachments/assets/18b2f7bf-63f5-4dca-af27-0d3c93b79ff9)
![Screenshot 2025-03-03 212325](https://github.com/user-attachments/assets/6af3283d-546e-441e-ba05-63238e1b7890)
![Screenshot 2025-03-03 222434](https://github.com/user-attachments/assets/10718fd5-fd14-4a69-8394-67dbdd201af4)
![Screenshot 2025-03-03 222147](https://github.com/user-attachments/assets/4d82731c-d330-4ef8-a52f-cdb079a1599b)

## 🔥 Challenges & Solutions
| Challenge | Solution |
|-----------|----------|
| Website access restrictions | Implemented **user-agent rotation** and **delays** to avoid detection |
| Tor network latency | Optimized request handling and multi-threading |
| Threat level accuracy | Enhanced model training with **larger labeled datasets** |
| Real-time analysis | Integrated a **Flask-based API** for real-time query processing |

## 📌 Future Enhancements
- **Integration with Law Enforcement Systems** for real-time alerts.
- **Advanced Deep Learning Models** (e.g., GPT-based threat detection).
- **Expanded Dark Web Coverage** by scraping more hidden services.

## Doc for research highlighting points of difference and enhancements
  [analysis.docx](https://github.com/user-attachments/files/20514366/analysis.docx)


## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

