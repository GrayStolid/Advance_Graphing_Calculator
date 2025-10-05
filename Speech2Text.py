from abc import ABC, abstractmethod
from word2number import w2n
import vosk
import pyaudio
import json

# Convert numerical words to mathematical expresions
class WordsToMathX(ABC):
    
    @abstractmethod
    def sen_to_math_m(self, sentence_v):
        pass
    
# Convert English numerical words to mathematical expresions
class EngToMathX(WordsToMathX):

    def __init__(self):
        # Dictionary of operators
        self.Oper_Dic_v = {"plus": '+', "add": '+', "sum": '+', "minus": '-',
                           "subtract": '-', "multiplied by": '*', "times": '*',
                           "product": '*', "“multiply": '*', "divided by": '/',
                           "to the power of": "^", "power": '^',
                           "root of": '√', "is equal to": '=', "of": "func",
                           "open parenthesis": '(',
                           "close  parenthesis": '(',  "open bracket": '[',
                           "close  bracket": ']', "eggs": "x", "aches": "x",
                           "why": "y", "zed": "z", "zip": "z"}
        self.Numb_Dic_v = {"to": "two", "tree": "three", "for": "four"}
        self.math_exp_v = ""

    def sen_to_math_m(self, sentence_v):
        sentence_v = sentence_v.split()
        for i in range(0, len(sentence_v)):
            try:
                sentence_v[i] = self.Oper_Dic_v[sentence_v[i]]
            except:
                print(f"{sentence_v[i]} in the expresion didn't"
                           " find in Operator keys!")
                try:
                    sentence_v[i] = self.Numb_Dic_v[sentence_v[i]]
                except:
                    print(f"{sentence_v[i]} in the expresion didn't"
                           " find in false ditected number keys!")
                
        buffer_v1, buffer_v2 = "", ""
        operator_list_v = self.Oper_Dic_v.values()
        for i in range(0, len(sentence_v)):
            word_v = sentence_v[i]

            if word_v in operator_list_v:
                try:
                    print("In THe end ", word_v)
                    buffer_v2 += str(w2n.word_to_num(buffer_v1)) + word_v
                    
                except:
                    if buffer_v1 == "":
                        buffer_v2 += word_v
                buffer_v1 = ""
            elif i != (len(sentence_v)-1):
                buffer_v1 +=  " " + word_v
            else:
                try:
                    buffer_v2 += str(w2n.word_to_num(buffer_v1 + " " + word_v))
                    
                except:
                    pass
        self.math_exp_v = buffer_v2
        return self.math_exp_v

def main():  
    # Set the model path vosk-model-small-fa-0.42
    model_path_v = "_internal\\vosk-model-small-en-us-0.15"
    # Initialize the model with model-path
    vosk_model_v = vosk.Model(model_path_v)

    # Create a recognizer
    vosk_speech2text_v = vosk.KaldiRecognizer(vosk_model_v, 16000)

    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16, channels = 1,
                    rate = 16000, input = True,
                    frames_per_buffer = 8192)

    # Specify the path for the output text file
    #out_file_path = "recognized_text.txt"

    # list of converted audio to expresion
    audi_to_tex_resul = []
    
    # Open a text file in write mode using a 'with' block
    #with open(out_file_path, "wt", encoding = 'utf_8') as output_file:
    print("Listening for speech. Say 'Terminate' to stop.")
    # Start streaming and recognize speech
    while True:
        data = stream.read(4096) # Read in chunks of 4096 bytes
        # Accept waveform of input voice
        if vosk_speech2text_v.AcceptWaveform(data): 
            # Parse the JSON result and get the recognized text
            result = json.loads(vosk_speech2text_v.Result())
            recognized_text = result['text']
            # Check for the termination keyword
            if ("terminate" in recognized_text.lower()) or \
               ("ایست" in recognized_text):
                print("Termination keyword detected. Stopping...")
                break
            print(f'\nBefore Processing: {recognized_text}')
            engli_to_math_v = EngToMathX().sen_to_math_m # For shortness
            recognized_text = engli_to_math_v(recognized_text)
            # Write recognized text to the file
            #output_file.write(recognized_text + "\n")
            audi_to_tex_resul += [recognized_text]
            print(f'\nAfter Processing: {recognized_text}')
                
    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PyAudio object
    p.terminate()

    return "".join(audi_to_tex_resul)

if __name__ == "__main__":
    main()
