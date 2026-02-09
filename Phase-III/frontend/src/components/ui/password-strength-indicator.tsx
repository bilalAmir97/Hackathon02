'use client';

import React from 'react';

interface PasswordStrengthIndicatorProps {
  password: string;
  className?: string;
}

export const PasswordStrengthIndicator: React.FC<PasswordStrengthIndicatorProps> = ({
  password,
  className = ''
}) => {
  const calculateStrength = (password: string): { score: number; label: string; color: string } => {
    let score = 0;

    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;

    // Character variety checks
    if (/[a-z]/.test(password)) score++; // lowercase
    if (/[A-Z]/.test(password)) score++; // uppercase
    if (/[0-9]/.test(password)) score++; // numbers
    if (/[^A-Za-z0-9]/.test(password)) score++; // special chars

    // Determine strength level
    if (score <= 2) return { score, label: 'Weak', color: 'bg-red-500' };
    if (score <= 4) return { score, label: 'Medium', color: 'bg-yellow-500' };
    return { score, label: 'Strong', color: 'bg-green-500' };
  };

  const { score, label, color } = calculateStrength(password);

  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Password Strength</span>
        <span className={`text-xs font-semibold ${
          score <= 2 ? 'text-red-500' :
          score <= 4 ? 'text-yellow-500' : 'text-green-500'
        }`}>
          {label}
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all duration-300 ease-out ${color}`}
          style={{ width: `${(score / 6) * 100}%` }}
        ></div>
      </div>
      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {score === 0 && 'Enter at least 8 characters with uppercase, lowercase, numbers, and symbols'}
        {score > 0 && score <= 2 && 'Add more character variety for stronger password'}
        {score > 2 && score <= 4 && 'Good password, consider adding more length'}
        {score > 4 && 'Excellent password strength!'}
      </div>
    </div>
  );
};

export default PasswordStrengthIndicator;