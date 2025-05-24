# code taken and adapted from https://github.com/m-bain/whisperX

import whisperx
import time

class Transcriber:
    def __init__(self, model="large-v2", device="cuda", compute_type="int8", batch_size=4):
        self.device = device
        self.compute_type = compute_type
        self.batch_size = batch_size
        self.model = whisperx.load_model(model, device, compute_type=compute_type, language="en")
        self.model_a, self.metadata = whisperx.load_align_model(language_code='en', device=device)


    def transcribe(self, audio_file):        

        # Transcribe the audio file
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=self.batch_size)
        results = whisperx.align(result["segments"], self.model_a, self.metadata, audio, self.device, return_char_alignments=False)
        return results
