import { useState } from 'react';

function BirthChart() {
  const [birthDetails, setBirthDetails] = useState({
    date: '',
    time: '',
    location: ''
  });
  const [chart, setChart] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setBirthDetails({ ...birthDetails, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setChart(null);

    const response = await fetch('/api/spiritual/birth-chart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ birth_details: birthDetails })
    });
    const data = await response.json();
    if (data.success) {
      setChart(data.birth_chart);
    } else {
      setError(data.message || 'Something went wrong');
    }
  };

  // Card style
  const cardStyle = {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '1rem',
    margin: '0.5rem',
    background: '#fafaff',
    boxShadow: '0 2px 8px #eee',
    minWidth: '180px',
    display: 'inline-block',
    verticalAlign: 'top'
  };

  return (
    <div>
      <h2>ஜாதக விவரங்கள் (Birth Chart)</h2>
      <form onSubmit={handleSubmit} style={{marginBottom: '1rem'}}>
        <input name="date" type="date" onChange={handleChange} required />{' '}
        <input name="time" type="time" onChange={handleChange} required />{' '}
        <input name="location" type="text" placeholder="jaffna,srilanka" onChange={handleChange} required />{' '}
        <button type="submit">பார்க்கவும்</button>
      </form>
      {error && <div style={{color:'red'}}>{error}</div>}
      {chart && (
        <div>
          <h3>Planets</h3>
          <div style={{display:'flex', flexWrap:'wrap'}}>
            {chart.planets && Object.entries(chart.planets).map(([planet, details]) => (
              <div key={planet} style={cardStyle}>
                <strong>{planet}</strong>
                <div>Rashi: {details.rashi}</div>
                <div>Degree: {details.degree}</div>
                <div>House: {details.house}</div>
              </div>
            ))}
          </div>
          <h3>Rashis</h3>
          <div style={{display:'flex', flexWrap:'wrap'}}>
            {chart.rashis && Object.entries(chart.rashis).map(([rashi, details]) => (
              <div key={rashi} style={cardStyle}>
                <strong>{rashi}</strong>
                <div>Lord: {details.lord}</div>
                <div>Start Degree: {details.start_degree}</div>
                <div>End Degree: {details.end_degree}</div>
              </div>
            ))}
          </div>
          <h3>Houses</h3>
          <div style={{display:'flex', flexWrap:'wrap'}}>
            {chart.houses && Object.entries(chart.houses).map(([house, details]) => (
              <div key={house} style={cardStyle}>
                <strong>House {house}</strong>
                <div>Sign: {details.sign}</div>
                <div>Degree: {details.degree}</div>
                <div>Lord: {details.lord}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BirthChart; 