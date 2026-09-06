import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, useForm, usePage } from '@inertiajs/react';
import EmotionTestForm from '@/Components/AI/EmotionTestForm';
import EmotionTestResult from '@/Components/AI/EmotionTestResult';

export default function Dashboard() {
    const { flash, history } = usePage().props;
    const { data, setData, post, processing } = useForm({
        sentence: flash.sentence || '',
    });

    const submit = (e) => {
        e.preventDefault();
        post(route('detect.emotion'));
    };

    return (
        <AuthenticatedLayout
            header={<h2 className="text-xl font-semibold leading-tight text-gray-800">AI Reels Dashboard</h2>}
        >
            <Head title="Dashboard" />

            <div className="py-12">
                <div className="mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="overflow-hidden bg-white shadow-sm sm:rounded-lg">
                        <div className="p-6 text-gray-900">
                            <div className="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-lg mx-auto border border-gray-700">
                                
                                <div className="flex items-center mb-6">
                                    <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-2xl mr-4">🤖</div>
                                    <div>
                                        <h1 className="text-2xl font-bold text-blue-400">Hunter Agent Core</h1>
                                        <p className="text-gray-400 text-sm">Powered by React + Inertia + Python</p>
                                    </div>
                                </div>

                                <EmotionTestForm 
                                    data={data} 
                                    setData={setData} 
                                    submit={submit} 
                                    processing={processing} 
                                />

                                <EmotionTestResult result={flash.result} />

                            </div>

                            {/* History Section */}
                            {history && history.length > 0 && (
                                <div className="mt-12 bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-5xl mx-auto border border-gray-700">
                                    <h2 className="text-xl font-bold text-white mb-6 flex items-center">
                                        <span className="mr-2">📜</span> Previous Analyses
                                    </h2>
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm text-left text-gray-300">
                                            <thead className="text-xs text-gray-400 uppercase bg-gray-900">
                                                <tr>
                                                    <th className="px-4 py-3 rounded-tl-lg">Dialogue</th>
                                                    <th className="px-4 py-3">Emotion</th>
                                                    <th className="px-4 py-3">CEFR</th>
                                                    <th className="px-4 py-3">Translation</th>
                                                    <th className="px-4 py-3 rounded-tr-lg">Time</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {history.map((item) => (
                                                    <tr key={item.id} className="border-b border-gray-700 hover:bg-gray-750">
                                                        <td className="px-4 py-4 max-w-xs truncate" title={item.sentence}>{item.sentence}</td>
                                                        <td className="px-4 py-4">
                                                            <span className={`px-2 py-1 rounded text-xs font-bold ${item.emotion === 'JOY' || item.emotion === 'LOVE' ? 'bg-green-900 text-green-300' : item.emotion === 'ANGER' ? 'bg-red-900 text-red-300' : 'bg-blue-900 text-blue-300'}`}>
                                                                {item.emotion}
                                                            </span>
                                                        </td>
                                                        <td className="px-4 py-4 font-bold text-yellow-400">{item.cefr_level}</td>
                                                        <td className="px-4 py-4 max-w-xs truncate" title={item.translation}>{item.translation}</td>
                                                        <td className="px-4 py-4 text-xs text-gray-500">{new Date(item.created_at).toLocaleString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
