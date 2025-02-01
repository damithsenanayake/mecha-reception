# Mecha-Reception: A virtual reception for your mechanic

This is a POC for a scheduling system for a mechanic. The program will carry on a conversation with a caller and extract information necessary to schedule appointments (date, car make/model, issues etc.)

This simple implementation has a back-end Flask application, which has the main endpoint `/fill_form` which takes in an audio, parses the content in the audio for necessary information and adjusts conversation to ask user for missing information. 

## Design

The aim is to fill a predefined json form which contains information required for scheduling appointment (caller email to send the invite, desired date and time of service etc.) as well as other required information for the mechanic (rego, car make and model, issues etc.). 

The predefined json is filled as the conversation progresses. 

### Approach: STT-LLM-TTS pipeline

Out of the two possible approaches of either using a real-time voice to voice LLM vs a pipeline, I chose the pipeline approach due to the following reasons. 

#### Content Parsing

A voice-to-voice chat does not provide us with the ability to generate parseable json objects as output. Instead, one would have to call a text-generation LLM / entity extraction model to parse content out of the user input separately. However, this means that the consistency between the LLM output may not guide the conversation to make the user reveal missing information as such missing information  will have to be revealed post-hoc.

#### Custom Prompts and Query Routing

Depending on the conversational progression, one may need to alter system prompts. For instance, at the beginning/end of the conversation the default prompts may differ. A voce-to-voice API does not provide us with the ability to set system prompts similar to `chat.completions` functionality. Therefore for more complex scenarios, the multimodal LLM provides us with very limited versatility


### Tradeoffs

- The pipeline approach adds overhead of making multiple API calls
    - transcription
    - llm call to parse input
    - response generation
    - voice synthesis
    This naturally adds a delay to the conversation
- Code complexity
    - streamlining these queries require some engineering. For instance, rather than bulk generating output, one can stream the response and synthesize voice sentence by sentence. This usually means the voice synthesis output is done in smaller batches and the first sentence may be played while the others are being generated. 
- Pipeline Management
    - requires managing pipelines: conversational memory needs to be separately managed and handled

## Setup

To run this in a simple dev setup (not wsgi enabled) you need to clone this repository. Once cloned, move into the directory. 

```
$ git clone https://github.com/damithsenanayake/mecha-reception.git
$ cd MECHA-RECEPTION
```

Create the file `/path/to/repo/MECHA-RECEPTION/app/config.ini` with following content.

```
[API_KEY]
openai = your_api_key
```

Create a virtual environment.

```
python3 -m venv env
source env/bin/activate
```

Install required libraries

```
pip install -r requirements.txt
```

Run Flask application

```
python -m app.app
```

A simple web interface is provided at `http://127.0.0.1:5000`. Once browser is open, click and hold the button to record, and release to send the message. You may have to allow access to microphone on your device. 
