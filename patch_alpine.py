import re
filepath = 'resources/views/filament/pages/ai-studio-native.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the alpine js block
pattern = r'x-data="\{.*?progress: 0.*?startProgress.*?this\.progress = 0.*?this\.interval = setInterval.*?\}"'
replacement = '''x-data="{ 
             progress: 0, 
             status: 'Initializing AI Engine...',
             interval: null,
             startProgress() {
                 this.progress = 1;
                 this.status = 'Establishing Secure Connection...';
                 this.interval = setInterval(() => {
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
             }
         }"'''
         
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("Alpine Patch applied successfully!")
