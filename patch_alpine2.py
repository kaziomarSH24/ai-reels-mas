filepath = 'resources/views/filament/pages/ai-studio-native.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

import re

# We need to replace the entire x-data and x-init block
pattern = r'<div x-data="\{.*?\}"\s+x-init=".*?">'

replacement = '''<div x-data="{ 
             progress: 0, 
             status: 'Initializing AI Engine...',
             intervalId: null,
             startProgress() {
                 if (this.intervalId) return;
                 this.progress = 1;
                 this.status = 'Establishing Secure Connection...';
                 this.intervalId = setInterval(() => {
                     if (this.progress < 25) {
                         this.progress += 0.5;
                         this.status = 'Analyzing Audio Spectrogram & Extracting Subtitles...';
                     } else if (this.progress < 50) {
                         this.progress += 0.2;
                         this.status = 'Running NLP Token Classification...';
                     } else if (this.progress < 75) {
                         this.progress += 0.3;
                         this.status = 'Detecting Idioms & Complex Vocabulary...';
                     } else if (this.progress < 95) {
                         this.progress += 0.1;
                         this.status = 'Performing Neural Machine Translation (NMT)...';
                     } else {
                         this.status = 'Finalizing Data Models...';
                     }
                 }, 100);
             },
             stopProgress() {
                 if (this.intervalId) { 
                     clearInterval(this.intervalId); 
                     this.intervalId = null; 
                 }
             },
             init() {
                 let observer = new MutationObserver((mutations) => {
                     if (this.$el.style.display !== 'none') {
                         this.startProgress();
                     } else {
                         this.stopProgress();
                     }
                 });
                 observer.observe(this.$el, { attributes: true, attributeFilter: ['style'] });
                 if (this.$el.style.display !== 'none') this.startProgress();
             }
         }">'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("Alpine block rewritten perfectly!")
