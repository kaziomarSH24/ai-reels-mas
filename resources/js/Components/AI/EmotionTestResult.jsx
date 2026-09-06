import React from 'react';

export default function EmotionTestResult({ result }) {
    if (!result) return null;

    const getEmotionEmoji = (emotion) => {
        const map = {
            'ANGER': '😡',
            'JOY': '😄',
            'SADNESS': '😢',
            'FEAR': '😨',
            'SURPRISE': '😲',
            'LOVE': '😍'
        };
        return map[emotion] || '🤔';
    };

    return (
        <div className="mt-8 p-5 bg-gray-900 rounded-lg border border-gray-700">
            <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-3">AI Analysis Result</h3>
            
            {result.error ? (
                <div className="text-red-400 flex items-center">
                    <span className="text-xl mr-2">❌</span>
                    {result.error}
                </div>
            ) : (
                <>
                    <div className="flex justify-between items-center mb-4">
                        <span className="text-gray-300">Detected Emotion:</span>
                        <span className={`text-2xl font-bold flex items-center gap-2 ${result.emotion === 'JOY' || result.emotion === 'LOVE' ? 'text-green-400' : result.emotion === 'ANGER' ? 'text-red-400' : 'text-blue-400'}`}>
                            {result.emotion} {getEmotionEmoji(result.emotion)}
                        </span>
                    </div>
                    
                    <div className="mb-4">
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Confidence</span>
                            <span className="text-blue-400 font-mono">{result.confidence}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${result.confidence}%` }}></div>
                        </div>
                    </div>

                    <div className="flex justify-between items-center mb-4 p-3 bg-gray-800 rounded border border-gray-700">
                        <span className="text-gray-300">CEFR Difficulty Level:</span>
                        <span className="text-xl font-bold text-yellow-400">{result.cefr_level || 'N/A'}</span>
                    </div>

                    <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                        <div className="text-xs text-blue-400 uppercase tracking-wider mb-1">Bangla Translation</div>
                        <p className="text-lg text-white font-medium">{result.translation || 'Translation failed'}</p>
                    </div>
                </>
            )}
        </div>
    );
}
