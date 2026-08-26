"""Catalog seed, part 4: depth for thinly-covered skills, plus extra
projects and assessments so every major track ends in something graded.

Same row format as ``catalog_core``.
"""

ROWS = """
go-102   | Building Microservices in Go               | Ardan Labs      | course     | 3 | 22 | mixed       | go-lang:0.6,distributed-systems:0.3,rest-api:0.25         | go-101           | 4.7 | 78000
rust-102 | Rust for Systems Programming               | Udemy           | course     | 3 | 24 | video       | rust:0.6,os-concepts:0.3,c-lang:0.2                       | rust-101         | 4.6 | 62000
rust-p01 | Project: Build a CLI Tool in Rust          | PathFinder Labs | project    | 2 | 14 | project     | rust:0.45,bash-shell:0.2,testing:0.2                      | rust-101         | 4.7 | 34000
comp-102 | Compiler Design                            | NPTEL           | course     | 3 | 30 | video       | compilers:0.7,discrete-math:0.25,algorithms:0.2           | math-107,c-101   | 4.5 | 140000
comp-p01 | Project: Write a Small Interpreter         | PathFinder Labs | project    | 3 | 22 | project     | compilers:0.5,python-advanced:0.3,testing:0.25            | comp-101         | 4.8 | 29000

clu-101  | Dimensionality Reduction: PCA, t-SNE, UMAP | PathFinder Labs | course     | 3 | 10 | mixed       | clustering:0.6,linear-algebra:0.35                        | ml-107           | 4.6 | 57000
ts-101   | Applied Time Series with Prophet & ARIMA   | Udemy           | course     | 2 | 16 | video       | time-series:0.65,statistics:0.3,data-analysis:0.2         | ml-108           | 4.5 | 96000
ts-p01   | Project: Demand Forecasting System         | PathFinder Labs | project    | 3 | 20 | project     | time-series:0.5,feature-eng:0.3,mlops:0.2                 | ts-101           | 4.7 | 31000
rec-101  | Building Recommender Systems in Python     | PathFinder Labs | course     | 2 | 16 | mixed       | recsys:0.6,ml-foundations:0.25,python-advanced:0.2        | ml-103           | 4.6 | 84000
rec-p01  | Project: Hybrid Recommendation Engine      | PathFinder Labs | project    | 3 | 22 | project     | recsys:0.55,feature-eng:0.3,model-eval:0.25               | rec-101          | 4.8 | 39000
rl-102   | Deep RL Hands-On                           | PathFinder Labs | course     | 3 | 26 | mixed       | reinforcement-learn:0.65,pytorch:0.35,deep-learning:0.25  | rl-101,dl-103    | 4.7 | 44000
tf-101   | TensorFlow: Advanced Techniques            | DeepLearning.AI | course     | 3 | 24 | video       | tensorflow:0.7,deep-learning:0.3,cnn:0.2                  | dl-104           | 4.7 | 130000
bd-101   | PySpark for Large-scale Data               | DataCamp        | course     | 2 | 18 | interactive | big-data:0.65,data-engineering:0.3,python-advanced:0.2    | de-101           | 4.6 | 145000
bd-102   | Distributed Data Processing Patterns       | PathFinder Labs | course     | 3 | 16 | reading     | big-data:0.5,distributed-systems:0.35                     | bd-101           | 4.5 | 38000
dbt-102  | Dimensional Modeling & Star Schemas        | PathFinder Labs | course     | 2 | 12 | reading     | dbt-modeling:0.6,db-design:0.35                           | sql-103          | 4.6 | 52000
excel-102| Advanced Excel: Power Query & DAX          | Microsoft Learn | course     | 2 | 12 | interactive | excel-sheets:0.65,bi-tools:0.3                            | excel-101        | 4.5 | 310000

ft-101   | Instruction Tuning & Dataset Curation      | PathFinder Labs | course     | 3 | 14 | mixed       | finetuning:0.6,llm-evaluation:0.3,data-cleaning:0.25      | gen-107          | 4.6 | 41000
diff-101 | Building with Diffusion Models             | PathFinder Labs | course     | 3 | 14 | mixed       | diffusion-models:0.6,pytorch:0.3,computer-vision:0.25     | gen-109          | 4.6 | 36000
gen-111  | Structured Output & Function Calling       | PathFinder Labs | course     | 2 |  8 | mixed       | agents:0.4,prompt-engineering:0.45,rest-api:0.2           | gen-102          | 4.7 | 74000
gen-a02  | Assessment: RAG System Design Review       | PathFinder Labs | assessment | 3 |  3 | mixed       | rag:0.3,vector-databases:0.25,system-design:0.2           | gen-p01          | 4.7 | 33000

next-102 | Next.js Performance & Caching              | PathFinder Labs | course     | 3 | 12 | mixed       | nextjs:0.6,web-performance:0.4                            | react-104        | 4.6 | 64000
vue-102  | SvelteKit in Production                    | PathFinder Labs | course     | 2 | 14 | mixed       | vue-svelte:0.65,web-performance:0.25                      | vue-101          | 4.5 | 42000
gql-102  | GraphQL Federation & Schema Design         | PathFinder Labs | course     | 3 | 12 | reading     | graphql:0.6,system-design:0.25,rest-api:0.2               | api-104          | 4.5 | 31000
ios-102  | Advanced SwiftUI & App Architecture        | PathFinder Labs | course     | 3 | 20 | video       | ios-dev:0.65,oop:0.25,testing:0.2                         | mob-103          | 4.6 | 58000
mob-a01  | Assessment: Mobile Development Check       | PathFinder Labs | assessment | 2 |  2 | interactive | android-dev:0.2,react-native:0.2,ios-dev:0.2              | mob-104          | 4.5 | 37000

iac-102  | Ansible & Configuration Management         | Red Hat         | course     | 2 | 14 | mixed       | iac:0.6,linux-admin:0.3                                   | lin-101          | 4.6 | 175000
csec-102 | Cloud Security Posture & Compliance        | PathFinder Labs | course     | 3 | 14 | mixed       | cloud-security:0.6,observability:0.25,security-basics:0.2 | sec-106          | 4.5 | 29000
for-102  | Malware Analysis Fundamentals              | PathFinder Labs | course     | 3 | 18 | mixed       | forensics:0.6,security-basics:0.25,os-concepts:0.2        | sec-107          | 4.6 | 34000
cloud-p01| Project: Multi-tier Cloud Deployment       | PathFinder Labs | project    | 3 | 24 | project     | aws:0.4,iac:0.35,cloud-architecture:0.35,observability:0.2| iac-101,aws-102  | 4.8 | 47000
cloud-a01| Assessment: Cloud Architecture Review      | PathFinder Labs | assessment | 3 |  3 | mixed       | cloud-architecture:0.3,aws:0.2                            | aws-102          | 4.7 | 41000

agile-102| Scrum Master in Practice                   | PathFinder Labs | course     | 2 | 10 | mixed       | agile-scrum:0.6,communication:0.3,product-thinking:0.2    | pm-102           | 4.5 | 88000
free-102 | Client Work & Pricing for Developers       | PathFinder Labs | course     | 2 |  8 | reading     | freelancing:0.6,communication:0.25                        | car-103          | 4.4 | 46000
ux-a01   | Assessment: Portfolio & Design Critique    | PathFinder Labs | assessment | 2 |  3 | mixed       | ui-design:0.25,ux-research:0.25,communication:0.2         | ux-103           | 4.6 | 39000
pm-a01   | Assessment: Product Case Study            | PathFinder Labs | assessment | 2 |  3 | mixed       | product-thinking:0.3,communication:0.25                    | pm-101           | 4.6 | 52000

qc-102   | Quantum Algorithms & Complexity            | PathFinder Labs | course     | 3 | 18 | video       | quantum-computing:0.6,linear-algebra:0.3,algorithms:0.2   | qc-101           | 4.5 | 27000
rob-102  | Motion Planning & SLAM                     | PathFinder Labs | course     | 3 | 22 | mixed       | robotics:0.6,linear-algebra:0.3,computer-vision:0.25      | rob-101          | 4.6 | 24000
arvr-102 | Immersive Interaction Design               | PathFinder Labs | course     | 3 | 16 | mixed       | ar-vr:0.6,ui-design:0.3,game-dev:0.2                      | arvr-101         | 4.4 | 21000
bc-p01   | Project: Deploy a Smart Contract dApp      | PathFinder Labs | project    | 3 | 20 | project     | blockchain:0.5,react:0.25,testing:0.2                     | bc-102           | 4.6 | 43000
iot-p01  | Project: Sensor-to-Cloud IoT Pipeline      | PathFinder Labs | project    | 2 | 18 | project     | iot-embedded:0.45,streaming-data:0.3,cloud-architecture:0.2| iot-101,aws-101 | 4.6 | 32000
game-p01 | Project: Ship a Playable Game Demo         | PathFinder Labs | project    | 2 | 24 | project     | game-dev:0.5,ui-design:0.2,testing:0.2                    | game-102         | 4.7 | 56000

int-a01  | Assessment: Full Mock Technical Interview  | PathFinder Labs | assessment | 3 |  4 | mixed       | interview-prep:0.35,dsa-advanced:0.25,communication:0.2   | car-101          | 4.8 | 112000
nlp-p01  | Project: Text Classification Service       | PathFinder Labs | project    | 2 | 18 | project     | nlp:0.45,mlops:0.25,model-eval:0.25                       | nlp-102          | 4.7 | 51000
cv-p01   | Project: Real-time Object Detection App    | PathFinder Labs | project    | 3 | 22 | project     | computer-vision:0.5,cnn:0.3,mlops:0.2                     | cv-102           | 4.7 | 44000
resp-a01 | Assessment: Model Fairness Audit           | PathFinder Labs | assessment | 3 |  3 | mixed       | responsible-ai:0.35,model-eval:0.25                       | ml-110           | 4.6 | 28000
sysd-p01 | Project: Design & Document a Scalable API  | PathFinder Labs | project    | 3 | 20 | project     | system-design:0.45,rest-api:0.3,tech-writing:0.25         | sysd-101,api-103 | 4.7 | 49000
"""
