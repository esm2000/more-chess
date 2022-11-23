import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

import Background from './components/Background';


class App extends React.Component {
    render() {
        return (
            <div>
                <Background />
            </div>
        );
    }
  }
  
  // ========================================
  
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(<App />);
  
  