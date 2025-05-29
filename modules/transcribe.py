# code taken and adapted from https://github.com/m-bain/whisperX

import whisperx
import os

class Transcriber:
    def __init__(self, api_key, model="large-v2", device="cuda", compute_type="int8", batch_size=4):
        self.device = device
        self.compute_type = compute_type
        self.batch_size = batch_size
        self.model = whisperx.load_model(model, device, compute_type=compute_type, language="en")
        self.model_a, self.metadata = whisperx.load_align_model(language_code='en', device=device)
        self.diarize_model = whisperx.diarize.DiarizationPipeline(use_auth_token=api_key, device=device)


    def transcribe(self, audio_file):        

        # Transcribe the audio file
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=self.batch_size)
        results = whisperx.align(result["segments"], self.model_a, self.metadata, audio, self.device, return_char_alignments=False)
        diarize_segments = self.diarize_model(audio, min_speakers=1, max_speakers=2)
        diarize_results = whisperx.assign_word_speakers(diarize_segments, results)
        return diarize_results
