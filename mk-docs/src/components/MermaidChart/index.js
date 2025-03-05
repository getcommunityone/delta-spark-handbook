// src/components/MermaidChart.js
import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false, // Important to call mermaid.init manually
  theme: 'default',   // Customize according to your needs
});

const MermaidChart = ({ chart }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartRef.current) {
      mermaid.init(undefined, chartRef.current);
    }
  }, [chart]);

  return (
    <div className="mermaid" ref={chartRef}>
      {chart}
    </div>
  );
};

export default MermaidChart;
