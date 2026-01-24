import api from './api';

export interface Category {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active: boolean;
  is_system: boolean;
  tenant_id?: string;
  created_at: string;
  updated_at: string;
  scenario_count: number;
}

export interface CategoryListResponse {
  categories: Category[];
  total: number;
}

export interface CategoryCreate {
  name: string;
  display_name?: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  display_name?: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active?: boolean;
}

const categoryService = {
  /**
   * Get all categories
   */
  async getCategories(params?: {
    is_active?: boolean;
    include_system?: boolean;
  }): Promise<CategoryListResponse> {
    const response = await api.get<CategoryListResponse>('/categories', { params });
    return response.data;
  },

  /**
   * Get a single category by ID
   */
  async getCategory(id: string): Promise<Category> {
    const response = await api.get<Category>(`/categories/${id}`);
    return response.data;
  },

  /**
   * Create a new category (admin only)
   */
  async createCategory(data: CategoryCreate): Promise<Category> {
    const response = await api.post<Category>('/categories', data);
    return response.data;
  },

  /**
   * Update an existing category (admin only)
   */
  async updateCategory(id: string, data: CategoryUpdate): Promise<Category> {
    const response = await api.patch<Category>(`/categories/${id}`, data);
    return response.data;
  },

  /**
   * Delete a category (admin only)
   */
  async deleteCategory(id: string, force?: boolean): Promise<void> {
    await api.delete(`/categories/${id}`, {
      params: { force: force || false },
    });
  },
};

export default categoryService;
