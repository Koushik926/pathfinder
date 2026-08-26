"""Curated skill taxonomy for PathFinder.

Each skill has a stable id, a display name, a category and a short set of
aliases. Aliases matter: the goal parser matches free-text learner input
("I want to get into deep learning") against them before falling back to
embedding similarity.
"""

# (id, name, category, aliases)
SKILLS = [
    # --- Programming foundations -------------------------------------------
    ("python-basics",      "Python Fundamentals",        "Programming",  ["python", "python3", "scripting"]),
    ("python-advanced",    "Advanced Python",            "Programming",  ["decorators", "generators", "asyncio", "pythonic"]),
    ("javascript",         "JavaScript",                 "Programming",  ["js", "es6", "ecmascript", "vanilla js"]),
    ("typescript",         "TypeScript",                 "Programming",  ["ts", "typed javascript"]),
    ("java",               "Java",                       "Programming",  ["jvm", "core java"]),
    ("cpp",                "C++",                        "Programming",  ["c plus plus", "cpp", "competitive programming"]),
    ("c-lang",             "C Programming",              "Programming",  ["c language", "systems c"]),
    ("go-lang",            "Go",                         "Programming",  ["golang"]),
    ("rust",               "Rust",                       "Programming",  ["rustlang", "memory safety"]),
    ("sql",                "SQL",                        "Programming",  ["queries", "select", "joins", "rdbms queries"]),
    ("bash-shell",         "Shell & Bash",               "Programming",  ["terminal", "command line", "zsh", "cli"]),
    ("git",                "Git & Version Control",      "Programming",  ["github", "version control", "branching"]),
    ("oop",                "Object-Oriented Design",     "Programming",  ["oops", "classes", "inheritance", "solid"]),
    ("functional-prog",    "Functional Programming",     "Programming",  ["pure functions", "immutability", "map reduce"]),
    ("clean-code",         "Clean Code & Refactoring",   "Programming",  ["code quality", "refactor", "readable code"]),
    ("testing",            "Software Testing",           "Programming",  ["unit tests", "pytest", "jest", "tdd"]),
    ("debugging",          "Debugging & Profiling",      "Programming",  ["profiler", "breakpoints", "troubleshooting"]),

    # --- CS core ------------------------------------------------------------
    ("dsa-basics",         "Data Structures",            "CS Core",      ["arrays", "linked list", "stacks", "queues", "hashmap"]),
    ("algorithms",         "Algorithms",                 "CS Core",      ["sorting", "searching", "greedy", "complexity"]),
    ("dsa-advanced",       "Advanced Algorithms",        "CS Core",      ["dynamic programming", "graphs", "dp", "trees", "segment tree"]),
    ("os-concepts",        "Operating Systems",          "CS Core",      ["processes", "threads", "scheduling", "memory management"]),
    ("networking",         "Computer Networks",          "CS Core",      ["tcp", "http", "dns", "osi", "sockets"]),
    ("db-design",          "Database Design",            "CS Core",      ["normalisation", "er diagram", "schema design", "indexing"]),
    ("compilers",          "Compilers & Language Design","CS Core",      ["parsing", "lexer", "codegen", "interpreter"]),
    ("distributed-systems","Distributed Systems",        "CS Core",      ["consensus", "replication", "sharding", "cap theorem"]),
    ("system-design",      "System Design",              "CS Core",      ["hld", "lld", "scalability", "architecture interview"]),

    # --- Mathematics & statistics ------------------------------------------
    ("linear-algebra",     "Linear Algebra",             "Mathematics",  ["matrices", "vectors", "eigenvalues", "svd"]),
    ("calculus",           "Calculus",                   "Mathematics",  ["derivatives", "gradients", "integration"]),
    ("probability",        "Probability",                "Mathematics",  ["random variables", "distributions", "bayes"]),
    ("statistics",         "Statistics",                 "Mathematics",  ["hypothesis testing", "p value", "regression stats"]),
    ("optimization",       "Optimization",               "Mathematics",  ["gradient descent", "convex", "lagrange"]),
    ("discrete-math",      "Discrete Mathematics",       "Mathematics",  ["combinatorics", "graph theory", "logic", "proofs"]),

    # --- Data ---------------------------------------------------------------
    ("data-analysis",      "Data Analysis",              "Data",         ["pandas", "eda", "exploratory analysis", "numpy"]),
    ("data-viz",           "Data Visualization",         "Data",         ["matplotlib", "seaborn", "plotly", "charts"]),
    ("data-cleaning",      "Data Wrangling",             "Data",         ["cleaning", "missing values", "etl basics", "preprocessing"]),
    ("feature-eng",        "Feature Engineering",        "Data",         ["feature selection", "encoding", "scaling"]),
    ("bi-tools",           "BI & Dashboards",            "Data",         ["power bi", "tableau", "looker", "reporting"]),
    ("excel-sheets",       "Spreadsheet Analytics",      "Data",         ["excel", "google sheets", "pivot table"]),
    ("data-engineering",   "Data Engineering",           "Data",         ["etl", "elt", "pipelines", "data warehouse"]),
    ("big-data",           "Big Data Processing",        "Data",         ["spark", "hadoop", "pyspark", "mapreduce"]),
    ("streaming-data",     "Streaming Data",             "Data",         ["kafka", "real time pipeline", "flink"]),
    ("dbt-modeling",       "Analytics Engineering",      "Data",         ["dbt", "data modeling", "star schema"]),

    # --- Machine learning ---------------------------------------------------
    ("ml-foundations",     "ML Foundations",             "Machine Learning", ["machine learning", "supervised", "unsupervised", "ml basics"]),
    ("regression",         "Regression Models",          "Machine Learning", ["linear regression", "logistic regression"]),
    ("classification",     "Classification",             "Machine Learning", ["decision tree", "random forest", "svm", "knn"]),
    ("ensemble-methods",   "Ensemble Methods",           "Machine Learning", ["xgboost", "gradient boosting", "lightgbm", "bagging"]),
    ("clustering",         "Clustering & Dim. Reduction","Machine Learning", ["kmeans", "pca", "dbscan", "tsne"]),
    ("model-eval",         "Model Evaluation",           "Machine Learning", ["cross validation", "roc auc", "confusion matrix", "overfitting"]),
    ("recsys",             "Recommender Systems",        "Machine Learning", ["collaborative filtering", "matrix factorisation", "recommendation"]),
    ("time-series",        "Time Series Forecasting",    "Machine Learning", ["arima", "forecasting", "prophet", "seasonality"]),
    ("deep-learning",      "Deep Learning",              "Machine Learning", ["neural networks", "backpropagation", "dnn"]),
    ("pytorch",            "PyTorch",                    "Machine Learning", ["torch", "tensors"]),
    ("tensorflow",         "TensorFlow & Keras",         "Machine Learning", ["keras", "tf"]),
    ("cnn",                "Convolutional Networks",     "Machine Learning", ["cnn", "image classification", "resnet"]),
    ("rnn-seq",            "Sequence Models",            "Machine Learning", ["rnn", "lstm", "gru", "seq2seq"]),
    ("transformers",       "Transformers & Attention",   "Machine Learning", ["attention", "bert", "self attention"]),
    ("nlp",                "Natural Language Processing","Machine Learning", ["text mining", "tokenisation", "sentiment analysis"]),
    ("computer-vision",    "Computer Vision",            "Machine Learning", ["opencv", "object detection", "image processing", "yolo"]),
    ("reinforcement-learn","Reinforcement Learning",     "Machine Learning", ["q learning", "policy gradient", "rl", "bandits"]),
    ("mlops",              "MLOps",                      "Machine Learning", ["model deployment", "mlflow", "model monitoring", "experiment tracking"]),
    ("responsible-ai",     "Responsible AI",             "Machine Learning", ["fairness", "bias", "explainability", "ai ethics", "shap"]),

    # --- Generative AI ------------------------------------------------------
    ("llm-foundations",    "LLM Foundations",            "Generative AI", ["large language models", "gpt", "claude", "foundation models"]),
    ("prompt-engineering", "Prompt Engineering",         "Generative AI", ["prompting", "few shot", "chain of thought"]),
    ("rag",                "Retrieval-Augmented Gen.",   "Generative AI", ["rag", "vector search", "embeddings retrieval"]),
    ("vector-databases",   "Vector Databases",           "Generative AI", ["pinecone", "faiss", "chroma", "pgvector"]),
    ("agents",             "AI Agents & Tool Use",       "Generative AI", ["agentic", "function calling", "tool use", "langgraph"]),
    ("finetuning",         "Fine-tuning & PEFT",         "Generative AI", ["lora", "peft", "instruction tuning", "sft"]),
    ("llm-evaluation",     "LLM Evaluation",             "Generative AI", ["evals", "llm as judge", "hallucination testing"]),
    ("diffusion-models",   "Diffusion & Image Gen.",     "Generative AI", ["stable diffusion", "text to image", "gan"]),

    # --- Web development ----------------------------------------------------
    ("html-css",           "HTML & CSS",                 "Web",          ["markup", "stylesheets", "flexbox", "grid"]),
    ("responsive-design",  "Responsive Design",          "Web",          ["mobile first", "media queries", "tailwind"]),
    ("react",              "React",                      "Web",          ["reactjs", "hooks", "jsx", "components"]),
    ("nextjs",             "Next.js",                    "Web",          ["ssr", "app router", "react framework"]),
    ("vue-svelte",         "Vue & Svelte",               "Web",          ["vuejs", "sveltekit"]),
    ("state-management",   "Frontend State Management",  "Web",          ["redux", "zustand", "context api"]),
    ("web-performance",    "Web Performance",            "Web",          ["lighthouse", "core web vitals", "bundle size"]),
    ("accessibility",      "Web Accessibility",          "Web",          ["a11y", "wcag", "screen reader", "aria"]),
    ("node-backend",       "Node.js Backend",            "Web",          ["express", "nodejs", "nestjs"]),
    ("fastapi-backend",    "Python Web Backends",        "Web",          ["fastapi", "django", "flask"]),
    ("rest-api",           "REST API Design",            "Web",          ["api design", "endpoints", "openapi", "swagger"]),
    ("graphql",            "GraphQL",                    "Web",          ["apollo", "schema stitching"]),
    ("auth-security",      "Auth & AppSec",              "Web",          ["oauth", "jwt", "session", "authentication"]),
    ("websockets",         "Realtime & WebSockets",      "Web",          ["socket.io", "sse", "realtime"]),

    # --- Mobile -------------------------------------------------------------
    ("android-dev",        "Android Development",        "Mobile",       ["kotlin", "android studio", "jetpack compose"]),
    ("ios-dev",            "iOS Development",            "Mobile",       ["swift", "swiftui", "xcode"]),
    ("react-native",       "Cross-platform Mobile",      "Mobile",       ["react native", "flutter", "expo"]),

    # --- Cloud, infra & DevOps ---------------------------------------------
    ("linux-admin",        "Linux Administration",       "Cloud & DevOps", ["ubuntu", "systemd", "permissions", "server admin"]),
    ("docker",             "Containers & Docker",        "Cloud & DevOps", ["containerisation", "dockerfile", "compose"]),
    ("kubernetes",         "Kubernetes",                 "Cloud & DevOps", ["k8s", "helm", "pods", "orchestration"]),
    ("ci-cd",              "CI/CD",                      "Cloud & DevOps", ["github actions", "jenkins", "pipelines", "continuous delivery"]),
    ("iac",                "Infrastructure as Code",     "Cloud & DevOps", ["terraform", "ansible", "pulumi"]),
    ("aws",                "AWS",                        "Cloud & DevOps", ["amazon web services", "ec2", "s3", "lambda"]),
    ("azure-gcp",          "Azure & GCP",                "Cloud & DevOps", ["azure", "google cloud", "gcp"]),
    ("observability",      "Monitoring & Observability", "Cloud & DevOps", ["prometheus", "grafana", "logging", "tracing"]),
    ("cloud-architecture", "Cloud Architecture",         "Cloud & DevOps", ["well architected", "cloud native", "serverless design"]),

    # --- Security -----------------------------------------------------------
    ("security-basics",    "Security Fundamentals",      "Security",     ["cia triad", "threat model", "infosec"]),
    ("cryptography",       "Cryptography",               "Security",     ["encryption", "hashing", "tls", "pki"]),
    ("web-security",       "Web Application Security",   "Security",     ["owasp", "xss", "sql injection", "csrf"]),
    ("pentesting",         "Penetration Testing",        "Security",     ["ethical hacking", "kali", "burp suite", "red team"]),
    ("network-security",   "Network Security",           "Security",     ["firewall", "ids", "vpn", "packet analysis"]),
    ("cloud-security",     "Cloud Security",             "Security",     ["iam", "least privilege", "cspm"]),
    ("forensics",          "Digital Forensics",          "Security",     ["incident response", "malware analysis", "blue team"]),

    # --- Product, design & career ------------------------------------------
    ("ux-research",        "UX Research",                "Product & Design", ["user research", "interviews", "usability testing"]),
    ("ui-design",          "UI Design",                  "Product & Design", ["figma", "visual design", "design systems"]),
    ("product-thinking",   "Product Management",         "Product & Design", ["roadmap", "prioritisation", "prd", "product sense"]),
    ("agile-scrum",        "Agile & Scrum",              "Product & Design", ["sprint", "kanban", "standup", "jira"]),
    ("tech-writing",       "Technical Writing",          "Product & Design", ["documentation", "readme", "api docs"]),
    ("communication",      "Communication & Storytelling","Product & Design", ["presentation", "stakeholder", "public speaking"]),
    ("interview-prep",     "Interview Preparation",      "Career",       ["coding interview", "behavioural", "resume", "placement"]),
    ("freelancing",        "Freelancing & Portfolio",    "Career",       ["portfolio", "upwork", "personal brand"]),

    # --- Emerging -----------------------------------------------------------
    ("blockchain",         "Blockchain & Web3",          "Emerging",     ["solidity", "smart contracts", "ethereum", "web3"]),
    ("iot-embedded",       "IoT & Embedded Systems",     "Emerging",     ["arduino", "raspberry pi", "microcontroller", "esp32"]),
    ("quantum-computing",  "Quantum Computing",          "Emerging",     ["qiskit", "qubits", "quantum algorithms"]),
    ("game-dev",           "Game Development",           "Emerging",     ["unity", "unreal", "godot", "game engine"]),
    ("ar-vr",              "AR / VR",                    "Emerging",     ["augmented reality", "virtual reality", "xr", "metaverse"]),
    ("robotics",           "Robotics",                   "Emerging",     ["ros", "slam", "motion planning"]),
]
