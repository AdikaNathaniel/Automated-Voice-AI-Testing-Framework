import { beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import JiraIntegrationPage from '../Integrations/Jira';
import { renderWithProviders, screen, waitFor, userEvent } from '../../test/utils';

// Use the global axios mock from setup.ts
const mockedAxios = vi.mocked(axios);

describe('JiraIntegrationPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it(
    'loads configuration, allows editing mappings, and saves updates',
    async () => {
      mockedAxios.get.mockResolvedValue({
      data: {
        baseUrl: 'https://example.atlassian.net/rest/api/3',
        browseUrl: 'https://example.atlassian.net',
        userEmail: 'qa@example.com',
        apiTokenSet: true,
        projectMapping: {
          voice: {
            projectKey: 'QA',
            issueType: 'Bug',
            browseUrl: 'https://example.atlassian.net/browse',
          },
        },
      },
    });

    mockedAxios.put.mockResolvedValue({
      data: {
        baseUrl: 'https://new-instance.atlassian.net/rest/api/3',
        browseUrl: 'https://new-instance.atlassian.net',
        userEmail: 'qa@example.com',
        apiTokenSet: true,
        projectMapping: {
          voice: {
            projectKey: 'QA',
            issueType: 'Task',
            browseUrl: 'https://example.atlassian.net/browse',
          },
          mobile: {
            projectKey: 'MB',
            issueType: 'Bug',
          },
        },
      },
    });

    renderWithProviders(<JiraIntegrationPage />);

    await waitFor(() => expect(mockedAxios.get).toHaveBeenCalledTimes(1));

    expect(screen.getByRole('heading', { name: /Jira Integration/i })).toBeInTheDocument();

    const baseUrlInput = await screen.findByLabelText(/Jira REST API URL/i);
    expect(baseUrlInput).toHaveValue('https://example.atlassian.net/rest/api/3');
    await userEvent.clear(baseUrlInput);
    await userEvent.type(baseUrlInput, 'https://new-instance.atlassian.net/rest/api/3');

    const browseUrlInput = screen.getByLabelText(/Jira browse URL/i);
    await userEvent.clear(browseUrlInput);
    await userEvent.type(browseUrlInput, 'https://new-instance.atlassian.net');

    const tokenInput = screen.getByLabelText(/API token/i);
    await userEvent.type(tokenInput, 'new-token');

    const issueTypeInputs = screen.getAllByLabelText(/Issue type/i);
    await userEvent.clear(issueTypeInputs[0]);
    await userEvent.type(issueTypeInputs[0], 'Task');

    const addMappingButton = screen.getByRole('button', { name: /Add project mapping/i });
    await userEvent.click(addMappingButton);

    const mappingIdInputs = screen.getAllByLabelText(/Mapping ID/i);
    await userEvent.type(mappingIdInputs[1], 'mobile');

    const projectKeyInputs = screen.getAllByLabelText(/Project key/i);
    await userEvent.type(projectKeyInputs[1], 'MB');

    const newIssueTypeInputs = screen.getAllByLabelText(/Issue type/i);
    await userEvent.type(newIssueTypeInputs[1], 'Bug');

    const saveButton = screen.getByRole('button', { name: /Save configuration/i });
    await userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockedAxios.put).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/jira/config',
        {
          baseUrl: 'https://new-instance.atlassian.net/rest/api/3',
          browseUrl: 'https://new-instance.atlassian.net',
          userEmail: 'qa@example.com',
          apiToken: 'new-token',
          projectMapping: {
            voice: {
              projectKey: 'QA',
              issueType: 'Task',
              browseUrl: 'https://example.atlassian.net/browse',
            },
            mobile: {
              projectKey: 'MB',
              issueType: 'Bug',
            },
          },
        },
        expect.any(Object)
      );
    });

      const successAlert = await screen.findByText(/Configuration saved successfully/i);
      expect(successAlert).toBeInTheDocument();
    },
    30000
  );

  it('displays error state when configuration fetch fails and allows dismissing it', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Integration unavailable' } },
    });

    renderWithProviders(<JiraIntegrationPage />);

    const errorAlert = await screen.findByRole('alert');
    expect(errorAlert).toHaveTextContent('Integration unavailable');

    const dismissButton = screen.getByRole('button', { name: /Dismiss/i });
    await userEvent.click(dismissButton);

    await waitFor(() => {
      expect(screen.queryByRole('alert')).toBeNull();
    });
  });
});
