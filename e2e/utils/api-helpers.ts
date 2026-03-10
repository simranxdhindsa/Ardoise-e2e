/** Factory for consistent mock API responses matching the backend format */
export const ApiResponse = {
  success: <T>(data: T) => ({ status: 'success', data }),

  paginated: <T>(items: T[], total: number, page = 1, pageSize = 10) => ({
    status: 'success',
    data: { results: items, total, page, page_size: pageSize },
  }),

  error: (message: string, code = 'ERROR') => ({
    status: 'error',
    error: { message, code },
  }),
};
