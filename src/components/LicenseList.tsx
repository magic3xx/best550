import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';

interface License {
  id: number;
  key: string;
  active: boolean;
  expiration_date: string;
  subscription_type: string;
  support_name: string;
  activated: boolean;
  key_type: string;
  multi_device: boolean;
}

export default function LicenseList() {
  const [licenses, setLicenses] = useState<License[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLicenses();
  }, []);

  const fetchLicenses = async () => {
    try {
      const response = await axios.get('/api/licenses');
      setLicenses(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch licenses');
      setLoading(false);
    }
  };

  const toggleActive = async (id: number) => {
    try {
      await axios.post(`/api/toggle_active/${id}`);
      fetchLicenses();
    } catch (err) {
      setError('Failed to toggle license status');
    }
  };

  const deleteLicense = async (id: number) => {
    if (!confirm('Are you sure you want to delete this license?')) return;
    try {
      await axios.delete(`/api/delete_license/${id}`);
      fetchLicenses();
    } catch (err) {
      setError('Failed to delete license');
    }
  };

  if (loading) return <div className="text-center">Loading...</div>;
  if (error) return <div className="text-red-600 text-center">{error}</div>;

  return (
    <div className="bg-white shadow rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiration</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {licenses.map((license) => (
            <tr key={license.id}>
              <td className="px-6 py-4 whitespace-nowrap">{license.key}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    license.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}
                >
                  {license.active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {format(new Date(license.expiration_date), 'PPP')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">{license.subscription_type}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  onClick={() => toggleActive(license.id)}
                  className="text-indigo-600 hover:text-indigo-900 mr-4"
                >
                  Toggle Status
                </button>
                <button
                  onClick={() => deleteLicense(license.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}