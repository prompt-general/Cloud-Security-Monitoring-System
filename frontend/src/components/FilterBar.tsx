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
    <div className="mb-6 flex gap-4 flex-wrap">
      <select
        value={selectedUser}
        onChange={(e) => setSelectedUser(e.target.value)}
        className="px-3 py-2 border rounded"
      >
        <option value="">All users</option>
        {users.map(user => <option key={user} value={user}>{user}</option>)}
      </select>
      <select
        value={severityFilter}
        onChange={(e) => setSeverityFilter(e.target.value)}
        className="px-3 py-2 border rounded"
      >
        <option value="">All severities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
      </select>
    </div>
  );
}
