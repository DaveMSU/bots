import os


DB_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]
TOKEN = os.environ["GEORGE_BOT_TOKEN"]

MESSAGES_WITH_PRAISE = [
    "Good! It's right!",
    "Cool! This is the right answer!",
    "Great! You guessed it!\nOr maybe it's not accidental anymore?...)",
    "Cool, right!",
    "Another one right.",
    "Great!\nKeep going at this pace and soon you will have a vocabulary like mine.",
    "And this... the right answer!",
    "You're right!",
    "You are sooo clever, right answer!",
    "Yeah! Fantastic!",
    "Ohh, you guessed it correctly!",
    "Ohh, you are... Inevitable!",
    "Best student ever! Yeah, it's right!",
    "Good!",
    "Yeah, right!",
    "Correct!",
    "You're awesome, dude!",
    "Yes, correct answer!",
    "Yes, correct!",
    "Right!",
    "You are correct!",
    "Yes! Right answer!"
]

MESSAGES_WITH_CONDEMNATION = [
    "Uhhh.. you were wrong this time. The correct answer is \"{}\".",
    "Unfortunately, this is wrong. The correct answer was \"{}\".",
    "No, no luck this time. The answer is \"{}\".",
    "Answer is \"{}\"... but this is normal, because, as they say, \"practice makes perfect\"!",
    "No, sorry, answer is \"{}\". But keep going! Shit happens!",
    "No, unfortunately. I was expecting \"{}\".",
    "You are wrong, the answer is \"{}\"."
]
