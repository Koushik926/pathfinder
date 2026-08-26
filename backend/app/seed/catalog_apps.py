"""Catalog seed, part 3: web, mobile, cloud, security, product and emerging tech.

Same row format as ``catalog_core``.
"""

ROWS = """
web-101  | Responsive Web Design                      | freeCodeCamp    | course     | 1 | 25 | interactive | html-css:0.65,responsive-design:0.4                       |                  | 4.8 | 2100000
web-102  | CSS Layout: Flexbox & Grid                 | The Odin Project| course     | 1 | 12 | interactive | html-css:0.4,responsive-design:0.55                       | web-101          | 4.7 | 480000
web-103  | Tailwind CSS in Practice                   | PathFinder Labs | course     | 1 | 8  | mixed       | responsive-design:0.5,ui-design:0.2                       | web-102          | 4.6 | 120000
web-104  | Web Accessibility Fundamentals             | Google/Udacity  | course     | 2 | 10 | video       | accessibility:0.75,html-css:0.2                           | web-102          | 4.7 | 210000
web-105  | Web Performance Optimisation               | web.dev         | course     | 2 | 12 | reading     | web-performance:0.75,javascript:0.2                       | js-103           | 4.7 | 165000
react-101| React: The Complete Guide                  | Udemy           | course     | 2 | 30 | video       | react:0.7,javascript:0.25                                 | js-103           | 4.7 | 900000
react-102| React Hooks & Patterns                     | Epic React      | course     | 2 | 18 | interactive | react:0.6,state-management:0.35                           | react-101        | 4.9 | 240000
react-103| State Management with Redux & Zustand      | Frontend Masters| course     | 2 | 12 | video       | state-management:0.7,react:0.25                           | react-101        | 4.6 | 190000
react-104| Next.js App Router in Depth                | Vercel          | course     | 2 | 20 | mixed       | nextjs:0.75,react:0.3,web-performance:0.25                | react-102        | 4.7 | 320000
react-105| Testing React Applications                 | Testing Library | course     | 2 | 12 | mixed       | testing:0.55,react:0.3                                    | react-101        | 4.7 | 150000
vue-101  | Vue 3 & Svelte Essentials                  | Vue Mastery     | course     | 2 | 18 | video       | vue-svelte:0.75,javascript:0.25                           | js-103           | 4.6 | 175000
web-p01  | Project: Portfolio Website from Scratch    | PathFinder Labs | project    | 1 | 12 | project     | html-css:0.4,responsive-design:0.35,accessibility:0.2     | web-102          | 4.7 | 210000
web-p02  | Project: Full-stack Dashboard App          | PathFinder Labs | project    | 2 | 26 | project     | react:0.4,rest-api:0.35,node-backend:0.3,data-viz:0.2     | react-102,node-101| 4.8 | 88000
web-a01  | Assessment: Frontend Skills Check          | PathFinder Labs | assessment | 2 |  2 | interactive | react:0.25,javascript:0.25,html-css:0.2                   | react-101        | 4.6 | 94000

node-101 | Node.js & Express Backends                 | The Odin Project| course     | 2 | 24 | interactive | node-backend:0.7,rest-api:0.35,javascript:0.2             | js-103           | 4.7 | 420000
node-102 | NestJS for Scalable APIs                   | Udemy           | course     | 3 | 18 | video       | node-backend:0.55,rest-api:0.35,typescript:0.3            | node-101,js-104  | 4.6 | 130000
api-101  | FastAPI: Modern Python APIs                | PathFinder Labs | course     | 2 | 14 | mixed       | fastapi-backend:0.7,rest-api:0.4,python-advanced:0.2      | py-104           | 4.8 | 175000
api-102  | Django for Web Applications                | Coursera        | course     | 2 | 26 | video       | fastapi-backend:0.6,db-design:0.3,auth-security:0.25      | py-104,sql-101   | 4.6 | 380000
api-103  | REST API Design Best Practices             | PathFinder Labs | course     | 2 | 10 | reading     | rest-api:0.75,tech-writing:0.2                            | net-102          | 4.7 | 105000
api-104  | GraphQL from Zero to Production            | Apollo          | course     | 3 | 14 | mixed       | graphql:0.75,rest-api:0.2,node-backend:0.2                | node-101         | 4.6 | 120000
api-105  | Authentication & Authorisation in Practice | Auth0           | course     | 2 | 12 | mixed       | auth-security:0.75,web-security:0.3,rest-api:0.2          | api-103          | 4.7 | 165000
api-106  | Realtime Apps with WebSockets              | PathFinder Labs | course     | 3 | 12 | mixed       | websockets:0.75,node-backend:0.25                         | node-101         | 4.5 | 72000

mob-101  | Android Development with Kotlin            | Google/Udacity  | course     | 2 | 30 | mixed       | android-dev:0.75,oop:0.2                                  | java-101         | 4.6 | 390000
mob-102  | Jetpack Compose Essentials                 | Google          | course     | 2 | 16 | mixed       | android-dev:0.6,ui-design:0.25                            | mob-101          | 4.7 | 180000
mob-103  | iOS Development with SwiftUI               | Stanford CS193p | course     | 2 | 28 | video       | ios-dev:0.75,ui-design:0.25                               |                  | 4.8 | 260000
mob-104  | Flutter & Dart Complete Guide              | Udemy           | course     | 2 | 26 | video       | react-native:0.7,ui-design:0.2                            | js-102           | 4.6 | 340000
mob-105  | React Native in Practice                   | Expo            | course     | 2 | 20 | mixed       | react-native:0.65,react:0.35                              | react-101        | 4.6 | 155000
mob-p01  | Project: Ship a Mobile App to Store        | PathFinder Labs | project    | 3 | 28 | project     | react-native:0.4,ui-design:0.25,ci-cd:0.2                 | mob-104          | 4.7 | 46000

lin-101  | Linux Fundamentals                         | Linux Foundation| course     | 1 | 18 | mixed       | linux-admin:0.7,bash-shell:0.35                           | sh-101           | 4.6 | 480000
dock-101 | Docker for Developers                      | Docker          | course     | 2 | 12 | mixed       | docker:0.75,linux-admin:0.25                              | lin-101          | 4.8 | 560000
k8s-101  | Kubernetes Basics                          | Linux Foundation| course     | 2 | 20 | mixed       | kubernetes:0.7,docker:0.3                                 | dock-101         | 4.7 | 380000
k8s-102  | Kubernetes in Production                   | CNCF            | course     | 3 | 24 | mixed       | kubernetes:0.65,observability:0.3,cloud-architecture:0.25 | k8s-101          | 4.7 | 145000
ci-101   | CI/CD with GitHub Actions                  | GitHub          | course     | 2 | 12 | mixed       | ci-cd:0.75,git:0.25,testing:0.2                           | git-101          | 4.7 | 420000
iac-101  | Infrastructure as Code with Terraform      | HashiCorp       | course     | 2 | 18 | mixed       | iac:0.75,cloud-architecture:0.25                          | aws-101          | 4.7 | 290000
aws-101  | AWS Cloud Practitioner Essentials          | AWS             | course     | 1 | 14 | video       | aws:0.6,cloud-architecture:0.25                           |                  | 4.7 | 1200000
aws-102  | AWS Solutions Architect Associate          | AWS             | course     | 2 | 34 | mixed       | aws:0.75,cloud-architecture:0.5,network-security:0.2      | aws-101          | 4.8 | 780000
aws-103  | Serverless with Lambda & API Gateway       | AWS             | course     | 2 | 16 | mixed       | aws:0.5,cloud-architecture:0.35,rest-api:0.25             | aws-102          | 4.6 | 240000
gcp-101  | Google Cloud Fundamentals                  | Google Cloud    | course     | 1 | 14 | mixed       | azure-gcp:0.65,cloud-architecture:0.25                    |                  | 4.6 | 520000
az-101   | Microsoft Azure Fundamentals AZ-900        | Microsoft Learn | course     | 1 | 14 | mixed       | azure-gcp:0.65,cloud-architecture:0.25                    |                  | 4.7 | 890000
obs-101  | Observability with Prometheus & Grafana    | Grafana Labs    | course     | 2 | 14 | mixed       | observability:0.75,linux-admin:0.2                        | dock-101         | 4.6 | 165000
dev-p01  | Project: Containerise & Deploy a Service   | PathFinder Labs | project    | 2 | 18 | project     | docker:0.45,ci-cd:0.35,cloud-architecture:0.25            | dock-101,ci-101  | 4.8 | 74000
dev-a01  | Assessment: DevOps Readiness Check         | PathFinder Labs | assessment | 2 |  2 | interactive | docker:0.25,ci-cd:0.25,linux-admin:0.2                    | ci-101           | 4.6 | 58000

sec-101  | Cybersecurity Fundamentals                 | edX             | course     | 1 | 18 | video       | security-basics:0.7,networking:0.2                        |                  | 4.6 | 640000
sec-102  | Cryptography I                             | Stanford        | course     | 3 | 28 | video       | cryptography:0.8,discrete-math:0.3,probability:0.2        | math-107         | 4.8 | 260000
sec-103  | OWASP Top 10 Web Security                  | PortSwigger     | course     | 2 | 16 | interactive | web-security:0.75,security-basics:0.3                     | sec-101,net-102  | 4.8 | 410000
sec-104  | Ethical Hacking & Penetration Testing      | TryHackMe       | course     | 2 | 30 | interactive | pentesting:0.7,web-security:0.35,linux-admin:0.3          | sec-103          | 4.8 | 520000
sec-105  | Network Security & Packet Analysis         | Cisco NetAcad   | course     | 2 | 20 | mixed       | network-security:0.75,networking:0.35                     | net-101,sec-101  | 4.6 | 300000
sec-106  | Cloud Security & IAM                       | AWS             | course     | 3 | 16 | mixed       | cloud-security:0.75,aws:0.25,security-basics:0.2          | aws-102,sec-101  | 4.6 | 175000
sec-107  | Incident Response & Digital Forensics      | SANS            | course     | 3 | 24 | mixed       | forensics:0.75,security-basics:0.25,linux-admin:0.2       | sec-105          | 4.7 | 120000
sec-p01  | Project: Secure a Vulnerable Web App       | PathFinder Labs | project    | 2 | 16 | project     | web-security:0.5,auth-security:0.3,testing:0.2            | sec-103          | 4.8 | 52000
sec-a01  | Assessment: Capture the Flag Challenge     | PathFinder Labs | assessment | 2 |  4 | interactive | pentesting:0.3,web-security:0.25                          | sec-104          | 4.9 | 96000

ux-101   | Introduction to UX Design                  | Google/Coursera | course     | 1 | 20 | video       | ux-research:0.6,ui-design:0.35                            |                  | 4.8 | 950000
ux-102   | UX Research Methods                        | NN/g            | course     | 2 | 14 | mixed       | ux-research:0.75,communication:0.2                        | ux-101           | 4.7 | 230000
ux-103   | UI Design with Figma                       | Figma           | course     | 1 | 12 | mixed       | ui-design:0.7,responsive-design:0.2                       | ux-101           | 4.7 | 480000
ux-104   | Design Systems in Practice                 | Frontend Masters| course     | 2 | 12 | video       | ui-design:0.55,responsive-design:0.3,accessibility:0.25   | ux-103           | 4.6 | 140000
pm-101   | Product Management Fundamentals            | Coursera        | course     | 1 | 16 | video       | product-thinking:0.7,communication:0.3                    |                  | 4.6 | 520000
pm-102   | Agile & Scrum in Practice                  | Scrum.org       | course     | 1 | 10 | mixed       | agile-scrum:0.75,communication:0.2                        |                  | 4.6 | 610000
pm-103   | Data-Informed Product Decisions            | Reforge         | course     | 3 | 14 | video       | product-thinking:0.55,data-analysis:0.3,statistics:0.25   | pm-101,da-104    | 4.7 | 95000
com-101  | Technical Writing for Engineers            | Google          | course     | 1 |  8 | reading     | tech-writing:0.75,communication:0.3                       |                  | 4.7 | 340000
com-102  | Presenting & Storytelling for Tech         | PathFinder Labs | course     | 2 | 10 | mixed       | communication:0.7,tech-writing:0.2                        | com-101          | 4.6 | 78000
car-101  | Coding Interview Preparation               | LeetCode        | course     | 2 | 30 | interactive | interview-prep:0.6,dsa-advanced:0.4,algorithms:0.3        | dsa-102          | 4.7 | 880000
car-102  | Behavioural Interviews & Resume Craft      | PathFinder Labs | course     | 1 |  8 | mixed       | interview-prep:0.55,communication:0.35                    |                  | 4.5 | 260000
car-103  | Freelancing & Building a Portfolio         | PathFinder Labs | course     | 1 | 10 | mixed       | freelancing:0.7,communication:0.25,tech-writing:0.2       | web-p01          | 4.5 | 130000

bc-101   | Blockchain Basics                          | Coursera        | course     | 1 | 16 | video       | blockchain:0.6,cryptography:0.25                          |                  | 4.5 | 380000
bc-102   | Smart Contracts with Solidity              | Alchemy         | course     | 2 | 22 | mixed       | blockchain:0.7,testing:0.2                                | bc-101,js-103    | 4.6 | 210000
iot-101  | IoT with Arduino & ESP32                   | NPTEL           | course     | 1 | 20 | mixed       | iot-embedded:0.7,c-lang:0.3                               |                  | 4.5 | 250000
iot-102  | Embedded Systems Programming               | edX             | course     | 3 | 26 | video       | iot-embedded:0.6,c-lang:0.4,os-concepts:0.25              | iot-101,c-101    | 4.6 | 130000
game-101 | Game Development with Unity                | Unity Learn     | course     | 2 | 30 | mixed       | game-dev:0.7,oop:0.25                                     | cpp-101          | 4.6 | 420000
game-102 | Godot & 2D Game Design                     | GDQuest         | course     | 1 | 18 | mixed       | game-dev:0.6,ui-design:0.2                                |                  | 4.6 | 160000
arvr-101 | AR/VR Development Foundations              | Meta/Coursera   | course     | 2 | 22 | mixed       | ar-vr:0.7,game-dev:0.3                                    | game-101         | 4.5 | 145000
rob-101  | Robotics with ROS                          | edX             | course     | 3 | 28 | mixed       | robotics:0.75,python-advanced:0.25,linear-algebra:0.2     | py-104,math-101  | 4.6 | 110000
qc-101   | Quantum Computing with Qiskit              | IBM             | course     | 3 | 20 | mixed       | quantum-computing:0.75,linear-algebra:0.4                 | math-101         | 4.6 | 165000
"""
