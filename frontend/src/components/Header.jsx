import React from 'react';
import { NavLink } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="app-header">
      <div className="header-branding">
        <h1>Scanntech Chatbot</h1>
        <h2>Chatea con: 'An Introduction to Statistical Learning"</h2>
      </div>

      <nav className="header-nav">
        <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Chat
        </NavLink>
        <NavLink to="/offline-evals" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Monitoreo Offline
        </NavLink>
        <NavLink to="/conversation-metrics" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          Métricas Online
        </NavLink>
      </nav>
    </header>
  );
};

export default Header;