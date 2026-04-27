import React from 'react';

type FilterBarProps = {
  selectedUser: string;
  setSelectedUser: (user: string) => void;
  severityFilter: string;
  setSeverityFilter: (severity: string) => void;
  users: string[];
};

export default function FilterBar({
  selectedUser,
  setSelectedUser,
  severityFilter,
  setSeverityFilter,
  users
}: FilterBarProps) {
  return (
    <div className="mb-6 p-4 bg-white rounded-lg shadow">
      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium mb-1">Filter by User</label>
          <select
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Users</option>
            {users.map(user => (
              <option key={user} value={user}>
                {user}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium mb-1">Filter by Severity</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        {(selectedUser || severityFilter) && (
          <div className="flex items-end">
            <button
              onClick={() => {
                setSelectedUser('');
                setSeverityFilter('');
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-md text-sm hover:bg-gray-600"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
