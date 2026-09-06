"""A second catalog, in clinical medicine, for a domain PathFinder was never
written for.

PathFinder's engines take a catalog as an argument; nothing in the profiler,
gap analysis, ranker, planner or question answerer knows what a "course" is
about. This file exists to prove that rather than assert it: it builds a
catalog that shares no skill, role, item id or category with the software one,
and the same engine produces a coherent clinical curriculum from it —
anatomy before physiology before pharmacology, ward rotations at the end —
with no code change.

Build it:      python examples/medicine/build_catalog.py
Run PathFinder on it:
    cp examples/medicine/data/*.json backend/app/data/
    cd backend && uvicorn app.main:app --port 8000
(then restore with `git checkout backend/app/data` to get the software catalog back)

The test in backend/tests/test_catalog_agnostic.py exercises this end to end.
"""
import json, math, random
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

SKILLS = [
    ("anatomy","Human Anatomy","Foundations",["anatomy","structure"]),
    ("physiology","Physiology","Foundations",["physiology","function"]),
    ("biochem","Biochemistry","Foundations",["biochemistry","metabolism"]),
    ("pharma","Pharmacology","Clinical Science",["pharmacology","drugs"]),
    ("pathology","Pathology","Clinical Science",["pathology","disease"]),
    ("micro","Microbiology","Clinical Science",["microbiology","infection"]),
    ("diagnosis","Clinical Diagnosis","Practice",["diagnosis","examination"]),
    ("emergency","Emergency Medicine","Practice",["emergency","trauma","acute care"]),
    ("surgery","Surgical Basics","Practice",["surgery","operative"]),
    ("ethics","Medical Ethics","Professional",["ethics","consent"]),
    ("patient-comms","Patient Communication","Professional",["bedside manner","counselling","talking to patients"]),
    ("research","Clinical Research","Professional",["trials","evidence based"]),
]
ROWS = """
med-101 | Foundations of Human Anatomy    | MedSchool | course     | 1 | 30 | video       | anatomy:0.7                          |                 | 4.7 | 120000
med-102 | Physiology of Organ Systems     | MedSchool | course     | 1 | 28 | video       | physiology:0.7,anatomy:0.2           | med-101         | 4.6 | 98000
med-103 | Medical Biochemistry            | MedSchool | course     | 1 | 24 | reading     | biochem:0.7                          |                 | 4.4 | 76000
med-104 | Principles of Pharmacology      | MedSchool | course     | 2 | 26 | video       | pharma:0.75,biochem:0.25             | med-103,med-102 | 4.6 | 64000
med-105 | General Pathology               | MedSchool | course     | 2 | 26 | video       | pathology:0.75,physiology:0.2        | med-102         | 4.5 | 58000
med-106 | Clinical Microbiology           | MedSchool | course     | 2 | 20 | mixed       | micro:0.75,pathology:0.2             | med-105         | 4.5 | 41000
med-107 | Clinical Examination Skills     | Hospital  | course     | 2 | 22 | mixed       | diagnosis:0.75,patient-comms:0.3     | med-102         | 4.8 | 52000
med-108 | Emergency and Acute Care        | Hospital  | course     | 3 | 24 | mixed       | emergency:0.8,diagnosis:0.35         | med-107,med-104 | 4.8 | 37000
med-109 | Introduction to Surgery         | Hospital  | course     | 3 | 28 | mixed       | surgery:0.75,anatomy:0.3             | med-107         | 4.7 | 29000
med-110 | Medical Ethics and Consent      | MedSchool | course     | 1 | 10 | reading     | ethics:0.8,patient-comms:0.25        |                 | 4.5 | 88000
med-111 | Communicating with Patients     | Hospital  | course     | 1 | 12 | mixed       | patient-comms:0.8,ethics:0.2         |                 | 4.7 | 71000
med-112 | Evidence-Based Practice         | MedSchool | course     | 2 | 16 | reading     | research:0.8,pathology:0.2           | med-105         | 4.4 | 33000
med-p01 | Rotation: Supervised Ward Round | Hospital  | project    | 3 | 30 | project     | diagnosis:0.5,patient-comms:0.4      | med-107         | 4.9 | 22000
med-p02 | Rotation: Emergency Department  | Hospital  | project    | 3 | 32 | project     | emergency:0.55,diagnosis:0.35        | med-108         | 4.9 | 18000
med-a01 | Assessment: Clinical Skills OSCE| MedSchool | assessment | 3 |  4 | mixed       | diagnosis:0.35,patient-comms:0.25    | med-107         | 4.6 | 44000
med-a02 | Assessment: Pharmacology Exam   | MedSchool | assessment | 2 |  3 | interactive | pharma:0.35                          | med-104         | 4.5 | 39000
"""
ROLES = [
    ("emergency-physician","Emergency Physician","Clinical",
     ["emergency medicine","er doctor","acute care physician","emergency"],
     {"emergency":0.95,"diagnosis":0.9,"pharma":0.8,"physiology":0.7,"anatomy":0.6,
      "patient-comms":0.7,"ethics":0.6,"pathology":0.5}),
    ("surgeon","Surgeon","Clinical",
     ["surgery","surgeon","operative medicine"],
     {"surgery":0.95,"anatomy":0.9,"diagnosis":0.7,"emergency":0.5,"ethics":0.6,
      "patient-comms":0.6,"pathology":0.5}),
    ("clinical-researcher","Clinical Researcher","Academic",
     ["clinical research","medical research","trials"],
     {"research":0.95,"pathology":0.7,"biochem":0.6,"ethics":0.8,"patient-comms":0.5,
      "micro":0.5}),
]

def main():
    skills=[{"id":a,"name":b,"category":c,"aliases":d} for a,b,c,d in SKILLS]
    roles=[{"id":a,"title":b,"family":c,"aliases":d,"skills":e} for a,b,c,d,e in ROLES]
    items=[]
    for line in ROWS.strip().splitlines():
        f=[x.strip() for x in line.split("|")]
        sk={}
        for pair in f[7].split(","):
            if pair.strip():
                k,_,v=pair.partition(":"); sk[k.strip()]=float(v)
        items.append({"id":f[0],"title":f[1],"provider":f[2],"kind":f[3],"level":int(f[4]),
                      "hours":int(f[5]),"modality":f[6],"skills":sk,
                      "prereqs":[p.strip() for p in f[8].split(",") if p.strip()],
                      "rating":float(f[9]),"learners":int(f[10])})
    by={i["id"]:i for i in items}; depth={}
    def walk(i):
        if i in depth: return depth[i]
        p=by[i]["prereqs"]; depth[i]=0 if not p else 1+max(walk(x) for x in p); return depth[i]
    for i in items: i["depth"]=walk(i["id"])

    rng=random.Random(7); co=defaultdict(lambda: defaultdict(int)); cnt=defaultdict(int)
    for _ in range(800):
        role=rng.choice(roles)
        pool=[i["id"] for i in items if sum(w*role["skills"].get(s,0) for s,w in i["skills"].items())>0.05]
        chosen=set(rng.sample(pool,min(len(pool),rng.randint(3,8))))
        for c in list(chosen): chosen.update(by[c]["prereqs"])
        ses=sorted(chosen)
        for x in ses: cnt[x]+=1
        for a_i,a in enumerate(ses):
            for b in ses[a_i+1:]: co[a][b]+=1; co[b][a]+=1
    inter={"seed":7,"n_sessions":800,"item_counts":dict(cnt),
           "co_counts":{a:dict(b) for a,b in co.items()}}
    for name,payload in (("skills.json",skills),("catalog.json",items),
                         ("roles.json",roles),("interactions.json",inter)):
        (OUT/name).write_text(json.dumps(payload,indent=1,sort_keys=True)+"\n")
    print(f"  alt catalog: {len(items)} items, {len(skills)} skills, {len(roles)} roles, max depth {max(depth.values())}")

if __name__=="__main__": main()
