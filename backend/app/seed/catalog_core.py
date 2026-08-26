"""Catalog seed, part 1: programming foundations, CS core, mathematics.

Row format (pipe-delimited, one item per line):
    id | title | provider | kind | level | hours | modality | skills | prereqs | rating | learners

  kind      course | project | assessment
  level     1 beginner, 2 intermediate, 3 advanced
  hours     estimated effort in hours
  modality  video | interactive | reading | project | mixed
  skills    skill-id:weight,...   weight in [0,1] = how much of that skill the item teaches
  prereqs   comma-separated item ids that should be completed first (may be empty)
  rating    mean learner rating out of 5
  learners  approximate enrolment, used as a popularity prior
"""

ROWS = """
py-101   | Python for Everybody: Getting Started      | Coursera        | course     | 1 | 18 | video       | python-basics:0.55                                        |                  | 4.8 | 2400000
py-102   | Automate the Boring Stuff with Python      | Udemy           | course     | 1 | 22 | video       | python-basics:0.5,bash-shell:0.2                          | py-101           | 4.7 | 1300000
py-103   | Python Data Structures                     | Coursera        | course     | 1 | 20 | video       | python-basics:0.4,dsa-basics:0.35                         | py-101           | 4.8 | 900000
py-104   | Intermediate Python                        | freeCodeCamp    | course     | 2 | 25 | video       | python-basics:0.3,python-advanced:0.5,oop:0.3             | py-103           | 4.6 | 610000
py-105   | Fluent Python Patterns                     | O'Reilly        | course     | 3 | 30 | reading     | python-advanced:0.75,clean-code:0.3                       | py-104           | 4.9 | 120000
py-106   | Async Python with asyncio                  | Talk Python     | course     | 3 | 14 | video       | python-advanced:0.6,websockets:0.2                        | py-104           | 4.7 | 88000
py-107   | Python Testing with pytest                 | Test & Code     | course     | 2 | 12 | mixed       | testing:0.65,python-basics:0.2                            | py-104           | 4.7 | 140000
py-p01   | Project: Build a CLI Expense Tracker       | PathFinder Labs | project    | 1 | 10 | project     | python-basics:0.4,bash-shell:0.25                         | py-102           | 4.6 | 42000
py-p02   | Project: REST Scraper & Data Reporter      | PathFinder Labs | project    | 2 | 16 | project     | python-advanced:0.4,data-cleaning:0.35,rest-api:0.2       | py-104           | 4.7 | 31000
py-a01   | Assessment: Python Proficiency Check       | PathFinder Labs | assessment | 1 |  2 | interactive | python-basics:0.3                                         | py-103           | 4.5 | 96000
py-a02   | Assessment: Advanced Python & Idioms       | PathFinder Labs | assessment | 3 |  2 | interactive | python-advanced:0.35                                      | py-105           | 4.6 | 27000

js-101   | JavaScript Algorithms and Data Structures  | freeCodeCamp    | course     | 1 | 30 | interactive | javascript:0.55,dsa-basics:0.25                           |                  | 4.8 | 1800000
js-102   | Modern JavaScript from the Beginning       | Udemy           | course     | 1 | 22 | video       | javascript:0.6                                            | js-101           | 4.7 | 420000
js-103   | JavaScript: Understanding the Weird Parts  | Udemy           | course     | 2 | 18 | video       | javascript:0.55,functional-prog:0.25                      | js-102           | 4.7 | 380000
js-104   | TypeScript Deep Dive                       | Frontend Masters| course     | 2 | 16 | video       | typescript:0.7,javascript:0.2                             | js-103           | 4.8 | 210000
js-105   | Testing JavaScript with Jest & Vitest      | Frontend Masters| course     | 2 | 12 | mixed       | testing:0.6,javascript:0.2                                | js-103           | 4.7 | 130000
js-a01   | Assessment: JavaScript Core Concepts       | PathFinder Labs | assessment | 2 |  2 | interactive | javascript:0.3                                            | js-103           | 4.5 | 74000

java-101 | Java Programming: Solving Problems         | Coursera        | course     | 1 | 28 | video       | java:0.55,oop:0.3                                         |                  | 4.6 | 540000
java-102 | Object-Oriented Programming in Java        | Coursera        | course     | 2 | 26 | video       | java:0.4,oop:0.6                                          | java-101         | 4.7 | 380000
java-103 | Spring Boot Essentials                     | Udemy           | course     | 2 | 24 | video       | java:0.3,rest-api:0.45,fastapi-backend:0.15               | java-102         | 4.6 | 290000
cpp-101  | C++ Fundamentals                           | edX             | course     | 1 | 26 | video       | cpp:0.55,oop:0.25                                         |                  | 4.5 | 310000
cpp-102  | Competitive Programming in C++             | CodeChef        | course     | 3 | 40 | interactive | cpp:0.4,dsa-advanced:0.55,algorithms:0.35                 | cpp-101,dsa-102  | 4.7 | 160000
c-101    | C Programming and Memory                   | NPTEL           | course     | 1 | 24 | video       | c-lang:0.6,os-concepts:0.15                               |                  | 4.5 | 270000
go-101   | Go: The Complete Guide                     | Udemy           | course     | 2 | 20 | video       | go-lang:0.65,networking:0.15                              | py-104           | 4.6 | 145000
rust-101 | Rust Programming: The Book                 | rust-lang.org   | course     | 2 | 35 | reading     | rust:0.7,functional-prog:0.2                              | c-101            | 4.9 | 200000

git-101  | Git & GitHub Fundamentals                  | freeCodeCamp    | course     | 1 |  8 | video       | git:0.65                                                  |                  | 4.7 | 880000
git-102  | Advanced Git: Rebase, Bisect, Hooks        | Frontend Masters| course     | 2 | 10 | video       | git:0.5,debugging:0.2                                     | git-101          | 4.8 | 95000
sh-101   | The Missing Semester of Your CS Education  | MIT             | course     | 1 | 12 | video       | bash-shell:0.6,git:0.3,linux-admin:0.25,debugging:0.25    |                  | 4.9 | 460000
cc-101   | Clean Code & Refactoring Principles        | Pluralsight     | course     | 2 | 14 | video       | clean-code:0.7,oop:0.25,testing:0.2                       | py-104           | 4.6 | 175000
dbg-101  | Debugging & Profiling in Practice          | PathFinder Labs | course     | 2 |  9 | mixed       | debugging:0.65,testing:0.2                                | py-104           | 4.5 | 52000

sql-101  | SQL for Data Science                       | Coursera        | course     | 1 | 16 | interactive | sql:0.6,db-design:0.2                                     |                  | 4.6 | 950000
sql-102  | Intermediate SQL: Window Functions         | Mode Analytics  | course     | 2 | 12 | interactive | sql:0.55,data-analysis:0.2                                | sql-101          | 4.7 | 310000
sql-103  | Database Design & Normalisation            | NPTEL           | course     | 2 | 20 | video       | db-design:0.7,sql:0.25                                     | sql-101          | 4.5 | 220000
sql-104  | Query Performance & Indexing               | Use The Index   | course     | 3 | 10 | reading     | db-design:0.45,sql:0.35,debugging:0.2                     | sql-103          | 4.8 | 84000
sql-a01  | Assessment: SQL Query Challenge            | PathFinder Labs | assessment | 2 |  2 | interactive | sql:0.3                                                   | sql-102          | 4.6 | 118000

dsa-101  | Data Structures Easy to Advanced           | freeCodeCamp    | course     | 1 | 30 | video       | dsa-basics:0.65,algorithms:0.25                           | py-103           | 4.8 | 720000
dsa-102  | Algorithms Part I                          | Coursera        | course     | 2 | 34 | video       | algorithms:0.7,dsa-basics:0.3                             | dsa-101          | 4.9 | 640000
dsa-103  | Algorithms Part II: Graphs & Strings       | Coursera        | course     | 3 | 34 | video       | dsa-advanced:0.65,algorithms:0.35                         | dsa-102          | 4.9 | 380000
dsa-104  | Dynamic Programming Patterns               | AlgoExpert      | course     | 3 | 24 | interactive | dsa-advanced:0.7,algorithms:0.25                          | dsa-102          | 4.7 | 210000
dsa-p01  | Project: Build Your Own Data Structures    | PathFinder Labs | project    | 2 | 14 | project     | dsa-basics:0.45,oop:0.3,testing:0.2                       | dsa-101          | 4.6 | 38000
dsa-a01  | Assessment: DSA Timed Mock Test            | PathFinder Labs | assessment | 2 |  3 | interactive | dsa-basics:0.3,algorithms:0.3                             | dsa-102          | 4.7 | 205000

os-101   | Operating Systems: Three Easy Pieces       | Wisconsin       | course     | 2 | 30 | reading     | os-concepts:0.75,c-lang:0.2                               | c-101            | 4.9 | 190000
net-101  | Computer Networking: A Top-Down Approach   | NPTEL           | course     | 2 | 28 | video       | networking:0.75                                           |                  | 4.6 | 260000
net-102  | HTTP, DNS & The Modern Web Stack           | PathFinder Labs | course     | 1 |  8 | mixed       | networking:0.4,rest-api:0.2                               |                  | 4.5 | 61000
ds-101   | Distributed Systems Fundamentals           | MIT OCW         | course     | 3 | 32 | video       | distributed-systems:0.75,networking:0.25                  | os-101,net-101   | 4.8 | 120000
sysd-101 | System Design Primer                       | GitHub          | course     | 2 | 20 | reading     | system-design:0.6,distributed-systems:0.3,db-design:0.2   | net-101          | 4.8 | 540000
sysd-102 | Grokking Modern System Design              | Educative       | course     | 3 | 26 | interactive | system-design:0.75,distributed-systems:0.4,cloud-architecture:0.25 | sysd-101 | 4.7 | 290000
sysd-a01 | Assessment: System Design Mock Interview   | PathFinder Labs | assessment | 3 |  3 | mixed       | system-design:0.35                                        | sysd-102         | 4.8 | 66000
comp-101 | Crafting Interpreters                      | craftinginterpreters | course| 3 | 40 | reading     | compilers:0.8,cpp:0.2,clean-code:0.2                      | java-102         | 4.9 | 95000

math-101 | Linear Algebra for Machine Learning        | Imperial/Coursera| course    | 1 | 20 | video       | linear-algebra:0.7                                        |                  | 4.7 | 480000
math-102 | Essence of Linear Algebra                  | 3Blue1Brown     | course     | 1 |  6 | video       | linear-algebra:0.45                                       |                  | 4.9 | 1100000
math-103 | Multivariate Calculus for ML               | Imperial/Coursera| course    | 2 | 20 | video       | calculus:0.7,optimization:0.25                            | math-101         | 4.6 | 300000
math-104 | Probability & Statistics for Data Science  | edX             | course     | 1 | 24 | video       | probability:0.6,statistics:0.5                            |                  | 4.6 | 420000
math-105 | Statistical Inference                      | Coursera        | course     | 2 | 22 | video       | statistics:0.7,probability:0.35                           | math-104         | 4.5 | 260000
math-106 | Convex Optimization                        | Stanford        | course     | 3 | 30 | video       | optimization:0.8,linear-algebra:0.3,calculus:0.3          | math-103         | 4.8 | 88000
math-107 | Discrete Mathematics                        | NPTEL          | course     | 1 | 26 | video       | discrete-math:0.75,algorithms:0.2                         |                  | 4.5 | 240000
math-a01 | Assessment: Math Readiness for ML          | PathFinder Labs | assessment | 1 |  2 | interactive | linear-algebra:0.25,probability:0.25,calculus:0.2         | math-101,math-104| 4.6 | 130000
"""
