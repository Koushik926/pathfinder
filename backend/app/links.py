"""Where to actually go and take a recommended item.

A recommender that names a course but gives you no way to reach it is only
half a recommendation. We do not hardcode deep links: 238 hand-written URLs
would rot, and an item pointing at a dead page is worse than one pointing
nowhere. Instead each provider gets a search URL built from the item title,
which stays correct as catalogs change and is honest about what it does —
the interface labels it "Find on Coursera", not "Go to course".

Items authored for this project have no external home, so they return None
and the interface simply does not show a link.
"""

from __future__ import annotations

from urllib.parse import quote_plus

# provider -> search URL template, {q} replaced by the url-encoded title
PROVIDER_SEARCH = {
    "Coursera": "https://www.coursera.org/search?query={q}",
    "edX": "https://www.edx.org/search?q={q}",
    "Udemy": "https://www.udemy.com/courses/search/?q={q}",
    "freeCodeCamp": "https://www.freecodecamp.org/news/search/?query={q}",
    "Kaggle Learn": "https://www.kaggle.com/learn",
    "Kaggle": "https://www.kaggle.com/competitions",
    "DeepLearning.AI": "https://www.deeplearning.ai/courses/?search={q}",
    "fast.ai": "https://course.fast.ai/",
    "Hugging Face": "https://huggingface.co/learn",
    "NPTEL": "https://nptel.ac.in/courses",
    "MIT": "https://ocw.mit.edu/search/?q={q}",
    "MIT OCW": "https://ocw.mit.edu/search/?q={q}",
    "Stanford": "https://online.stanford.edu/search-catalog?keywords={q}",
    "Google": "https://grow.google/certificates/",
    "Google Cloud": "https://www.cloudskillsboost.google/catalog?search={q}",
    "Microsoft Learn": "https://learn.microsoft.com/en-us/search/?terms={q}",
    "AWS": "https://skillbuilder.aws/search?searchText={q}",
    "The Odin Project": "https://www.theodinproject.com/paths",
    "Frontend Masters": "https://frontendmasters.com/courses/",
    "Codecademy": "https://www.codecademy.com/search?query={q}",
    "DataCamp": "https://www.datacamp.com/search?q={q}",
    "Udacity": "https://www.udacity.com/catalog?searchValue={q}",
    "LeetCode": "https://leetcode.com/studyplan/",
    "GitHub": "https://github.com/search?q={q}",
    "Linux Foundation": "https://training.linuxfoundation.org/full-catalog/?_sf_s={q}",
    "Docker": "https://docs.docker.com/get-started/",
    "HashiCorp": "https://developer.hashicorp.com/tutorials",
    "PortSwigger": "https://portswigger.net/web-security",
    "TryHackMe": "https://tryhackme.com/hacktivities",
    "Figma": "https://help.figma.com/hc/en-us",
    "Unity Learn": "https://learn.unity.com/search?k={q}",
    "IBM": "https://www.ibm.com/training/search?q={q}",
    "Vercel": "https://nextjs.org/learn",
    "LangChain": "https://python.langchain.com/docs/tutorials/",
    "Pinecone": "https://www.pinecone.io/learn/",
    "Confluent": "https://developer.confluent.io/courses/",
    "dbt Labs": "https://courses.getdbt.com/collections",
    "Scrum.org": "https://www.scrum.org/courses",
    "Cisco NetAcad": "https://www.netacad.com/courses",
    "Red Hat": "https://www.redhat.com/en/services/training",
    "Grafana Labs": "https://grafana.com/tutorials/",
    "Auth0": "https://auth0.com/docs",
    "Apollo": "https://www.apollographql.com/tutorials/",
    "Expo": "https://docs.expo.dev/tutorial/introduction/",
    "Alchemy": "https://university.alchemy.com/",
    "rust-lang.org": "https://doc.rust-lang.org/book/",
    "O'Reilly": "https://www.oreilly.com/search/?q={q}",
    "Talk Python": "https://training.talkpython.fm/courses/all",
    "Karpathy": "https://karpathy.ai/zero-to-hero.html",
    "3Blue1Brown": "https://www.3blue1brown.com/topics/linear-algebra",
    "web.dev": "https://web.dev/learn",
    "spaCy": "https://course.spacy.io/en/",
    "PyImageSearch": "https://pyimagesearch.com/start-here/",
    "AlgoExpert": "https://www.algoexpert.io/product",
    "Ardan Labs": "https://www.ardanlabs.com/training/",
    "CNCF": "https://www.cncf.io/training/",
    "CodeChef": "https://www.codechef.com/practice",
    "Educative": "https://www.educative.io/search?query={q}",
    "Epic React": "https://epicreact.dev/",
    "Evidently AI": "https://www.evidentlyai.com/blog",
    "GDQuest": "https://school.gdquest.com/",
    "Mode Analytics": "https://mode.com/sql-tutorial/",
    "NN/g": "https://www.nngroup.com/courses/",
    "Pluralsight": "https://www.pluralsight.com/search?q={q}",
    "Reforge": "https://www.reforge.com/programs",
    "SANS": "https://www.sans.org/cyber-security-courses/",
    "Stanford CS193p": "https://cs193p.sites.stanford.edu/",
    "Test & Code": "https://testandcode.com/",
    "Testing Library": "https://testing-library.com/docs/",
    "Use The Index": "https://use-the-index-luke.com/",
    "Vue Mastery": "https://www.vuemastery.com/courses/",
    "Wisconsin": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
    "craftinginterpreters": "https://craftinginterpreters.com/",
}

# Co-branded providers ("Imperial/Coursera", "Google/Udacity") are hosted on the
# platform named after the slash, so fall back to that rather than losing the link.
PLATFORM_SUFFIXES = ("Coursera", "Udacity", "edX")

# Authored for this project — no external page to link to.
INTERNAL_PROVIDERS = {"PathFinder Labs"}


def resource_url(provider: str, title: str) -> str | None:
    """A search URL on the provider's own site, or None when there isn't one."""
    if provider in INTERNAL_PROVIDERS:
        return None
    template = PROVIDER_SEARCH.get(provider)
    if not template:
        for platform in PLATFORM_SUFFIXES:
            if platform.lower() in provider.lower():
                template = PROVIDER_SEARCH[platform]
                break
    if not template:
        return None
    if "{q}" not in template:
        return template
    return template.format(q=quote_plus(title))
