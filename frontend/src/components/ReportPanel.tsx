import React, { useEffect, useState } from 'react';
import './ReportPanel.css';

interface ReportPanelProps {
  refreshTrigger?: number;
  userId?: string;
}

export const ReportPanel: React.FC<ReportPanelProps> = ({ refreshTrigger, userId }) => {
  const [iframeUrl, setIframeUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [key, setKey] = useState(0); // Use key to force re-render of iframe

  const loadReport = () => {
    setLoading(true);
    const timestamp = new Date().getTime();
    // Use the same baseUrl logic as agent.ts
    // @ts-ignore - Vite env variables
    const baseUrl = import.meta.env.DEV ? `http://${window.location.hostname}:8000` : '';
    let url = `${baseUrl}/temp/html_report.html?t=${timestamp}`;
    if (userId) {
      url += `&user_id=${encodeURIComponent(userId)}`;
    }
    setIframeUrl(url);
    setKey(prev => prev + 1);
  };

  useEffect(() => {
    loadReport();
  }, [refreshTrigger]);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  return (
    <div className="report-panel">
      <div className="report-header">
        <h2>📊 HTML Report</h2>
        <button onClick={loadReport} className="refresh-button" disabled={loading}>
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      <div className="report-content" style={{ padding: 0, position: 'relative', overflow: 'hidden' }}>
        {loading && (
          <div className="report-loading" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: '#f8f9fa', zIndex: 10 }}>
            <div className="loading-spinner"></div>
            <p>Loading HTML report...</p>
          </div>
        )}
        
        <iframe
          key={key}
          src={iframeUrl}
          className="report-iframe"
          onLoad={handleIframeLoad}
          title="Report Analysis"
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            display: 'block'
          }}
        />
      </div>
    </div>
  );
};
