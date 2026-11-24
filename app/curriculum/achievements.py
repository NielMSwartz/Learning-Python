"""Achievement definitions. Progress evaluation lives in app/services/progress.py."""

ACHIEVEMENTS = [
    ("first-steps", "First Steps", "Complete your first learning activity.", "🌱"),
    ("project-novice", "Project Novice", "Complete your first project.", "🔨"),
    ("project-builder", "Project Builder", "Complete five projects.", "🏗️"),
    ("project-master", "Project Master", "Complete fifteen projects.", "🏆"),
    ("challenge-hunter", "Challenge Hunter", "Complete ten coding challenges.", "🎯"),
    ("perfect-score", "Flawless", "Score 100% on five submissions.", "💯"),
    ("streak-7", "Seven Day Streak", " practise on seven consecutive days.", "🔥"),
    ("streak-30", "Thirty Day Streak", "Practise on thirty consecutive days.", "🌞"),
    ("code-marathon", "Code Marathon", "Accumulate one hour of coding time.", "⏱️"),
    ("library-reader", "Knowledge Seeker", "Complete ten practice exercises.", "📚"),
    ("snippet-collector", "Snippet Collector", "Save ten useful snippets.", "🧩"),
    ("all-levels", "Academy Graduate", "Reach the Professional Development level.", "🎓"),
]

# Fix a stray leading space in one description while keeping the table readable.
ACHIEVEMENTS = [
    (code, name, description.strip(), icon) for code, name, description, icon in ACHIEVEMENTS
]
