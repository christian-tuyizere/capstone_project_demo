# Capstone Starter (Week 11): your chatbot online, every turn logged, and help when it is lost.
# app.py, requirements.txt and intent_classifier.joblib go together in the streamlit folder of
# your Portfolio Project 2 repository. "How to set up.md" says how, step by step.
#
#   PART 1. YOUR DOMAIN: your chatbot (the same as PART 1 of the Portfolio Project 2 starter).
#   PART 2. YOUR DOMAIN: THRESHOLD from Part 1. intent_classifier.joblib sits next to app.py.
#   PART 3. PROVIDED: the classifier inside the chatbot.
#   PART 4. YOUR DOMAIN: your FAQ passages, and three switches.
#   PART 5. PROVIDED: who answered each message, and the log in your Google Sheet (3.6).
#   PART 6. PROVIDED: when the chatbot is lost: the retriever and a language model (no marks).
#   PART 7. PROVIDED: the web page.
#
# Secrets (Streamlit: Manage app, Settings, Secrets), never in the repository:
#   LOG_URL = "https://script.google.com/macros/s/.../exec"     the Sheet (How to set up, B)
#   OPENROUTER_API_KEY = "sk-or-..."                             optional (How to set up, C)
#
# The worked example is the fictional City Bus Desk. It may not be submitted.


# ==============================================================================================
# PART 1. YOUR DOMAIN: your chatbot (Step 1 of the notebook). Replace the example.
# ==============================================================================================

# STEP 1. YOUR DOMAIN: your Portfolio Project 1 chatbot, pasted here.
# Replace everything below with your own chatbot: every cell from Step 1 to Step 10 of
# your Week_7_Own_Domain_Chatbot notebook, one after another.
# The worked example below is the fictional City Bus Desk.

# AITCD001, Week 7: a rule-based chatbot for a domain of my own
import re
from datetime import datetime

print("ready")


# STEP 1. YOUR DOMAIN: replace these three lines with your own.
BOT_NAME = "City Bus Desk"
USERS = "travellers buying bus tickets in Kigali"
TOPICS = "departure times, fares, luggage and booking a seat"

print(f"{BOT_NAME}: a chatbot for {USERS}.")
print(f"It can help with {TOPICS}.")


# STEP 2. YOUR DOMAIN: your intents, in priority order. At least five.
# Each rule is (intent, pattern). The first rule that matches a request wins, so put
# "cancel" above what it cancels, and the specific above the general.
# Do not add "name" or "greeting": Step 6 adds them.
RULES = [
    ("cancel",  r"\bcancel\w*\b|\bcall it off\b"),
    ("hours",   r"\bhours?\b|\bopen\w*\b|\bwhat ?time\b|\bleav\w*\b|\btimetable\b"),
    ("fares",   r"\bfares?\b|\bprices?\b|\bcosts?\b|\bhow ?much\b|\bangahe\b"),
    ("luggage", r"\bluggage\b|\bbags?\b|\bsuitcases?\b|\bparcels?\b"),
    ("book",    r"\bbook\w*\b|\breserv\w*\b|\btickets?\b|\bseats?\b"),
]

print(len(RULES), "intents in the rule table")


# STEP 3. PROVIDED: cleaning, matching, and several requests in one message (Weeks 3 to 5).
def normalise(text):
    """Remove punctuation (keeping the colon of 21:00), lowercase, trim."""
    return re.sub(r"[^\w\s:]", "", text).lower().strip()


def match(message):
    """The tag of the first rule that matches, or "fallback"."""
    text = normalise(message)
    for tag, pattern in RULES:
        if re.search(pattern, text):
            return tag
    return "fallback"


CONNECTORS = r"\band\b|\bbut\b|\balso\b|\bthen\b|[?]"


def split_requests(message):
    """Break one message into the separate requests it contains."""
    requests = []
    for part in re.split(CONNECTORS, message.lower()):
        part = normalise(part)
        if part != "":
            requests.append(part)
    return requests


def route(message):
    """One (intent, request) pair for each request understood."""
    found = []
    seen = []
    for request in split_requests(message):
        tag = match(request)
        if tag != "fallback" and tag not in seen:
            seen.append(tag)
            found.append((tag, request))
    return found


print(route("what time do buses leave and how much is a ticket"))


# STEP 4. YOUR DOMAIN: one handler per intent, then the router.
FARES = {"huye": "3,000 RWF", "musanze": "2,500 RWF",
         "rubavu": "4,000 RWF", "nyagatare": "3,500 RWF"}
PLACES = r"\b(" + "|".join(FARES) + r")\b"     # \b(huye|musanze|rubavu|nyagatare)\b


def handle_hours(text):
    return "Buses leave every hour, 06:00 to 18:00, every day."


def handle_fares(text):
    """Reads the message: the fare to the town named, if it is one we serve."""
    found = re.search(PLACES, text)
    if found:
        town = found.group(1)
        return f"A ticket to {town.capitalize()} is {FARES[town]}."
    return "Huye 3,000 RWF, Musanze 2,500, Rubavu 4,000, Nyagatare 3,500."


def handle_luggage(text):
    return "One bag up to 20 kg travels free. Each extra bag is 500 RWF."


def handle_book(text):
    """Starts the booking conversation (Step 5)."""
    if flow["step"] is not None:
        return "Your booking is already under way."
    return start_flow()


def handle_cancel(text):
    if flow["step"] is not None:
        reset_flow()
        return "Your booking has been cancelled. Nothing was booked."
    return "There is no booking in progress to cancel."


HANDLERS = {
    "cancel":  handle_cancel,
    "hours":   handle_hours,
    "fares":   handle_fares,
    "luggage": handle_luggage,
    "book":    handle_book,
}
ASKS = ["book"]       # intents whose reply is a question: it goes last

for tag, pattern in RULES:
    if tag not in HANDLERS:
        print("No handler for:", tag)
print(len(HANDLERS), "intents routed")


# STEP 5a. YOUR DOMAIN: the questions your ONE conversation asks, in order.
# Each step is (what to remember, the question, the pattern of a valid answer).
FLOW_STEPS = [
    ("destination", "Where to? Huye, Musanze, Rubavu or Nyagatare?", PLACES),
    ("day",         "Which day? Today or tomorrow?", r"\b(today|tomorrow)\b"),
    ("time",        "Morning, afternoon or evening?", r"\b(morning|afternoon|evening)\b"),
]
DONE = "Booked: "                                  # said after "yes"
NOT_DONE = "No problem. Nothing has been booked."  # said after "no"

print(len(FLOW_STEPS), "questions, then a confirmation")


# STEP 5b. PROVIDED: the flow (Weeks 4 and 5), now driven by FLOW_STEPS,
# and ending with a real confirmation: nothing is done until the user says yes.
flow = {"step": None, "collected": {}}
YES = r"\b(yes|yeah|yego|correct|ok|okay)\b"     # yego: yes
NO = r"\b(no|nope|oya|wrong)\b"                  # oya: no


def start_flow():
    flow["step"] = 0
    flow["collected"] = {}
    return FLOW_STEPS[0][1]


def reset_flow():
    flow["step"] = None
    flow["collected"] = {}


def summary():
    return ", ".join(flow["collected"].values())


def continue_flow(message):
    """One answer: store it, ask the next question, and at the end, confirm."""
    text = normalise(message)
    if flow["step"] == "confirm":
        if re.search(YES, text):
            booked = summary()
            reset_flow()
            return DONE + booked + ". Thank you."
        if re.search(NO, text):
            reset_flow()
            return NOT_DONE
        return "Please answer yes or no."
    name, question, pattern = FLOW_STEPS[flow["step"]]
    found = re.search(pattern, text)
    if not found:
        return question                          # not a valid answer: ask again
    flow["collected"][name] = found.group()
    flow["step"] = flow["step"] + 1
    if flow["step"] < len(FLOW_STEPS):
        return FLOW_STEPS[flow["step"]][1]       # the next question
    flow["step"] = "confirm"
    return "So: " + summary() + ". Shall I book it? Yes or no."


print("Bot:", start_flow())
for answer in ["huye please", "tomorrow", "in the morning", "yes"]:
    print("You:", answer)
    print("Bot:", continue_flow(answer))


# STEP 6. PROVIDED, except FOLLOW_UPS: memory, a name, a greeting, follow ups (Week 5).
# Run this cell ONCE: it adds the name and greeting rules to RULES.
context = {"name": None, "last_intent": None, "fallbacks": 0}


def reset_context():
    context["name"] = None
    context["last_intent"] = None
    context["fallbacks"] = 0


NAME = r"\bmy name is (\w+)"


def handle_name(text):
    found = re.search(NAME, text)
    if found:
        context["name"] = found.group(1).capitalize()
        return f"Nice to meet you, {context['name']}."
    return "Sorry, I did not catch your name."


def handle_greeting(text):
    if context["name"] is not None:
        return f"Muraho, {context['name']}! How can I help?"
    return (f"Muraho! I am the {BOT_NAME} assistant, a computer program. "
            f"I can help with {TOPICS}.")


RULES.insert(0, ("name", r"\bmy name is\b"))
RULES.append(("greeting", r"\bhello\b|\bhi\b|\bhey\b|\bmuraho\b|\bmwaramutse\b|\bmwiriwe\b"))
HANDLERS["name"] = handle_name
HANDLERS["greeting"] = handle_greeting

# YOUR DOMAIN: an intent, and the pattern that continues it ("and musanze?" after a fare).
FOLLOW_UPS = {"fares": PLACES}


def follow_up(text):
    """A message with no intent of its own, read in the light of the last one."""
    last = context["last_intent"]
    if last in FOLLOW_UPS and re.search(FOLLOW_UPS[last], text):
        return [(last, text)]
    return []


print(len(RULES), "rules,", len(HANDLERS), "intents routed")


# STEP 7. PROVIDED: validation, errors, the fallback and a person (Week 6).
MAX_LENGTH = 300
ASK_AGAIN = f"Please type a question. I can help with {TOPICS}."
IN_WORDS = "Please type your question in words."
TOO_LONG = "That is a long message. Could you ask one thing at a time?"


def validate(message):
    """Return a reply if the message cannot be used; None if it can."""
    if message is None:
        return ASK_AGAIN
    text = message.strip()
    if text == "":
        return ASK_AGAIN
    if normalise(text) == "":
        return IN_WORDS
    if len(text) > MAX_LENGTH:
        return TOO_LONG
    return None


ERROR_LOG = []
SORRY = "Sorry, something went wrong on my side. Please try again, or type 'human'."


def log_error(message, error):
    ERROR_LOG.append({"time": datetime.now().strftime("%H:%M:%S"), "message": message,
                      "error": type(error).__name__ + ": " + str(error)})


def safe_handle(tag, request):
    """Run one handler. If it raises an error, log it and apologise instead of crashing."""
    try:
        return HANDLERS[tag](request)
    except Exception as error:
        log_error(request, error)
        return SORRY


def respond(found):
    """Answer every request found; a reply that asks a question goes last."""
    answers = []
    questions = []
    for tag, request in found:
        reply = safe_handle(tag, request)
        if tag in ASKS:
            questions.append(reply)
        else:
            answers.append(reply)
    return " ".join(answers + questions)


UNMATCHED = []
FALLBACK = f"Sorry, I did not understand. I can help with {TOPICS}."
STILL_LOST = f"Sorry, I still did not understand. Type 'human' for a member of staff, or ask about {TOPICS}."


def fallback(message):
    UNMATCHED.append(message)
    context["fallbacks"] = context["fallbacks"] + 1
    if context["fallbacks"] >= 2:
        return STILL_LOST
    return FALLBACK


EXIT_WORDS = ("bye", "goodbye", "exit", "quit", "thanks", "murakoze")
HUMAN_WORDS = ("human", "staff", "agent", "person")
HANDOVER = "Connecting you to a member of staff. They can see this conversation."

print("validation, error handling and the fallback are ready")


# STEP 7, continued. PROVIDED: one complete turn, in the Week 6 order.
def reply_to(message):
    problem = validate(message)                  # 0. unusable input
    if problem is not None:
        return problem
    text = normalise(message)

    if text in EXIT_WORDS:                       # 1. the exit, at any point
        name = context["name"]
        reset_flow()
        reset_context()
        if name is not None:
            return f"Thank you, {name}. Murakoze."
        return "Thank you for contacting us. Murakoze."

    if text in HUMAN_WORDS:                      # 2. a person, at any point
        reset_flow()
        return HANDOVER

    if flow["step"] is not None:                 # 3. the flow sees it first
        step_before = flow["step"]
        flow_reply = continue_flow(message)
        if flow["step"] != step_before:
            return flow_reply
        found = route(message)
        if len(found) == 0:
            return flow_reply
        reply = respond(found)
        if flow["step"] is not None:
            reply = reply + " " + flow_reply
        return reply

    found = route(message)                       # 4. route
    if len(found) == 0:
        found = follow_up(text)                  # 5. a follow up
    if len(found) == 0:
        return fallback(message)                 # 6. the fallback, counted

    context["fallbacks"] = 0
    last_tag, last_request = found[-1]
    context["last_intent"] = last_tag
    return respond(found)


def run_conversation(turns):
    """Play a conversation from a clean start, printing both sides."""
    reset_flow()
    reset_context()
    for message in turns:
        print("You:", message)
        print("Bot:", reply_to(message))
    print()


run_conversation(["muraho", "how much is a ticket to huye", "and musanze?", "bye"])


# STEP 8. YOUR DOMAIN: ten test conversations. Write what you EXPECT on paper first.
# Include local phrasing, unexpected input, and one you think will break the chatbot.
TESTS = [
    ('A greeting, a name, a goodbye',
     ['muraho', 'my name is aline', 'bye']),
    ('Two requests in one message',
     ['what time do buses leave and how much is a ticket to huye']),
    ('A booking, confirmed',
     ['i would like to book a seat', 'huye', 'tomorrow', 'morning', 'yes']),
    ('A booking, refused at the end',
     ['book a seat', 'rubavu', 'today', 'evening', 'no']),
    ('A side question during the booking',
     ['book a seat', 'musanze', 'can i bring two bags', 'today']),
    ('Cancelling halfway',
     ['book a seat', 'nyagatare', 'cancel']),
    ('A follow up',
     ['how much to musanze', 'and huye?']),
    ('Unexpected input, then a person',
     ['', 'asdfgh', 'qwerty', 'human']),
    ('Local phrasing',
     ['ni angahe huye', 'murakoze']),
    ('A booking with the town already given',
     ['book a ticket to huye']),
]

number = 1
for title, turns in TESTS:
    print(f"Test {number}: {title}")
    run_conversation(turns)
    number = number + 1


# STEP 9. Refine: test 10 failed. The booking handler ignored the town in the request.
# The change: after starting the flow, use every answer the request already contains.
def handle_book(text):
    """Refined after test 10: answers already in the request are used."""
    if flow["step"] is not None:
        return "Your booking is already under way."
    reply = start_flow()
    while flow["step"] != "confirm":
        pattern = FLOW_STEPS[flow["step"]][2]     # the current question's pattern
        if not re.search(pattern, text):
            break                                 # the request does not answer it: ask
        reply = continue_flow(text)               # it does: answer it, and go on
    return reply


HANDLERS["book"] = handle_book      # the router keeps the old function until this line

title, turns = TESTS[9]
print("Test 10 again:", title)
run_conversation(turns)


# STEP 10. YOUR DOMAIN: messages written the way your users really write:
# Kinyarwanda, mixed, SMS spelling. Then see which ones end up in UNMATCHED.
PHRASING = [
    'ni angahe huye',
    'muraho, how much to rubavu',
    'wat tym bus leav',
    'hw much 4 musanze',
    'book seat 2moro',
    'cancle',
]


def not_understood(messages):
    """Run each message from a clean start. Return the ones that ended up in UNMATCHED."""
    missed = []
    for message in messages:
        reset_flow()
        reset_context()
        before = len(UNMATCHED)
        reply_to(message)
        if len(UNMATCHED) > before:
            missed.append(message)
    reset_flow()
    reset_context()
    return missed


missed = not_understood(PHRASING)
print(len(missed), "of", len(PHRASING), "not understood:", missed)


# ==============================================================================================
# PART 2. YOUR DOMAIN: the classifier from Part 1, and the threshold you chose there.
# ==============================================================================================

# STEP 2. YOUR DOMAIN: the classifier from Part 1, and the threshold you chose there.
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

THRESHOLD = 0.2      # YOUR DOMAIN: Part 1, Step 6

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "intent_classifier.joblib")

if os.path.exists(MODEL_PATH):
    classifier = joblib.load(MODEL_PATH)
    print("Loaded intent_classifier.joblib")
else:
    print("intent_classifier.joblib NOT FOUND: the worked example is used. It may not be submitted.")
    EXAMPLE = [('what time does the first bus leave', 'hours'), ('bus to huye leaves when', 'hours'), ('saa ngahe bus igenda?', 'hours'), ('wen is the last bus', 'hours'), ('are you open on sunday', 'hours'), ('timetable pls', 'hours'), ('when does the office open', 'hours'), ('last bus to musanze tonight?', 'hours'), ('what time do you close', 'hours'), ('is there a bus at 6am', 'hours'), ('bus igenda saa ngahe ejo', 'hours'), ('r u open today', 'hours'), ('how early do buses start', 'hours'), ('departure times please', 'hours'), ('when is the next bus', 'hours'), ('how much to musanze', 'fares'), ('ticket price for rubavu?', 'fares'), ('itike ya huye ni angahe', 'fares'), ('hw mch 2 nyagatare', 'fares'), ('is there a student discount', 'fares'), ('what does a ticket cost', 'fares'), ('price to huye pls', 'fares'), ('how much is a return ticket', 'fares'), ('fare for a child', 'fares'), ('itike ni angahe', 'fares'), ('is the fare cheaper at night', 'fares'), ('cost of a ticket to rubavu', 'fares'), ('how many francs to musanze', 'fares'), ('fares list', 'fares'), ('do kids pay full price', 'fares'), ('can i bring two bags', 'luggage'), ('how heavy can my suitcase be', 'luggage'), ('is the bag fee extra', 'luggage'), ('can i carry a bicycle', 'luggage'), ('imizigo yemewe ni ingahe?', 'luggage'), ('i have a big box, is that ok', 'luggage'), ('luggage limit?', 'luggage'), ('can i take a sack of potatoes', 'luggage'), ('is there space for a suitcase', 'luggage'), ('do you charge for bags', 'luggage'), ('can i bring my guitar', 'luggage'), ('how many bags allowed', 'luggage'), ('big luggage ok?', 'luggage'), ('nfite imizigo myinshi', 'luggage'), ('can i send a parcel on the bus', 'luggage'), ('book a seat to huye', 'book'), ('i want to travel to musanze tomorrow', 'book'), ('reserve 2 seats for rubavu', 'book'), ('ndashaka itike ya huye', 'book'), ('get me on the morning bus', 'book'), ('can i book for friday', 'book'), ('one ticket to nyagatare please', 'book'), ('i need a seat on the 8am bus', 'book'), ('book me to rubavu', 'book'), ('reserve a ticket for sunday', 'book'), ('ndashaka kujya musanze', 'book'), ('two tickets to huye today', 'book'), ('can i get a seat tonight', 'book'), ('i want to go to rubavu on saturday', 'book'), ('booking for 3 people', 'book'), ('cancel my booking', 'cancel'), ('i cant travel anymore', 'cancel'), ('call off my seat', 'cancel'), ('ndashaka guhagarika itike', 'cancel'), ('i want my money back', 'cancel'), ('cancle the ticket', 'cancel'), ('cancel my seat to huye', 'cancel'), ('refund please', 'cancel'), ('i will not travel', 'cancel'), ('drop my booking', 'cancel'), ('cancel the trip', 'cancel'), ('hagarika itike yanjye', 'cancel'), ('i changed my plans, cancel', 'cancel'), ('stop my reservation', 'cancel'), ('cancl my ticket', 'cancel'), ('i lost my phone on the bus', 'out_of_scope'), ('are you hiring drivers', 'out_of_scope'), ('the driver was rude', 'out_of_scope'), ('can i pay with momo', 'out_of_scope'), ('who won the match', 'out_of_scope'), ('asdfgh', 'out_of_scope'), ('where is the bus park', 'out_of_scope'), ('the bus was dirty', 'out_of_scope'), ('i want to speak to the manager', 'out_of_scope'), ('tell me a joke', 'out_of_scope'), ('is there wifi on the bus', 'out_of_scope'), ('my seat was broken', 'out_of_scope'), ('ok', 'out_of_scope'), ('what is your name', 'out_of_scope'), ('i left my bag on the bus', 'out_of_scope')]
    classifier = make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)),
                               LogisticRegression(max_iter=1000))
    classifier.fit([t for t, _ in EXAMPLE], [i for _, i in EXAMPLE])


def classify(text):
    """The intent with the highest score, and that score."""
    scores = classifier.predict_proba([text])[0]
    best = scores.argmax()
    return str(classifier.classes_[best]), float(scores[best])


print("intents:", list(classifier.classes_))


# ==============================================================================================
# PART 3. PROVIDED: the classifier inside the chatbot.
# ==============================================================================================

# STEP 3. PROVIDED: the classifier inside the chatbot (Week 9's hybrid, for any chatbot).
if "route_rules" not in globals():     # run again safely: keep the original rules
    route_rules = route


def route(message):
    """Rules keep the intents the classifier never learned; the classifier picks the rest."""
    found = []
    for request in split_requests(message):
        tag = None
        rule_only = [t for t, _ in route_rules(request) if t not in classifier.classes_]
        if rule_only:
            tag = rule_only[0]
        else:
            intent, score = classify(request)
            if score >= THRESHOLD and intent != "out_of_scope":
                tag = intent
        if tag in HANDLERS and tag not in [t for t, _ in found]:
            found.append((tag, request))
    return found              # empty: the chatbot's own fallback answers


# ==============================================================================================
# PART 4. YOUR DOMAIN: your FAQ passages, and three switches.
# ==============================================================================================

# Short answers to questions your intents do not cover (Week 9's retriever). Two to fifteen
# passages, each (topic, answer). Write facts only: the model may repeat them word for word.
FAQ = [
    ("Payment", "Tickets are paid in cash at the desk, or with MTN MoMo or Airtel Money. "
                "Cards are not accepted."),
    ("Bus park", "Buses leave from Nyabugogo bus park, platform 4. The desk is next to the "
                 "main gate."),
    ("Lost property", "Items left on a bus are kept at the desk for 30 days. Bring the ticket "
                      "to collect them."),
    ("Wifi", "There is no wifi on the buses. Every seat has a phone charger."),
    ("Complaints", "Complaints about a driver or a bus are written in the complaints book at "
                   "the desk and answered within 24 hours."),
]

USE_RAG = True     # look for the closest FAQ passage when the chatbot is lost
USE_LLM = True     # ask a language model (only if OPENROUTER_API_KEY is in the secrets)
SHOW_WHO = True    # show "answered by" under each reply: useful in the demonstration


# ==============================================================================================
# PART 5. PROVIDED: who answered each message, and the log in your Google Sheet.
# ==============================================================================================
import uuid
import requests
import streamlit as st


def secret(name):
    """A value from the app's secrets, or None when it is not there."""
    try:
        return st.secrets[name]
    except Exception:
        return None


LOG_URL = secret("LOG_URL")
COLUMNS = ["time", "user", "turn", "message", "intent", "confidence", "answered_by", "reply",
           "feedback"]


def who_answered(message, flow_before, lost):
    """Which part of the chatbot produced the reply."""
    if lost:
        return "fallback"
    if flow_before is not None:
        return "flow"
    if route_rules(message):
        return "rules"
    if route(message):
        return "classifier"
    return "rules"          # an exit word, a person, a follow up, unusable input


def log_turn(row):
    """Send one row to the Google Sheet. It never stops the chatbot: False if not saved."""
    if not LOG_URL:
        return False
    try:
        answer = requests.post(LOG_URL, json=row, timeout=10)
        return answer.ok and answer.text.strip() == "ok"
    except Exception as error:
        log_error("log_turn", error)
        return False


# ==============================================================================================
# PART 6. PROVIDED: when the chatbot is lost (Element 4: taught, not examined, no marks).
# ==============================================================================================
from sklearn.metrics.pairwise import cosine_similarity

MIN_SCORE = 0.2
finder = TfidfVectorizer(stop_words="english")
passages = [topic + ". " + answer for topic, answer in FAQ]
passage_vectors = finder.fit_transform(passages)


def retrieve(question):
    """The closest FAQ answer, and how close it is (Week 9)."""
    q = finder.transform([question])
    scores = cosine_similarity(q, passage_vectors)[0]
    best = scores.argmax()
    return float(scores[best]), FAQ[best][1]


MODELS = ["liquid/lfm-2.5-2.6b:free",     # the model of Week 10
          "google/gemma-4-31b-it:free",   # if the first is busy or gone
          "openrouter/free"]              # OpenRouter picks any free model
SYSTEM = (f"You are the assistant of {BOT_NAME}, a chatbot for {USERS}. "
          f"Answer in at most two sentences. Only talk about {TOPICS}.")
ALL_FACTS = " ".join(answer for topic, answer in FAQ)

client = None
if USE_LLM and secret("OPENROUTER_API_KEY"):
    from openai import OpenAI
    client = OpenAI(base_url="https://openrouter.ai/api/v1",
                    api_key=secret("OPENROUTER_API_KEY"))


def ask_llm(message, facts):
    """The model's answer from these facts only, or None (no key, no network, the limit)."""
    if client is None:
        return None
    grounded = (SYSTEM + " Use ONLY these facts. If the answer is not in them, say you do "
                "not know. Facts: " + facts)
    for model in MODELS:
        try:
            completion = client.chat.completions.create(
                model=model, timeout=20,
                messages=[{"role": "system", "content": grounded},
                          {"role": "user", "content": message}])
            answer = completion.choices[0].message.content
            if answer:
                return answer.strip()
        except Exception as error:      # busy, removed, 50 a day reached: try the next one
            log_error(message, error)
    return None


def answer_when_lost(message, fallback_reply):
    """RAG first, then the model on all the facts, then the chatbot's own fallback."""
    if USE_RAG:
        score, passage = retrieve(message)
        if score >= MIN_SCORE:
            answer = ask_llm(message, passage)       # RAG: retrieve, then generate
            if answer:
                return answer, "rag"
            return passage, "retriever"              # no model: the passage itself
    if USE_LLM:
        answer = ask_llm(message, ALL_FACTS)
        if answer:
            return answer, "llm"
    return fallback_reply, "fallback"


HELPED = ("rag", "retriever", "llm")


# ==============================================================================================
# PART 7. PROVIDED: the web page.
# ==============================================================================================
st.set_page_config(page_title=BOT_NAME, page_icon="💬")
st.title(BOT_NAME)
st.caption(f"Hello! I am the {BOT_NAME} assistant: a computer program. "
           f"I can help with {TOPICS}.")
st.caption("Messages are recorded to improve this chatbot. Please do not type names, phone "
           "numbers or ID numbers.")
if not os.path.exists(MODEL_PATH):
    st.warning("intent_classifier.joblib is not next to app.py: the worked example's "
               "classifier is in use. It may not be submitted.")

ss = st.session_state
if "history" not in ss:
    ss.history = []                  # this visitor's turns: (who, text, answered_by)
    ss.user = uuid.uuid4().hex[:10]  # a random code per visitor, never a name or a number
    ss.unsaved = 0


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_feedback(turn):
    value = ss.get(f"fb_{turn}")
    if value is None:
        return
    row = {"time": now(), "user": ss.user, "turn": turn,
           "feedback": "👍" if value == 1 else "👎"}
    if not log_turn(row):
        ss.unsaved += 1


message = st.chat_input("Type a message")
if message:
    # Streamlit runs this whole file again for every message, so the chatbot's memory starts
    # empty each time. Replaying THIS visitor's earlier messages rebuilds their conversation.
    # The replay uses the chatbot only: the language model is never asked twice.
    reset_flow()
    reset_context()
    for who, text, by in ss.history:
        if who == "user":
            reply_to(text)
            if by in HELPED:
                context["fallbacks"] = 0
    flow_before = flow["step"]
    lost_before = len(UNMATCHED)
    answer = reply_to(message)
    lost = len(UNMATCHED) > lost_before
    by = who_answered(message, flow_before, lost)
    if lost:
        answer, by = answer_when_lost(message, answer)
    intent, confidence = classify(normalise(message))
    turn = len(ss.history) // 2 + 1
    ss.history.append(("user", message, by))
    ss.history.append(("assistant", answer, by))
    row = {"time": now(), "user": ss.user, "turn": turn, "message": message,
           "intent": intent, "confidence": round(confidence, 2), "answered_by": by,
           "reply": answer, "feedback": ""}
    if not log_turn(row):
        ss.unsaved += 1

for i, (who, text, by) in enumerate(ss.history):
    with st.chat_message(who):
        st.write(text)
        if who == "assistant":
            if SHOW_WHO:
                st.caption(f"answered by: {by}")
            turn = i // 2 + 1
            st.feedback("thumbs", key=f"fb_{turn}", on_change=send_feedback, args=(turn,))

if not LOG_URL:
    st.info("The log is off: LOG_URL is not in this app's secrets, so nothing is saved.")
elif ss.unsaved:
    st.warning(f"{ss.unsaved} rows could not be saved to the Google Sheet.")
