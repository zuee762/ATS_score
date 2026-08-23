"""Job Roles Taxonomy and Custom Job Description Parser.

Contains detailed profiles for 25+ industry standard roles with skill requirements,
domain keywords, action verbs, and certifications, plus dynamic extraction for custom JDs.
"""

from typing import Dict, List, Any, Optional
import re

JOB_ROLES: Dict[str, Dict[str, Any]] = {
    "fullstack_dev": {
        "id": "fullstack_dev",
        "title": "Full Stack Developer",
        "category": "Software Engineering",
        "description": "Designs, builds, and maintains both client-side and server-side web applications and scalable APIs.",
        "mandatory_skills": [
            "JavaScript", "TypeScript", "React", "Node.js", "HTML5", "CSS3", "REST APIs", "SQL", "Git"
        ],
        "secondary_skills": [
            "Next.js", "Vue.js", "Express.js", "PostgreSQL", "MongoDB", "Redis", "Docker", "GraphQL", "TailwindCSS", "AWS", "CI/CD"
        ],
        "domain_keywords": [
            "responsive design", "state management", "microservices", "API integration", "database schema",
            "unit testing", "server-side rendering", "web security", "caching", "JWT", "OAuth", "performance optimization"
        ],
        "action_verbs": [
            "Architected", "Engineered", "Developed", "Implemented", "Integrated", "Optimized", "Refactored", "Scaled", "Deployed"
        ],
        "certifications": ["AWS Certified Developer", "Meta Front-End/Back-End Developer", "Oracle Certified Associate"],
        "education_keywords": ["Computer Science", "Software Engineering", "Information Technology", "Computer Applications"]
    },
    "frontend_dev": {
        "id": "frontend_dev",
        "title": "Frontend Developer",
        "category": "Software Engineering",
        "description": "Crafts high-performance, accessible, and responsive user interfaces with modern frontend frameworks.",
        "mandatory_skills": [
            "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Git", "Responsive Design"
        ],
        "secondary_skills": [
            "Next.js", "Vue.js", "Angular", "TailwindCSS", "SASS", "Webpack", "Vite", "Jest", "Cypress", "Figma", "RESTful APIs"
        ],
        "domain_keywords": [
            "DOM manipulation", "component lifecycle", "accessibility", "WCAG", "single-page application",
            "cross-browser compatibility", "web vitals", "lighthouse", "animations", "state management", "UI/UX design systems"
        ],
        "action_verbs": [
            "Designed", "Built", "Revamped", "Created", "Enhanced", "Translated", "Integrated", "Accelerated", "Delivered"
        ],
        "certifications": ["Meta Front-End Developer", "Google UX Design", "W3Schools Certified Front-End"],
        "education_keywords": ["Computer Science", "Web Development", "Software Engineering", "Graphic Design"]
    },
    "backend_dev": {
        "id": "backend_dev",
        "title": "Backend Developer",
        "category": "Software Engineering",
        "description": "Develops robust server-side logic, database architectures, microservices, and high-throughput APIs.",
        "mandatory_skills": [
            "Python", "Java", "Node.js", "SQL", "REST APIs", "Git", "Data Structures", "Database Design"
        ],
        "secondary_skills": [
            "Go", "FastAPI", "Django", "Spring Boot", "Express.js", "PostgreSQL", "MySQL", "MongoDB",
            "Redis", "Kafka", "Docker", "Kubernetes", "AWS", "gRPC", "GraphQL"
        ],
        "domain_keywords": [
            "microservices", "distributed systems", "concurrency", "asynchronous processing", "database indexing",
            "caching strategies", "message queues", "system architecture", "load balancing", "rate limiting", "ORM"
        ],
        "action_verbs": [
            "Constructed", "Architected", "Optimized", "Scaled", "Automated", "Streamlined", "Engineered", "Maintained", "Refactored"
        ],
        "certifications": ["AWS Certified Solutions Architect", "Oracle Certified Java Developer", "Google Cloud Associate Engineer"],
        "education_keywords": ["Computer Science", "Information Systems", "Software Engineering"]
    },
    "ai_ml_engineer": {
        "id": "ai_ml_engineer",
        "title": "AI / Machine Learning Engineer",
        "category": "Data & AI",
        "description": "Designs, trains, fine-tunes, and deploys scalable machine learning and deep learning models into production.",
        "mandatory_skills": [
            "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn", "NumPy", "Pandas", "Git"
        ],
        "secondary_skills": [
            "HuggingFace", "Transformers", "LLMs", "NLP", "Computer Vision", "LangChain", "MLflow",
            "Docker", "Kubernetes", "FastAPI", "SQL", "ONNX", "CUDA", "Vector Databases", "RAG"
        ],
        "domain_keywords": [
            "model evaluation", "cross-validation", "feature engineering", "hyperparameter tuning",
            "gradient descent", "fine-tuning", "prompt engineering", "embeddings", "model latency", "inference pipeline", "data preprocessing"
        ],
        "action_verbs": [
            "Trained", "Fine-tuned", "Deployed", "Developed", "Pioneered", "Implemented", "Evaluated", "Optimized", "Formulated"
        ],
        "certifications": ["AWS Certified Machine Learning", "TensorFlow Developer Certificate", "DeepLearning.AI Specialization"],
        "education_keywords": ["Computer Science", "Artificial Intelligence", "Data Science", "Mathematics", "Statistics"]
    },
    "data_scientist": {
        "id": "data_scientist",
        "title": "Data Scientist",
        "category": "Data & AI",
        "description": "Extracts actionable insights from complex datasets using statistical modeling, hypothesis testing, and machine learning.",
        "mandatory_skills": [
            "Python", "R", "SQL", "Statistics", "Machine Learning", "Pandas", "NumPy", "Data Visualization", "Data Wrangling"
        ],
        "secondary_skills": [
            "Scikit-Learn", "Matplotlib", "Seaborn", "Tableau", "Power BI", "Spark", "Jupyter", "A/B Testing", "BigQuery", "Git"
        ],
        "domain_keywords": [
            "exploratory data analysis", "hypothesis testing", "regression analysis", "clustering", "time series forecasting",
            "predictive modeling", "statistical significance", "data cleaning", "feature selection", "business intelligence"
        ],
        "action_verbs": [
            "Analyzed", "Discovered", "Modeled", "Predicted", "Synthesized", "Formulated", "Quantified", "Extracted", "Visualized"
        ],
        "certifications": ["IBM Data Science Professional", "Google Data Analytics", "SAS Certified Data Scientist"],
        "education_keywords": ["Data Science", "Statistics", "Mathematics", "Economics", "Computer Science"]
    },
    "data_analyst": {
        "id": "data_analyst",
        "title": "Data Analyst",
        "category": "Data & AI",
        "description": "Transforms raw business data into actionable dashboards, KPIs, and statistical reports to drive strategic decisions.",
        "mandatory_skills": [
            "SQL", "Excel", "Tableau", "Power BI", "Python", "Data Visualization", "Business Analytics"
        ],
        "secondary_skills": [
            "R", "Pandas", "Looker", "PostgreSQL", "Google Analytics", "DAX", "ETL", "Statistics", "Snowflake"
        ],
        "domain_keywords": [
            "dashboard creation", "KPI tracking", "trend analysis", "data hygiene", "cohort analysis",
            "data aggregation", "stakeholder presentation", "ad-hoc reporting", "business metrics", "data storytelling"
        ],
        "action_verbs": [
            "Identified", "Reported", "Uncovered", "Dashboarded", "Queried", "Monitored", "Consolidated", "Interpreted", "Presented"
        ],
        "certifications": ["Microsoft Certified Data Analyst Associate", "Google Data Analytics Certificate", "Tableau Certified Desktop Specialist"],
        "education_keywords": ["Business Analytics", "Information Systems", "Statistics", "Economics", "Finance", "Computer Science"]
    },
    "data_engineer": {
        "id": "data_engineer",
        "title": "Data Engineer",
        "category": "Data & AI",
        "description": "Architects reliable data pipelines, data warehouses, and streaming infrastructure for analytics and ML systems.",
        "mandatory_skills": [
            "Python", "SQL", "ETL Pipelines", "Apache Spark", "Data Warehousing", "Git", "Linux"
        ],
        "secondary_skills": [
            "Kafka", "Airflow", "Snowflake", "Databricks", "AWS Redshift", "BigQuery", "PostgreSQL", "Docker", "dbt", "Hadoop"
        ],
        "domain_keywords": [
            "batch processing", "stream processing", "schema evolution", "data lakehouse", "data modeling",
            "pipeline orchestration", "data quality checks", "dimensional modeling", "query optimization", "distributed data"
        ],
        "action_verbs": [
            "Engineered", "Pipeline-built", "Automated", "Transformed", "Optimized", "Scaled", "Ingested", "Maintained", "Architected"
        ],
        "certifications": ["AWS Certified Data Analytics", "Databricks Certified Data Engineer", "Google Professional Data Engineer"],
        "education_keywords": ["Computer Science", "Information Engineering", "Database Systems", "Software Engineering"]
    },
    "devops_engineer": {
        "id": "devops_engineer",
        "title": "DevOps Engineer",
        "category": "Cloud & Infrastructure",
        "description": "Automates deployment pipelines, provisions cloud infrastructure as code, and ensures high availability and reliability.",
        "mandatory_skills": [
            "Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Git", "Bash", "Terraform"
        ],
        "secondary_skills": [
            "GitHub Actions", "Jenkins", "Ansible", "Helm", "Prometheus", "Grafana", "GCP", "Azure", "Python", "ArgoCD", "Networking"
        ],
        "domain_keywords": [
            "infrastructure as code", "container orchestration", "pipeline automation", "monitoring and alerting",
            "zero-downtime deployment", "load balancing", "cloud security", "secrets management", "disaster recovery", "scalability"
        ],
        "action_verbs": [
            "Automated", "Provisioned", "Orchestrated", "Containerized", "Streamlined", "Deployed", "Migrated", "Secured", "Standardized"
        ],
        "certifications": ["AWS Certified DevOps Engineer", "Certified Kubernetes Administrator (CKA)", "HashiCorp Certified: Terraform Associate"],
        "education_keywords": ["Computer Science", "Information Technology", "Cloud Computing", "Systems Engineering"]
    },
    "cloud_architect": {
        "id": "cloud_architect",
        "title": "Cloud Solutions Architect",
        "category": "Cloud & Infrastructure",
        "description": "Designs secure, scalable, multi-region cloud computing architectures and migration roadmaps for enterprise systems.",
        "mandatory_skills": [
            "AWS", "Cloud Architecture", "Terraform", "Docker", "Kubernetes", "Microservices", "Networking", "Security"
        ],
        "secondary_skills": [
            "Azure", "GCP", "Serverless", "Lambda", "Cost Optimization", "IAM", "VPC", "CI/CD", "Kafka", "Python"
        ],
        "domain_keywords": [
            "well-architected framework", "high availability", "fault tolerance", "disaster recovery",
            "cloud migration", "hybrid cloud", "cost governance", "multi-tenant architecture", "compliance", "zero trust"
        ],
        "action_verbs": [
            "Architected", "Spearheaded", "Designed", "Migrated", "Optimized", "Governed", "Evaluated", "Transformed", "Standardized"
        ],
        "certifications": ["AWS Solutions Architect Professional", "Google Cloud Professional Cloud Architect", "Azure Solutions Architect Expert"],
        "education_keywords": ["Computer Science", "Software Engineering", "Enterprise Architecture"]
    },
    "cybersecurity_analyst": {
        "id": "cybersecurity_analyst",
        "title": "Cybersecurity / SecOps Analyst",
        "category": "Security",
        "description": "Defends organizational infrastructure, performs vulnerability assessments, monitors SIEM alerts, and conducts incident response.",
        "mandatory_skills": [
            "Cybersecurity", "Network Security", "Vulnerability Assessment", "SIEM", "Linux", "Firewalls", "Incident Response"
        ],
        "secondary_skills": [
            "Wireshark", "Splunk", "Python", "Burp Suite", "Metasploit", "Penetration Testing", "SOC", "NIST Framework", "Cryptography", "Identity Access Management (IAM)"
        ],
        "domain_keywords": [
            "threat modeling", "zero trust", "malware analysis", "endpoint detection", "compliance (SOC2, ISO27001)",
            "packet analysis", "security hardening", "patch management", "incident triage", "forensics"
        ],
        "action_verbs": [
            "Investigated", "Mitigated", "Remediated", "Monitored", "Hardened", "Audited", "Defended", "Secured", "Neutralized"
        ],
        "certifications": ["CompTIA Security+", "Certified Information Systems Security Professional (CISSP)", "CEH (Certified Ethical Hacker)"],
        "education_keywords": ["Cybersecurity", "Information Assurance", "Computer Science", "Network Engineering"]
    },
    "mobile_developer": {
        "id": "mobile_developer",
        "title": "Mobile App Developer (iOS / Android / Flutter)",
        "category": "Software Engineering",
        "description": "Develops native and cross-platform mobile apps with smooth animations, offline persistence, and seamless API integrations.",
        "mandatory_skills": [
            "Flutter", "React Native", "Swift", "Kotlin", "Git", "REST APIs", "Mobile UI Design"
        ],
        "secondary_skills": [
            "iOS", "Android", "Dart", "SwiftUI", "Jetpack Compose", "Firebase", "Redux", "GraphQL", "App Store Deployment", "SQLite"
        ],
        "domain_keywords": [
            "mobile lifecycle", "push notifications", "offline caching", "in-app purchases", "app performance",
            "memory management", "responsive layouts", "touch gestures", "deep linking", "play store release"
        ],
        "action_verbs": [
            "Developed", "Published", "Crafted", "Optimized", "Integrated", "Launched", "Refactored", "Designed", "Built"
        ],
        "certifications": ["Google Associate Android Developer", "Meta React Native Specialization", "Apple Developer Certification"],
        "education_keywords": ["Computer Science", "Mobile Application Development", "Software Engineering"]
    },
    "product_manager": {
        "id": "product_manager",
        "title": "Product Manager",
        "category": "Product & Management",
        "description": "Drives product vision, roadmap strategy, user research, feature prioritization, and cross-functional go-to-market execution.",
        "mandatory_skills": [
            "Product Strategy", "Roadmap Planning", "User Research", "Agile / Scrum", "Data-driven Decision Making", "Stakeholder Management"
        ],
        "secondary_skills": [
            "Jira", "Figma", "SQL", "A/B Testing", "Wireframing", "PRD Writing", "KPI Tracking", "Google Analytics", "Mixpanel"
        ],
        "domain_keywords": [
            "user journey mapping", "market analysis", "feature prioritization", "customer discovery", "MVP definition",
            "go-to-market (GTM)", "unit economics", "retention metrics", "sprint planning", "product lifecycle"
        ],
        "action_verbs": [
            "Spearheaded", "Led", "Prioritized", "Launched", "Defined", "Increased", "Negotiated", "Championed", "Grew"
        ],
        "certifications": ["Product School Certified Product Manager (CPM)", "Pragmatic Institute Certified", "CSPO (Certified Scrum Product Owner)"],
        "education_keywords": ["Business Administration (MBA)", "Computer Science", "Information Systems", "Economics"]
    },
    "ui_ux_designer": {
        "id": "ui_ux_designer",
        "title": "UI / UX Designer",
        "category": "Product & Design",
        "description": "Designs intuitive user experiences, wireframes, high-fidelity prototypes, and comprehensive design systems.",
        "mandatory_skills": [
            "Figma", "UI Design", "UX Research", "Wireframing", "Prototyping", "Design Systems", "User Testing"
        ],
        "secondary_skills": [
            "Adobe XD", "Illustrator", "Photoshop", "HTML/CSS", "Design Tokens", "Interaction Design", "Information Architecture", "Micro-interactions"
        ],
        "domain_keywords": [
            "usability heuristics", "user persona", "journey mapping", "accessibility (WCAG)", "responsive typography",
            "color theory", "visual hierarchy", "A/B testing", "atomic design", "heuristic evaluation"
        ],
        "action_verbs": [
            "Designed", "Prototyped", "Conceptualized", "Researched", "Iterated", "Revamped", "Simplified", "Validated", "Standardized"
        ],
        "certifications": ["Google UX Design Professional Certificate", "Nielsen Norman Group UX Master", "Interaction Design Foundation"],
        "education_keywords": ["Human-Computer Interaction (HCI)", "Graphic Design", "Digital Media", "Psychology"]
    },
    "qa_engineer": {
        "id": "qa_engineer",
        "title": "QA Automation Engineer",
        "category": "Software Engineering",
        "description": "Architects automated test suites, end-to-end testing frameworks, API tests, and performance benchmarks to guarantee software quality.",
        "mandatory_skills": [
            "Test Automation", "Selenium", "Python", "JavaScript", "API Testing", "Postman", "Git", "CI/CD"
        ],
        "secondary_skills": [
            "Playwright", "Cypress", "PyTest", "JMeter", "Appium", "SQL", "Jenkins", "Test Planning", "Bug Tracking", "Jira"
        ],
        "domain_keywords": [
            "regression testing", "end-to-end testing", "load testing", "test case design", "continuous testing",
            "BDD / TDD", "root cause analysis", "code coverage", "flaky test resolution", "performance benchmarking"
        ],
        "action_verbs": [
            "Automated", "Tested", "Validated", "Authored", "Prevented", "Diagnosed", "Integrated", "Executed", "Ensured"
        ],
        "certifications": ["ISTQB Certified Tester", "Selenium Automation Specialist", "AWS Certified QA"],
        "education_keywords": ["Computer Science", "Software Engineering", "Quality Assurance"]
    },
    "blockchain_dev": {
        "id": "blockchain_dev",
        "title": "Blockchain / Web3 Developer",
        "category": "Software Engineering",
        "description": "Develops decentralized applications (dApps), smart contracts, tokenomics mechanisms, and blockchain protocols.",
        "mandatory_skills": [
            "Solidity", "Smart Contracts", "Ethereum", "JavaScript", "TypeScript", "Web3.js", "Ethers.js", "Git"
        ],
        "secondary_skills": [
            "Hardhat", "Truffle", "Rust", "IPFS", "DeFi", "ERC-20 / ERC-721", "Node.js", "React", "Smart Contract Security", "Alchemy"
        ],
        "domain_keywords": [
            "gas optimization", "reentrancy attack prevention", "decentralized finance", "consensus algorithms",
            "cryptographic proofs", "zero knowledge", "cross-chain bridges", "tokenomics", "DAO governance"
        ],
        "action_verbs": [
            "Developed", "Deployed", "Audited", "Optimized", "Engineered", "Implemented", "Minted", "Secured", "Constructed"
        ],
        "certifications": ["Certified Blockchain Developer (CBD)", "Ethereum Developer Bootcamp"],
        "education_keywords": ["Computer Science", "Cryptography", "Mathematics", "Distributed Computing"]
    }
}


def get_all_roles() -> List[Dict[str, Any]]:
    """Returns a list of all configured job roles."""
    return list(JOB_ROLES.values())


def get_role_by_id(role_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific role definition by its ID."""
    return JOB_ROLES.get(role_id)


def parse_custom_job_description(job_title: str, jd_text: str) -> Dict[str, Any]:
    """
    Dynamically extracts skills, keywords, and qualifications from user-provided job descriptions.
    """
    text_lower = jd_text.lower()
    
    # Common tech/business skills to cross-check
    known_skills = [
        "python", "javascript", "typescript", "react", "node.js", "node", "angular", "vue.js", "vue",
        "next.js", "fastapi", "django", "flask", "java", "spring", "spring boot", "c++", "c#", ".net",
        "go", "golang", "rust", "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "jenkins", "git",
        "github", "gitlab", "linux", "bash", "html", "css", "tailwind", "graphql", "rest", "restful",
        "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
        "tableau", "power bi", "excel", "spark", "hadoop", "kafka", "airflow", "snowflake", "bigquery",
        "figma", "ui/ux", "wireframing", "agile", "scrum", "jira", "product management", "a/b testing",
        "selenium", "cypress", "playwright", "unit testing", "cybersecurity", "penetration testing",
        "solidity", "web3", "microservices", "system design", "distributed systems"
    ]
    
    found_skills = []
    for skill in known_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Format nicely
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
    
    # Extract capital terms / acronyms (like AWS, CI/CD, REST, NLP)
    capital_acronyms = set(re.findall(r'\b[A-Z]{2,6}\b', jd_text))
    
    # High impact action verbs
    standard_verbs = [
        "Architected", "Developed", "Led", "Engineered", "Optimized", "Scaled",
        "Spearheaded", "Implemented", "Delivered", "Automated", "Designed"
    ]
    
    # Dynamic Role Object
    mandatory = found_skills[:8] if found_skills else ["Communication", "Problem Solving", "Collaboration", "Project Delivery"]
    secondary = found_skills[8:18] if len(found_skills) > 8 else ["Git", "Agile", "Testing", "Documentation"]
    
    # Extract domain words (frequency analysis of nouns/tech words)
    words = re.findall(r'\b[A-Za-z]{4,}\b', text_lower)
    stopwords = {"with", "that", "this", "from", "have", "will", "your", "must", "work", "team", "years", "experience", "role", "help"}
    filtered_words = [w for w in words if w not in stopwords and len(w) > 4]
    
    # Top frequent words as domain keywords
    word_freq = {}
    for w in filtered_words:
        word_freq[w] = word_freq.get(w, 0) + 1
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    domain_keywords = [k[0] for k in sorted_keywords[:12]]
    
    return {
        "id": "custom_" + re.sub(r'[^a-zA-Z0-9]', '_', job_title.lower())[:20],
        "title": job_title.strip() if job_title.strip() else "Custom Job Role",
        "category": "Custom Target Role",
        "description": jd_text[:250] + "..." if len(jd_text) > 250 else jd_text,
        "mandatory_skills": mandatory,
        "secondary_skills": secondary,
        "domain_keywords": domain_keywords or ["scalability", "best practices", "collaboration", "delivery"],
        "action_verbs": standard_verbs,
        "certifications": ["Relevant Industry Certification"],
        "education_keywords": ["Computer Science", "Engineering", "Related Degree"]
    }
