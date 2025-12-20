import { getImageUrl } from '../api';

function ResultsView({ result }) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 text-center">
        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-gray-600">No results yet. Upload an MRI scan to get started.</p>
      </div>
    );
  }

  const isTumor = result.predicted_label === 'tumor';
  const confidence = (result.confidence * 100).toFixed(2);

  return (
    <div className="space-y-6">
      {/* Prediction Result Card */}
      <div className={`rounded-xl shadow-lg p-8 ${isTumor ? 'bg-red-50 border-2 border-red-200' : 'bg-green-50 border-2 border-green-200'}`}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Prediction: {isTumor ? 'Tumor Detected' : 'No Tumor Detected'}
            </h2>
            <p className="text-gray-700">
              Confidence: <span className="font-bold">{confidence}%</span>
            </p>
          </div>
          <div className={`w-20 h-20 rounded-full flex items-center justify-center ${isTumor ? 'bg-red-500' : 'bg-green-500'}`}>
            {isTumor ? (
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            ) : (
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>
        </div>

        {/* Probability Breakdown */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 mb-1">Tumor Probability</p>
            <p className="text-2xl font-bold text-red-600">
              {(result.probabilities.tumor * 100).toFixed(2)}%
            </p>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${result.probabilities.tumor * 100}%` }}
              ></div>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 mb-1">No Tumor Probability</p>
            <p className="text-2xl font-bold text-green-600">
              {(result.probabilities.no_tumor * 100).toFixed(2)}%
            </p>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${result.probabilities.no_tumor * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Grad-CAM Visualization */}
      <div className="bg-white rounded-xl shadow-md p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Explainability: Grad-CAM Heatmap</h3>
        <p className="text-gray-600 mb-6">
          The heatmap below highlights regions that influenced the model's prediction. 
          Red/yellow areas indicate higher importance.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Original Image */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">Original MRI</p>
            <img
              src={getImageUrl(result.gradcam_urls.original)}
              alt="Original MRI"
              className="w-full h-auto rounded-lg border-2 border-gray-300"
            />
          </div>

          {/* Heatmap */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">Grad-CAM Heatmap</p>
            <img
              src={getImageUrl(result.gradcam_urls.heatmap)}
              alt="Grad-CAM Heatmap"
              className="w-full h-auto rounded-lg border-2 border-gray-300"
            />
          </div>

          {/* Overlay */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">Overlay</p>
            <img
              src={getImageUrl(result.gradcam_urls.overlay)}
              alt="Grad-CAM Overlay"
              className="w-full h-auto rounded-lg border-2 border-gray-300"
            />
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> Heatmap indicates regions influencing model prediction; not a substitute for radiologist diagnosis. 
            This visualization is for decision support and educational purposes only.
          </p>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3">Prediction Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Prediction ID</p>
            <p className="font-semibold text-gray-900">#{result.id}</p>
          </div>
          <div>
            <p className="text-gray-600">Timestamp</p>
            <p className="font-semibold text-gray-900">
              {new Date(result.uploaded_at).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsView;
