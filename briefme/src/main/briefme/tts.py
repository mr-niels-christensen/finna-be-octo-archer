class SpeechSynthesisUtterances(object):
    '''Converts a list of paragraphs into a sequence
       of SpeechSynthesisUtterance attribute dicts.
       See https://dvcs.w3.org/hg/speech-api/raw-file/tip/speechapi.html#utterance-attributes
    '''
    def __init__(self, name):
        '''@param name: A name used to annotate every SpeechSynthesisUtterance
        '''
        self._utterances = []
        self._name = name

    def append(self, paragraph, emphasized = False):
        '''Appends utterances representing the given paragraph.
           See http://updates.html5rocks.com/2014/01/Web-apps-that-talk---Introduction-to-the-Speech-Synthesis-API
           Dodge https://code.google.com/p/chromium/issues/detail?id=369472
           @param paragraph: Text to add SpeechSynthesisUtterances for,
           e.g. "This is a dog. This is a cat."
           @param emphasized: If True, the SpeechSynthesisUtterances will
           use a slightly higher pitch to emphasize the text.
        '''
        pitch = 1.15 if emphasized else 1.0
        for sentence in paragraph.split('.'): #TODO: Handle !? etc
            if len(sentence) > 2 and len(sentence) < 300: #TODO Handle these better
                self._utterances.append({'text': sentence, 
                                         'pitch': pitch,
                                         'rate': 1.0,
                                         '_name': self._name,
                                         '_index': len(self._utterances)})

    def as_list(self):
        '''@return A list of dicts, each one specifying the utterance-attributes
           of a SpeechSynthesisUtterance object, e.g.
           {'text': "This is a dog"., 
            'pitch': 1.15,
            'rate': 1.0,
            '_name': "Dog talk",
            '_index': 37}
            Note that each utterance is indexed and named.
        '''
        return self._utterances


