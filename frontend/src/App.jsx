import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ChatPage from './components/ChatPage';
import OfflineEvalsPage from './components/OfflineEvalsPage';
import ConversationMetricsPage from './components/ConversationMetricsPage';

import './App.css';

function App() {
  return (
    <div className="app-container">
      <Header /> 
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/offline-evals" element={<OfflineEvalsPage />} />
          <Route path="/conversation-metrics" element={<ConversationMetricsPage />} />
        </Routes>
      </main>
    </div>
  );
}
export default App;