"""Worked example: rules vs learning (the heart of ML). Runs offline.

The chapter shows the ML side as pseudo-code (model.fit / model.predict);
here it is made runnable with a tiny scikit-learn classifier.
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


# Old way: you write the rules
def is_spam(email):
    if "lottery" in email: return True
    if "free money" in email: return True
    return False


print("Rule-based:", is_spam("You won a l0ttery!!"), "<- spammers write 'l0ttery', the rule fails")

# ML way: the model learns the rules from labelled examples
# (the chapter imagines 1 million examples; a handful is enough to see the idea)
emails = [
    "You won a l0ttery!!", "Claim your free m0ney now", "Win a fr33 prize today",
    "Congratulations, you are a lottery winner", "Cheap pr1ze, click now",
    "Meeting moved to 3pm", "Lunch tomorrow?", "Please review the attached report",
    "Your invoice for October", "Team standup notes",
]
labels = ["spam"] * 5 + ["not spam"] * 5

model = make_pipeline(CountVectorizer(analyzer="char_wb", ngram_range=(2, 4)), MultinomialNB())
model.fit(emails, labels)
print("Learned:   ", model.predict(["Claim your fr33 prize"])[0], "<- it learned the pattern itself")
