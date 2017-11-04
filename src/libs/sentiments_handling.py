# Groups
SAD = "sad"
ANGRY = "angry"
HAPPY = "happy"

# Sentiments
CONFLICT_SA = "conflict_sa"
CONFLICT_FA = "conflict_fa"
CONFLICT_TD = "conflict_td"
CONFLICT_JS = "conflict_js"
ANXIETY = "anxiety"
DOMINANCE = "dominance"
MORBIDNESS = "morbidness"
PESSIMISM = "pessimism"
OUTRAGE = "outrage"
SHAME = "shame"
SENTIMENTALITY = "sentimentality"
DELIGHT = "delight"
FATALISM = "fatalism"
PRIDE = "pride"
CYNISM = "cynism"
ENVY = "envy"
DESPAIR = "despair"
CURIOSITY = "curiosity"
GUILT = "guilt"
OPTIMISM = "optimism"
AGGRESSION = "aggression"
CONTEMPT = "contempt"
REMORSE = "remorse"
DISAPPOINTMENT = "disappointment"
ALARM = "alarm"
SUBMISSION = "submission"

# Emotions
NONE = "none"
ANTICIPATION = "anticipation"
ANGER = "anger"
DISGUST = "disgust"
SADNESS = "sadness"
SURPRISE = "surprise"
FEAR = "fear"
LOVE = "love"
TRUST = "trust"
JOY = "joy"
NEUTRAL = "neutral"

DYADS = {
    (JOY, TRUST): LOVE,
    (TRUST, FEAR): SUBMISSION,
    (FEAR, SURPRISE): ALARM,
    (SURPRISE, SADNESS): DISAPPOINTMENT,
    (SADNESS, DISGUST): REMORSE,
    (DISGUST, ANGER): CONTEMPT,
    (ANGER, ANTICIPATION): AGGRESSION,
    (ANTICIPATION, JOY): OPTIMISM,
    (JOY, FEAR): GUILT,
    (TRUST, SURPRISE): CURIOSITY,
    (FEAR, SADNESS): DESPAIR,
    (SADNESS, ANGER): ENVY,
    (DISGUST, ANTICIPATION): CYNISM,
    (JOY, ANGER): PRIDE,
    (TRUST, ANTICIPATION): FATALISM,
    (JOY, SURPRISE): DELIGHT,
    (TRUST, SADNESS): SENTIMENTALITY,
    (FEAR, DISGUST): SHAME,
    (SURPRISE, ANGER): OUTRAGE,
    (SADNESS, ANTICIPATION): PESSIMISM,
    (JOY, DISGUST): MORBIDNESS,
    (TRUST, ANGER): DOMINANCE,
    (FEAR, ANTICIPATION): ANXIETY,
    (JOY, SADNESS): CONFLICT_JS,
    (TRUST, DISGUST): CONFLICT_TD,
    (FEAR, ANGER): CONFLICT_FA,
    (SURPRISE, ANTICIPATION): CONFLICT_SA,
    (NONE, NONE): NONE
}

GROUPS = {
    LOVE: HAPPY,
    OPTIMISM: HAPPY,
    PRIDE: HAPPY,
    DELIGHT: HAPPY,

    ALARM: ANGRY,
    CONTEMPT: ANGRY,
    AGGRESSION: ANGRY,
    ENVY: ANGRY,
    CYNISM: ANGRY,
    OUTRAGE: ANGRY,
    ANXIETY: ANGRY,

    DISAPPOINTMENT: SAD,
    REMORSE: SAD,
    GUILT: SAD,
    DESPAIR: SAD,
    FATALISM: SAD,
    SENTIMENTALITY: SAD,
    SHAME: SAD,
    PESSIMISM: SAD,

    CONFLICT_SA: NONE,
    CONFLICT_FA: NONE,
    CONFLICT_TD: NONE,
    CONFLICT_JS: NONE,
    DOMINANCE: NONE,
    MORBIDNESS: NONE,
    SUBMISSION: NONE,
    CURIOSITY: NONE,

    NONE: NONE
}


def get_sentiment(emotion_a, emotion_b):
    """Given 2 emotions, returns the associated sentiment.
    If there is no match, returns an empty string."""
    if not (emotion_a, emotion_b) in DYADS:
        return DYADS.get((emotion_b, emotion_a), "")
    else:
        return DYADS.get((emotion_a, emotion_b), "")


def get_sentiment_emotions(sentiment):
    """Given a sentiment, returns the associated emotions
    in form of a tuple. If there is not such sentiment,
    returns an empty list."""
    for emotions, stored_sentiment in DYADS.items():
        if stored_sentiment == sentiment:
            return emotions

    return []
