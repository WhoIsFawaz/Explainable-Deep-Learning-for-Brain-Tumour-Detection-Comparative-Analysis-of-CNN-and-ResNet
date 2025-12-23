import { useState, useEffect } from 'react';
import { getDoctors, getPredictionHistory, getImageUrl } from '../../api';

function PatientHistory() {
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDoctors();
  }, []);

  const loadDoctors = async () => {
    try {
      const data = await getDoctors();
      setDoctors(data.doctors);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadHistory = async (doctorId) => {
    setLoading(true);
    setError('');
    try {
      const data = await getPredictionHistory({ doctor_id: doctorId });
      setHistory(data.predictions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDoctorChange = (e) => {
    const doctorId = e.target.value;
    setSelectedDoctor(doctorId);
    if (doctorId) {
      loadHistory(doctorId);
    } else {
      setHistory([]);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">My MRI Scan History</h2>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Doctor Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter by Doctor
        </label>
        <select
          value={selectedDoctor}
          onChange={handleDoctorChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
        >
          <option value="">-- All Doctors --</option>
          {doctors.map((doctor) => (
            <option key={doctor.id} value={doctor.id}>
              {doctor.name} ({doctor.email})
            </option>
          ))}
        </select>
      </div>

      {/* History Display */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading history...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No scan history found
        </div>
      ) : (
        <div className="space-y-6">
          {history.map((record) => {
            const isTumor = record.predicted_label === 'tumor';
            const confidence = (record.confidence * 100).toFixed(5);
            
            return (
              <div key={record.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Scan #{record.id}</h3>
                    <p className="text-sm text-gray-600">
                      Doctor: {record.doctor_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      Date: {new Date(record.uploaded_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                    isTumor ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {isTumor ? 'Tumor Detected' : 'No Tumor'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="text-lg font-bold text-gray-900">{confidence}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Probabilities</p>
                    <p className="text-sm text-gray-900">
                      Tumor: {(record.prob_tumor * 100).toFixed(5)}% | 
                      No Tumor: {(record.prob_no_tumor * 100).toFixed(5)}%
                    </p>
                  </div>
                </div>

                {/* Images */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">Original</p>
                    <img
                      src={getImageUrl(record.original_image_uri)}
                      alt="Original"
                      className="w-full h-auto rounded border border-gray-300"
                    />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">Heatmap</p>
                    <img
                      src={getImageUrl(record.gradcam_image_uri.replace('_overlay', '_heatmap'))}
                      alt="Heatmap"
                      className="w-full h-auto rounded border border-gray-300"
                    />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">Overlay</p>
                    <img
                      src={getImageUrl(record.gradcam_image_uri)}
                      alt="Overlay"
                      className="w-full h-auto rounded border border-gray-300"
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default PatientHistory;
