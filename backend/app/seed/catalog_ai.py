"""Catalog seed, part 2: data, machine learning and generative AI.

Same row format as ``catalog_core``.
"""

ROWS = """
da-101   | Data Analysis with Python                  | freeCodeCamp    | course     | 1 | 20 | video       | data-analysis:0.6,python-basics:0.2                       | py-103           | 4.7 | 830000
da-102   | Pandas in Depth                            | Kaggle Learn    | course     | 1 | 10 | interactive | data-analysis:0.55,data-cleaning:0.3                      | da-101           | 4.8 | 690000
da-103   | Data Cleaning & Preprocessing              | Kaggle Learn    | course     | 2 | 12 | interactive | data-cleaning:0.7,feature-eng:0.25                        | da-102           | 4.7 | 410000
da-104   | Exploratory Data Analysis in Practice      | DataCamp        | course     | 2 | 14 | interactive | data-analysis:0.5,data-viz:0.4,statistics:0.25            | da-102           | 4.6 | 350000
da-105   | Data Visualization with Matplotlib/Seaborn | DataCamp        | course     | 1 | 12 | interactive | data-viz:0.7                                              | da-101           | 4.6 | 400000
da-106   | Storytelling with Data                     | Coursera        | course     | 2 | 10 | video       | data-viz:0.4,communication:0.5                            | da-105           | 4.7 | 280000
da-107   | Power BI for Business Analytics            | Microsoft Learn | course     | 1 | 16 | mixed       | bi-tools:0.7,data-viz:0.3                                 | excel-101        | 4.6 | 520000
da-108   | Tableau Desktop Essentials                 | Coursera        | course     | 1 | 14 | video       | bi-tools:0.65,data-viz:0.3                                | excel-101        | 4.5 | 340000
excel-101| Spreadsheets for Analysts                  | Microsoft Learn | course     | 1 |  8 | interactive | excel-sheets:0.7,data-analysis:0.15                       |                  | 4.4 | 600000
da-p01   | Project: End-to-End EDA on Public Data     | PathFinder Labs | project    | 2 | 14 | project     | data-analysis:0.45,data-viz:0.35,data-cleaning:0.3        | da-104           | 4.7 | 58000
da-p02   | Project: Build an Interactive BI Dashboard | PathFinder Labs | project    | 2 | 16 | project     | bi-tools:0.5,data-viz:0.4,communication:0.2               | da-107           | 4.6 | 34000
da-a01   | Assessment: Data Analyst Skills Audit      | PathFinder Labs | assessment | 2 |  2 | interactive | data-analysis:0.3,sql:0.25,data-viz:0.2                   | da-104,sql-102   | 4.6 | 87000

de-101   | Data Engineering Foundations               | Coursera        | course     | 2 | 22 | video       | data-engineering:0.65,sql:0.25                            | sql-102,py-104   | 4.6 | 300000
de-102   | Building ETL Pipelines with Airflow        | Udacity         | course     | 2 | 20 | mixed       | data-engineering:0.6,python-advanced:0.25                 | de-101           | 4.6 | 150000
de-103   | Analytics Engineering with dbt             | dbt Labs        | course     | 2 | 14 | interactive | dbt-modeling:0.7,sql:0.35,data-engineering:0.25           | sql-103          | 4.7 | 190000
de-104   | Big Data with Apache Spark                 | edX             | course     | 3 | 26 | video       | big-data:0.7,data-engineering:0.3,python-advanced:0.2     | de-101           | 4.5 | 210000
de-105   | Streaming Data with Kafka                  | Confluent       | course     | 3 | 18 | mixed       | streaming-data:0.7,distributed-systems:0.25               | de-102           | 4.6 | 130000
de-106   | Data Warehousing on the Cloud              | Google Cloud    | course     | 2 | 16 | mixed       | data-engineering:0.45,cloud-architecture:0.3,sql:0.2      | de-101           | 4.5 | 175000
de-p01   | Project: Batch + Streaming Pipeline         | PathFinder Labs | project    | 3 | 24 | project     | data-engineering:0.5,streaming-data:0.4,docker:0.25       | de-105           | 4.8 | 26000

ml-101   | Machine Learning Specialization            | DeepLearning.AI | course     | 1 | 40 | video       | ml-foundations:0.7,regression:0.5,classification:0.4      | py-103,math-101  | 4.9 | 1500000
ml-102   | Intro to Machine Learning                  | Kaggle Learn    | course     | 1 |  8 | interactive | ml-foundations:0.45,classification:0.3                    | da-102           | 4.7 | 780000
ml-103   | Supervised Learning with scikit-learn      | DataCamp        | course     | 2 | 16 | interactive | classification:0.55,regression:0.5,model-eval:0.35        | ml-102           | 4.6 | 420000
ml-104   | Feature Engineering for ML                 | Kaggle Learn    | course     | 2 | 10 | interactive | feature-eng:0.7,data-cleaning:0.3                         | ml-103           | 4.7 | 330000
ml-105   | Model Evaluation & Validation              | Udacity         | course     | 2 | 12 | mixed       | model-eval:0.75,statistics:0.25                           | ml-103           | 4.6 | 240000
ml-106   | Ensemble Methods & Gradient Boosting       | Kaggle Learn    | course     | 2 | 12 | interactive | ensemble-methods:0.75,classification:0.3,model-eval:0.25  | ml-105           | 4.8 | 310000
ml-107   | Unsupervised Learning & Clustering         | Coursera        | course     | 2 | 14 | video       | clustering:0.75,linear-algebra:0.25                       | ml-103           | 4.6 | 260000
ml-108   | Time Series Forecasting                    | Kaggle Learn    | course     | 2 | 12 | interactive | time-series:0.75,statistics:0.3                           | ml-103,math-105  | 4.6 | 200000
ml-109   | Recommender Systems                        | Coursera        | course     | 3 | 20 | video       | recsys:0.8,linear-algebra:0.3,ml-foundations:0.25         | ml-107           | 4.7 | 180000
ml-110   | Responsible AI & Model Explainability      | Google Cloud    | course     | 2 | 10 | mixed       | responsible-ai:0.75,model-eval:0.25                       | ml-105           | 4.7 | 165000
ml-p01   | Project: Predictive Model End-to-End       | PathFinder Labs | project    | 2 | 20 | project     | ml-foundations:0.4,feature-eng:0.35,model-eval:0.35       | ml-105           | 4.8 | 72000
ml-p02   | Project: Kaggle Competition Sprint         | Kaggle          | project    | 3 | 30 | project     | ensemble-methods:0.45,feature-eng:0.45,model-eval:0.35    | ml-106           | 4.8 | 145000
ml-a01   | Assessment: ML Fundamentals Quiz           | PathFinder Labs | assessment | 2 |  2 | interactive | ml-foundations:0.3,model-eval:0.25                        | ml-103           | 4.6 | 156000

dl-101   | Deep Learning Specialization               | DeepLearning.AI | course     | 2 | 50 | video       | deep-learning:0.75,cnn:0.4,rnn-seq:0.4,optimization:0.25  | ml-101,math-103  | 4.9 | 1100000
dl-102   | Practical Deep Learning for Coders          | fast.ai        | course     | 2 | 35 | video       | deep-learning:0.6,pytorch:0.45,cnn:0.35                   | ml-103           | 4.9 | 620000
dl-103   | PyTorch Fundamentals                       | Microsoft Learn | course     | 2 | 14 | interactive | pytorch:0.75,deep-learning:0.3                            | ml-103           | 4.7 | 380000
dl-104   | TensorFlow Developer Certificate Prep      | DeepLearning.AI | course     | 2 | 28 | video       | tensorflow:0.75,deep-learning:0.35,cnn:0.3                | ml-103           | 4.7 | 340000
dl-105   | Convolutional Neural Networks              | DeepLearning.AI | course     | 3 | 22 | video       | cnn:0.8,computer-vision:0.4,deep-learning:0.3             | dl-101           | 4.9 | 420000
dl-106   | Sequence Models                            | DeepLearning.AI | course     | 3 | 22 | video       | rnn-seq:0.8,nlp:0.35,deep-learning:0.3                    | dl-101           | 4.8 | 380000
dl-107   | Attention & Transformers from Scratch      | Karpathy        | course     | 3 | 18 | video       | transformers:0.8,pytorch:0.4,deep-learning:0.3            | dl-103,dl-106    | 4.9 | 290000
dl-a01   | Assessment: Deep Learning Concepts         | PathFinder Labs | assessment | 3 |  2 | interactive | deep-learning:0.3,cnn:0.2,rnn-seq:0.2                     | dl-101           | 4.7 | 71000

nlp-101  | Natural Language Processing Specialization | DeepLearning.AI | course     | 2 | 40 | video       | nlp:0.75,rnn-seq:0.35,transformers:0.3                    | dl-101           | 4.7 | 320000
nlp-102  | NLP with spaCy & Classical Methods         | spaCy           | course     | 2 | 10 | interactive | nlp:0.5,data-cleaning:0.2                                 | py-104           | 4.6 | 210000
nlp-103  | Hugging Face Transformers Course           | Hugging Face    | course     | 2 | 20 | interactive | transformers:0.65,nlp:0.45,pytorch:0.3                    | dl-103           | 4.8 | 450000
cv-101   | Computer Vision with OpenCV                | PyImageSearch   | course     | 2 | 18 | mixed       | computer-vision:0.7,python-advanced:0.2                    | py-104           | 4.6 | 230000
cv-102   | Object Detection & Segmentation            | Coursera        | course     | 3 | 22 | video       | computer-vision:0.6,cnn:0.45,deep-learning:0.25           | dl-105           | 4.7 | 170000
rl-101   | Reinforcement Learning Specialization      | Alberta/Coursera| course     | 3 | 40 | video       | reinforcement-learn:0.8,probability:0.3,optimization:0.25 | ml-101,math-104  | 4.7 | 190000

mlops-101| MLOps Fundamentals                          | DeepLearning.AI | course     | 2 | 20 | video       | mlops:0.7,ml-foundations:0.2                              | ml-105           | 4.7 | 260000
mlops-102| Experiment Tracking with MLflow            | PathFinder Labs | course     | 2 | 10 | mixed       | mlops:0.55,testing:0.2                                    | mlops-101        | 4.5 | 68000
mlops-103| Deploying ML Models with Docker & FastAPI  | Udemy           | course     | 2 | 16 | mixed       | mlops:0.5,docker:0.4,fastapi-backend:0.35,rest-api:0.25   | mlops-101,py-104 | 4.7 | 195000
mlops-104| Model Monitoring & Drift Detection         | Evidently AI    | course     | 3 | 12 | mixed       | mlops:0.6,observability:0.3,model-eval:0.25               | mlops-103        | 4.6 | 54000
mlops-p01| Project: Ship an ML Service to Production  | PathFinder Labs | project    | 3 | 26 | project     | mlops:0.5,docker:0.35,ci-cd:0.3,rest-api:0.25             | mlops-103        | 4.8 | 41000

gen-101  | Generative AI for Everyone                 | DeepLearning.AI | course     | 1 |  8 | video       | llm-foundations:0.5,prompt-engineering:0.3                |                  | 4.8 | 720000
gen-102  | Prompt Engineering for Developers          | DeepLearning.AI | course     | 1 |  6 | interactive | prompt-engineering:0.7,llm-foundations:0.25               | gen-101          | 4.8 | 680000
gen-103  | How LLMs Actually Work                     | Karpathy        | course     | 2 | 10 | video       | llm-foundations:0.7,transformers:0.4                      | gen-101          | 4.9 | 540000
gen-104  | Building RAG Applications                  | LangChain       | course     | 2 | 14 | mixed       | rag:0.7,vector-databases:0.45,llm-foundations:0.25        | gen-102,py-104   | 4.7 | 310000
gen-105  | Vector Databases & Semantic Search         | Pinecone        | course     | 2 | 10 | mixed       | vector-databases:0.7,rag:0.35                             | gen-102          | 4.6 | 185000
gen-106  | Building AI Agents with Tool Use           | DeepLearning.AI | course     | 3 | 16 | mixed       | agents:0.75,prompt-engineering:0.3,rest-api:0.25          | gen-104          | 4.8 | 260000
gen-107  | Fine-tuning LLMs with LoRA & PEFT          | Hugging Face    | course     | 3 | 18 | mixed       | finetuning:0.8,transformers:0.35,pytorch:0.3              | nlp-103          | 4.7 | 175000
gen-108  | Evaluating LLM Applications                | DeepLearning.AI | course     | 3 | 10 | mixed       | llm-evaluation:0.75,responsible-ai:0.3,model-eval:0.25    | gen-104          | 4.7 | 130000
gen-109  | Diffusion Models & Image Generation        | Hugging Face    | course     | 3 | 16 | mixed       | diffusion-models:0.75,deep-learning:0.3,pytorch:0.25      | dl-103           | 4.7 | 145000
gen-110  | LLM Safety, Guardrails & Red-teaming       | PathFinder Labs | course     | 3 | 10 | mixed       | responsible-ai:0.55,llm-evaluation:0.35,security-basics:0.2| gen-108         | 4.6 | 48000
gen-p01  | Project: Build a RAG Chatbot over Your Docs| PathFinder Labs | project    | 2 | 20 | project     | rag:0.5,vector-databases:0.35,fastapi-backend:0.25        | gen-104          | 4.8 | 96000
gen-p02  | Project: Multi-tool AI Agent               | PathFinder Labs | project    | 3 | 24 | project     | agents:0.55,rest-api:0.3,testing:0.2                      | gen-106          | 4.8 | 63000
gen-a01  | Assessment: GenAI Practitioner Check       | PathFinder Labs | assessment | 2 |  2 | interactive | llm-foundations:0.3,prompt-engineering:0.25,rag:0.2       | gen-104          | 4.7 | 88000
"""
