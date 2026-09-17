<x-filament-panels::page>
    <div class="w-full">
        {{ $this->analyzerForm }}
    </div>

    <!-- Dynamic YouTube Preview -->
    <div x-data="{ 
            url: @entangle('analyzerData.youtubeUrl').live,
            videoId() {
                if (!this.url) return null;
                const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
                const match = this.url.match(regExp);
                return (match && match[2].length === 11) ? match[2] : null;
            }
        }"
        x-show="videoId()"
        style="display: none; margin-top: 1rem; padding: 1.5rem; background-color: rgba(17, 24, 39, 0.9); border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.4); align-items: flex-start; gap: 1.5rem;"
        :style="videoId() ? 'display: flex;' : 'display: none;'">
        
        <div style="position: relative; width: 240px; border-radius: 0.5rem; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); flex-shrink: 0;">
            <img :src="'https://img.youtube.com/vi/' + videoId() + '/hqdefault.jpg'" style="width: 100%; height: auto; object-fit: cover; aspect-ratio: 16/9;">
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background-color: rgba(0,0,0,0.2);">
                <svg style="width: 3rem; height: 3rem; color: white; opacity: 0.8;" fill="currentColor" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
            </div>
        </div>
        
        <div>
            <h3 style="font-size: 1.125rem; font-weight: 700; color: #10b981; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <svg style="width: 1.25rem; height: 1.25rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Video Ready for Analysis
            </h3>
            <p style="color: #9ca3af; font-size: 0.875rem; line-height: 1.5; max-width: 32rem;">
                Our AI Engine will download the subtitles, clean the text, and run the NLP Classification pipelines to extract targeted vocabulary.
            </p>
        </div>
    </div>

    <!-- AI Engine Processing (AlpineJS Simulated Realtime Progress) -->
    <div wire:loading wire:target="analyzeVideo" style="margin-top: 2rem; width: 100%;">
        <div x-data="{ 
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
         }">
        
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
    </div>

    @if($currentMovieId)
        <!-- Live Filament Table -->
        <div class="mt-8">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Extracted Dialogues</h3>
            {{ $this->table }}
        </div>
    @endif
    <x-filament-actions::modals />
</x-filament-panels::page>
