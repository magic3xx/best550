import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import LicenseList from './components/LicenseList';
import AddLicense from './components/AddLicense';
import Navbar from './components/Navbar';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<LicenseList />} />
          <Route path="/add" element={<AddLicense />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;