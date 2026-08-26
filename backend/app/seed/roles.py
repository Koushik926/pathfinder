"""Career goal profiles.

A role is a *target* skill vector: the skills a competent practitioner is
expected to hold, and how central each is to the job (importance in [0,1]).
The gap engine subtracts a learner's mastery vector from this target, so
importance directly drives what gets recommended first.

``aliases`` feed the goal parser: free-text like "I want to become a data
scientist" or "switch into cloud" resolves to a role before any embedding
similarity is attempted.
"""

# (id, title, family, aliases, {skill_id: importance})
ROLES = [
    ("data-scientist", "Data Scientist", "Data & AI",
     ["data science", "data scientist", "ds role", "analytics scientist"],
     {"python-basics": 0.9, "data-analysis": 0.95, "data-cleaning": 0.85, "data-viz": 0.8,
      "sql": 0.85, "statistics": 0.9, "probability": 0.75, "linear-algebra": 0.6,
      "ml-foundations": 0.95, "regression": 0.8, "classification": 0.8, "model-eval": 0.85,
      "feature-eng": 0.8, "ensemble-methods": 0.6, "clustering": 0.55, "communication": 0.65,
      "responsible-ai": 0.45}),

    ("ml-engineer", "Machine Learning Engineer", "Data & AI",
     ["ml engineer", "machine learning engineer", "mle", "ai engineer", "ai engineer", "work in ai"],
     {"python-basics": 0.9, "python-advanced": 0.7, "ml-foundations": 0.9, "deep-learning": 0.8,
      "pytorch": 0.7, "model-eval": 0.8, "feature-eng": 0.7, "mlops": 0.9, "docker": 0.75,
      "rest-api": 0.65, "ci-cd": 0.6, "sql": 0.6, "linear-algebra": 0.6, "testing": 0.6,
      "cloud-architecture": 0.55, "system-design": 0.5}),

    ("data-analyst", "Data Analyst", "Data & AI",
     ["data analyst", "business analyst", "analytics", "reporting analyst"],
     {"sql": 0.95, "data-analysis": 0.9, "data-viz": 0.9, "data-cleaning": 0.8,
      "bi-tools": 0.85, "excel-sheets": 0.7, "statistics": 0.7, "communication": 0.8,
      "python-basics": 0.55, "product-thinking": 0.4}),

    ("data-engineer", "Data Engineer", "Data & AI",
     ["data engineer", "etl developer", "pipeline engineer", "analytics engineer"],
     {"sql": 0.9, "python-basics": 0.8, "python-advanced": 0.6, "data-engineering": 0.95,
      "db-design": 0.8, "big-data": 0.75, "streaming-data": 0.65, "dbt-modeling": 0.6,
      "docker": 0.7, "cloud-architecture": 0.7, "linux-admin": 0.55, "ci-cd": 0.55,
      "distributed-systems": 0.5}),

    ("genai-engineer", "Generative AI Engineer", "Data & AI",
     ["genai", "gen ai engineer", "llm engineer", "ai application developer", "llm developer", "build chatbots", "ai apps", "work with llms"],
     {"python-basics": 0.85, "python-advanced": 0.65, "llm-foundations": 0.9,
      "prompt-engineering": 0.85, "rag": 0.9, "vector-databases": 0.75, "agents": 0.8,
      "llm-evaluation": 0.7, "finetuning": 0.55, "transformers": 0.6, "rest-api": 0.7,
      "fastapi-backend": 0.6, "responsible-ai": 0.6, "docker": 0.5}),

    ("nlp-engineer", "NLP Engineer", "Data & AI",
     ["nlp engineer", "computational linguist", "text mining", "language ai"],
     {"python-basics": 0.85, "nlp": 0.95, "transformers": 0.8, "deep-learning": 0.75,
      "pytorch": 0.7, "rnn-seq": 0.6, "model-eval": 0.7, "mlops": 0.55, "linear-algebra": 0.5,
      "data-cleaning": 0.6}),

    ("cv-engineer", "Computer Vision Engineer", "Data & AI",
     ["computer vision engineer", "cv engineer", "image processing", "vision ai"],
     {"python-basics": 0.85, "computer-vision": 0.95, "cnn": 0.85, "deep-learning": 0.8,
      "pytorch": 0.7, "linear-algebra": 0.55, "model-eval": 0.65, "mlops": 0.55,
      "data-cleaning": 0.5}),

    ("frontend-dev", "Frontend Developer", "Engineering",
     ["frontend", "front end developer", "ui developer", "react developer", "make websites", "build websites", "web design"],
     {"html-css": 0.9, "javascript": 0.95, "typescript": 0.7, "react": 0.9,
      "responsive-design": 0.85, "state-management": 0.7, "accessibility": 0.65,
      "web-performance": 0.65, "testing": 0.6, "git": 0.8, "rest-api": 0.6, "ui-design": 0.5}),

    ("backend-dev", "Backend Developer", "Engineering",
     ["backend", "back end developer", "api developer", "server side"],
     {"python-basics": 0.7, "rest-api": 0.95, "db-design": 0.85, "sql": 0.85,
      "auth-security": 0.75, "testing": 0.75, "docker": 0.7, "system-design": 0.7,
      "git": 0.8, "networking": 0.55, "node-backend": 0.5, "fastapi-backend": 0.6,
      "clean-code": 0.6, "observability": 0.5}),

    ("fullstack-dev", "Full-stack Developer", "Engineering",
     ["full stack", "fullstack developer", "web developer", "mern"],
     {"html-css": 0.8, "javascript": 0.9, "typescript": 0.65, "react": 0.85,
      "node-backend": 0.75, "rest-api": 0.8, "sql": 0.7, "db-design": 0.65,
      "auth-security": 0.6, "git": 0.8, "docker": 0.55, "testing": 0.6,
      "responsive-design": 0.7, "ci-cd": 0.5}),

    ("mobile-dev", "Mobile App Developer", "Engineering",
     ["mobile developer", "android developer", "ios developer", "app developer", "flutter"],
     {"react-native": 0.7, "android-dev": 0.65, "ios-dev": 0.5, "ui-design": 0.6,
      "rest-api": 0.7, "git": 0.75, "testing": 0.55, "oop": 0.6, "ci-cd": 0.45,
      "responsive-design": 0.5}),

    ("devops-engineer", "DevOps Engineer", "Infrastructure",
     ["devops", "sre", "platform engineer", "site reliability"],
     {"linux-admin": 0.9, "bash-shell": 0.85, "docker": 0.95, "kubernetes": 0.85,
      "ci-cd": 0.9, "iac": 0.8, "aws": 0.75, "observability": 0.8, "networking": 0.65,
      "git": 0.8, "cloud-architecture": 0.7, "security-basics": 0.55}),

    ("cloud-architect", "Cloud Architect", "Infrastructure",
     ["cloud architect", "solutions architect", "cloud engineer", "aws architect"],
     {"aws": 0.9, "cloud-architecture": 0.95, "iac": 0.75, "kubernetes": 0.7,
      "networking": 0.75, "system-design": 0.8, "cloud-security": 0.75,
      "distributed-systems": 0.65, "observability": 0.65, "docker": 0.65,
      "communication": 0.6}),

    ("security-analyst", "Security Analyst", "Security",
     ["cybersecurity", "security analyst", "soc analyst", "infosec", "blue team"],
     {"security-basics": 0.95, "networking": 0.8, "network-security": 0.85,
      "web-security": 0.75, "linux-admin": 0.7, "forensics": 0.7, "cryptography": 0.6,
      "cloud-security": 0.6, "bash-shell": 0.6, "observability": 0.5}),

    ("pentester", "Penetration Tester", "Security",
     ["ethical hacker", "pentester", "red team", "offensive security", "bug bounty", "hacking", "hacker", "cyber security"],
     {"pentesting": 0.95, "web-security": 0.9, "networking": 0.75, "linux-admin": 0.8,
      "bash-shell": 0.7, "security-basics": 0.8, "cryptography": 0.55,
      "python-basics": 0.6, "network-security": 0.65}),

    ("sde-placement", "Software Engineer (Campus Placement)", "Engineering",
     ["placement", "campus placement", "sde", "software engineer", "crack interviews",
      "product company", "faang"],
     {"dsa-basics": 0.95, "algorithms": 0.9, "dsa-advanced": 0.85, "interview-prep": 0.9,
      "oop": 0.75, "system-design": 0.6, "sql": 0.6, "os-concepts": 0.6,
      "networking": 0.5, "db-design": 0.55, "git": 0.6, "communication": 0.55,
      "cpp": 0.4, "java": 0.4}),

    ("product-manager", "Product Manager", "Product & Design",
     ["product manager", "pm role", "associate product manager", "apm"],
     {"product-thinking": 0.95, "communication": 0.9, "agile-scrum": 0.8,
      "data-analysis": 0.65, "ux-research": 0.7, "statistics": 0.5, "tech-writing": 0.6,
      "sql": 0.5, "ui-design": 0.4}),

    ("ux-designer", "UX / Product Designer", "Product & Design",
     ["ux designer", "ui designer", "product designer", "interaction designer"],
     {"ux-research": 0.9, "ui-design": 0.95, "accessibility": 0.7, "responsive-design": 0.6,
      "communication": 0.75, "product-thinking": 0.6, "html-css": 0.4, "tech-writing": 0.45}),

    ("mlops-engineer", "MLOps Engineer", "Data & AI",
     ["mlops", "ml platform engineer", "ml infrastructure"],
     {"mlops": 0.95, "docker": 0.85, "kubernetes": 0.7, "ci-cd": 0.8, "python-advanced": 0.7,
      "ml-foundations": 0.7, "model-eval": 0.6, "observability": 0.75, "cloud-architecture": 0.7,
      "iac": 0.6, "testing": 0.65, "rest-api": 0.6}),

    ("game-developer", "Game Developer", "Emerging",
     ["game developer", "unity developer", "game programmer", "gamedev"],
     {"game-dev": 0.95, "cpp": 0.6, "oop": 0.75, "ui-design": 0.5, "linear-algebra": 0.5,
      "testing": 0.45, "git": 0.6, "ar-vr": 0.35}),

    ("blockchain-dev", "Blockchain Developer", "Emerging",
     ["blockchain developer", "web3 developer", "solidity developer", "smart contract"],
     {"blockchain": 0.95, "javascript": 0.7, "react": 0.5, "cryptography": 0.6,
      "testing": 0.6, "auth-security": 0.5, "rest-api": 0.45, "git": 0.6}),

    ("embedded-engineer", "Embedded / IoT Engineer", "Emerging",
     ["embedded engineer", "iot developer", "firmware", "hardware programming"],
     {"iot-embedded": 0.95, "c-lang": 0.85, "os-concepts": 0.6, "networking": 0.55,
      "python-basics": 0.5, "streaming-data": 0.35, "cloud-architecture": 0.35}),
]
