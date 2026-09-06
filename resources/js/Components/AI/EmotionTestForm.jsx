import React from 'react';

export default function EmotionTestForm({ data, setData, submit, processing }) {
    return (
        <form onSubmit={submit} className="space-y-4">
            <div>
                <label htmlFor="sentence" className="block text-sm font-medium text-gray-300 mb-1">
                    Enter a movie dialogue:
                </label>
                <textarea
                    id="sentence"
                    value={data.sentence}
                    onChange={(e) => setData('sentence', e.target.value)}
                    rows="3"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
                    placeholder="e.g. I am completely fed up with your nonsense!"
                    required
                ></textarea>
            </div>

            <button 
                type="submit" 
                disabled={processing}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200 flex justify-center items-center disabled:opacity-50"
            >
                {processing ? 'Analyzing...' : 'Analyze Emotion ⚡'}
            </button>
        </form>
    );
}
