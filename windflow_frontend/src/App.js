import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Weather from './components/Weather';

const App = () => {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Weather/>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;