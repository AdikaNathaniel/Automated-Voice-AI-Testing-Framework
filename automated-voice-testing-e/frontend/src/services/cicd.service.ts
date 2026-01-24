/**
 * CI/CD service helpers.
 */

import apiClient from './api';
import type {
  CICDRunListParams,
  CICDRunListResponse,
} from '../types/cicd';

export const getCICDRuns = async (
  params: CICDRunListParams = {}
): Promise<CICDRunListResponse> => {
  const response = await apiClient.get('/cicd/runs', {
    params: {
      status: params.status ?? null,
    },
  });

  // Backend returns SuccessResponse with data field, unwrap it
  return response.data.data as CICDRunListResponse;
};

export default {
  getCICDRuns,
};
