import re
filepath = 'resources/views/filament/pages/ai-studio-native.blade.php'
with open(filepath, 'r') as f:
    content = f.read()

# Remove the old fake ring progress bar
pattern1 = r'<!-- Loading Animation.*?</div>\n    </div>'
replacement1 = '''<!-- AI Engine Processing (AlpineJS Simulated Realtime Progress) -->
    <div wire:loading wire:target="analyzeVideo" style="margin-top: 2rem; width: 100%;">
        <div x-data="{ 
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
         }"
         x-init="
             let observer = new MutationObserver((mutations) => {
                 if ($el.style.display !== 'none') {
                     if(!interval) startProgress();
                 } else {
                     if(interval) { clearInterval(interval); interval = null; }
                 }
             });
             observer.observe($el, { attributes: true, attributeFilter: ['style'] });
             if ($el.style.display !== 'none') startProgress();
         ">
        
        <div style="padding: 2rem; background-color: rgba(17, 24, 39, 0.9); border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);">
            
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <h3 style="font-size: 1.125rem; font-weight: 700; color: #ffffff; display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                    <style>
                        @keyframes spin { 100% { transform: rotate(360deg); } }
                        .animate-spin-custom { animation: spin 1s linear infinite; }
                    </style>
                    <svg class="animate-spin-custom" style="width: 1.5rem; height: 1.5rem; color: #10b981;" fill="none" viewBox="0 0 24 24"><circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    AI Pipeline Active
                </h3>
                <span style="color: #34d399; font-family: monospace; font-size: 1.25rem; font-weight: 700;" x-text="Math.floor(progress) + '%'">0%</span>
            </div>

            <!-- Progress Bar -->
            <div style="width: 100%; background-color: #1f2937; border-radius: 9999px; height: 0.75rem; margin-bottom: 0.5rem; overflow: hidden; border: 1px solid #374151;">
                <div style="background: linear-gradient(to right, #10b981, #2dd4bf); height: 0.75rem; border-radius: 9999px; transition: width 0.3s ease-out;" 
                     :style="'width: ' + progress + '%'"></div>
            </div>

            <!-- Dynamic Status Text -->
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.875rem; color: #9ca3af;">
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <style>
                        @keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
                        .animate-pulse-custom { animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
                    </style>
                    <span class="animate-pulse-custom" style="width: 0.5rem; height: 0.5rem; border-radius: 9999px; background-color: #10b981;"></span>
                    <span x-text="status"></span>
                </span>
                <span>Please wait... (Usually takes 1-2 mins)</span>
            </div>
        </div>
        </div>
    </div>'''

content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

# Remove the Live Progress Bar Section if it's there
pattern2 = r'<!-- Live Progress Bar Section -->.*?</div>.*?</div>'
replacement2 = ''
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
print("File restored and patched!")
