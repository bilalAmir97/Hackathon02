import { useState, useEffect, useCallback } from 'react';

interface SearchResult<T> {
  item: T;
  matches: string[];
}

export const useSearch = <T extends Record<string, any>>(items: T[], searchFields: (keyof T)[]) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<T[]>(items);
  const [isSearching, setIsSearching] = useState(false);

  const search = useCallback((searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults(items);
      return;
    }

    setIsSearching(true);
    const searchTerm = searchQuery.toLowerCase().trim();

    const filteredItems = items.filter(item => {
      return searchFields.some(field => {
        const fieldValue = item[field];
        if (fieldValue === null || fieldValue === undefined) return false;

        return String(fieldValue).toLowerCase().includes(searchTerm);
      });
    });

    // Simulate search delay for better UX
    setTimeout(() => {
      setResults(filteredItems);
      setIsSearching(false);
    }, 150);
  }, [items, searchFields]);

  useEffect(() => {
    search(query);
  }, [query, search]);

  const handleQueryChange = (newQuery: string) => {
    setQuery(newQuery);
  };

  return {
    query,
    results,
    isSearching,
    handleQueryChange,
    setSearchQuery: setQuery
  };
};