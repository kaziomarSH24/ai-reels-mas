import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, useForm, usePage } from '@inertiajs/react';
import EmotionTestForm from '@/Components/AI/EmotionTestForm';
import EmotionTestResult from '@/Components/AI/EmotionTestResult';

export default function Dashboard() {
    const { flash } = usePage().props;
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
                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
