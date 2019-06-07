# export GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Desktop/natural-lang-key.json"
import os


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Desktop/natural-lang-key.json"

##GOOGLE_APPLICATION_CREDENTIALS="/home/pi/Desktop/natural-lang-key.json"

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums as l_enums
from google.cloud.language import types as l_types



# Instantiates a client
client = language.LanguageServiceClient()

# The text to analyze
text = 'Oh god i am so stressful with my tests. They are next week. '
document = l_types.Document(
    content=text,
    type=l_enums.Document.Type.PLAIN_TEXT)

# Detects the sentiment of the text
sentiment = client.analyze_sentiment(document=document).document_sentiment

print('Text: {}'.format(text))
print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
