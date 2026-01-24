import { beforeEach, describe, expect, it, vi } from 'vitest';
import ReportBuilder from '../Reports/ReportBuilder';
import { renderWithProviders, screen, waitFor, within, userEvent } from '../../test/utils';
import { fireEvent } from '@testing-library/react';

const mockFetchSections = vi.fn();
const mockCreateReport = vi.fn();

vi.mock('../../services/reportBuilder.service', () => ({
  fetchReportSections: (...args: unknown[]) => mockFetchSections(...args),
  createCustomReport: (...args: unknown[]) => mockCreateReport(...args),
}));

const createSection = (overrides: Partial<Record<string, unknown>> = {}) => ({
  id: 'analytics-overview',
  title: 'Analytics Overview',
  description: 'Key pass/fail metrics and KPI trends.',
  metrics: ['pass_rate', 'defect_density'],
  ...overrides,
});

const createDataTransfer = (payload: string) => {
  const data: Record<string, string> = { 'text/plain': payload };
  return {
    setData: (type: string, value: string) => {
      data[type] = value;
    },
    getData: (type: string) => data[type],
    dropEffect: 'move',
    effectAllowed: 'all',
    types: ['text/plain'],
    clearData: () => {
      Object.keys(data).forEach((key) => delete data[key]);
    },
  };
};

describe('ReportBuilder page', () => {
  beforeEach(() => {
    mockFetchSections.mockReset();
    mockCreateReport.mockReset();
  });

  it('renders available sections, layout drop zone, and preview placeholder', async () => {
    const sampleSections = [
      createSection(),
      createSection({
        id: 'defect-summary',
        title: 'Defect Summary',
        description: 'Resolved vs open defects with severity breakdown.',
        metrics: ['defects_resolved', 'defects_open'],
      }),
    ];

    mockFetchSections.mockResolvedValue(sampleSections);

    renderWithProviders(<ReportBuilder />);

    expect(screen.getByText(/loading report sections/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(mockFetchSections).toHaveBeenCalledTimes(1);
    });

    const availableHeading = await screen.findByRole('heading', { name: /available sections/i });
    expect(availableHeading).toBeInTheDocument();

    const availableList = screen.getByRole('list', { name: /available sections/i });
    const availableItems = within(availableList).getAllByRole('listitem');
    expect(availableItems).toHaveLength(sampleSections.length);

    for (const section of sampleSections) {
      expect(within(availableList).getByText(section.title)).toBeInTheDocument();
      expect(within(availableList).getByText(section.description)).toBeInTheDocument();
    }

    const layoutRegion = screen.getByRole('region', { name: /report layout/i });
    expect(layoutRegion).toBeInTheDocument();
    expect(within(layoutRegion).getByText(/drag sections here/i)).toBeInTheDocument();

    const previewRegion = screen.getByRole('region', { name: /report preview/i });
    expect(previewRegion).toBeInTheDocument();
    expect(within(previewRegion).getByText(/add sections to see a preview of your report contents/i)).toBeInTheDocument();
  });

  it('supports dragging sections into the report layout', async () => {
    const sampleSections = [
      createSection(),
      createSection({
        id: 'defect-summary',
        title: 'Defect Summary',
      }),
    ];
    mockFetchSections.mockResolvedValue(sampleSections);

    renderWithProviders(<ReportBuilder />);
    await waitFor(() => expect(mockFetchSections).toHaveBeenCalled());

    const availableList = screen.getByRole('list', { name: /available sections/i });
    const layoutRegion = screen.getByRole('region', { name: /report layout/i });

    const analyticsItem = within(availableList).getByText('Analytics Overview').closest('li');
    if (!analyticsItem) {
      throw new Error('Analytics section list item not found');
    }

    const dataTransfer = createDataTransfer('available:analytics-overview');

    // Simulate dragging the analytics section into the layout container.
    fireEvent.dragStart(analyticsItem, { dataTransfer });
    fireEvent.dragOver(layoutRegion, { dataTransfer });
    fireEvent.drop(layoutRegion, { dataTransfer });

    const layoutList = screen.getByRole('list', { name: /report layout sections/i });

    expect(within(layoutList).getByText('Analytics Overview')).toBeInTheDocument();
    expect(within(availableList).queryByText('Analytics Overview')).not.toBeInTheDocument();
    expect(within(layoutRegion).queryByText(/drag sections here/i)).not.toBeInTheDocument();
  });

  it('allows reordering layout sections via drag-and-drop', async () => {
    const sampleSections = [
      createSection(),
      createSection({
        id: 'defect-summary',
        title: 'Defect Summary',
      }),
      createSection({
        id: 'performance-insights',
        title: 'Performance Insights',
      }),
    ];
    mockFetchSections.mockResolvedValue(sampleSections);

    renderWithProviders(<ReportBuilder />);
    await waitFor(() => expect(mockFetchSections).toHaveBeenCalled());

    const availableList = screen.getByRole('list', { name: /available sections/i });
    const layoutRegion = screen.getByRole('region', { name: /report layout/i });

    const dragIn = async (title: string, id: string) => {
      const item = within(availableList).getByText(title).closest('li');
      if (!item) {
        throw new Error(`List item for ${title} not found`);
      }
      const payload = createDataTransfer(`available:${id}`);
      fireEvent.dragStart(item, { dataTransfer: payload });
      fireEvent.dragOver(layoutRegion, { dataTransfer: payload });
      fireEvent.drop(layoutRegion, { dataTransfer: payload });
    };

    await dragIn('Analytics Overview', 'analytics-overview');
    await dragIn('Defect Summary', 'defect-summary');

    const layoutList = screen.getByRole('list', { name: /report layout sections/i });
    let layoutItems = within(layoutList).getAllByRole('listitem');
    expect(layoutItems.map((item) => within(item).getByRole('heading').textContent)).toEqual([
      'Analytics Overview',
      'Defect Summary',
    ]);

    const secondItem = layoutItems[1];
    const reorderTransfer = createDataTransfer('layout:defect-summary');
    fireEvent.dragStart(secondItem, { dataTransfer: reorderTransfer });
    const firstItem = layoutItems[0];
    fireEvent.dragOver(firstItem, { dataTransfer: reorderTransfer });
    fireEvent.drop(firstItem, { dataTransfer: reorderTransfer });

    layoutItems = within(layoutList).getAllByRole('listitem');
    expect(layoutItems.map((item) => within(item).getByRole('heading').textContent)).toEqual([
      'Defect Summary',
      'Analytics Overview',
    ]);
  });

  it('generates a preview summary and exports the report', async () => {
    const sampleSections = [
      createSection({
        metrics: ['pass_rate', 'defect_density'],
      }),
      createSection({
        id: 'defect-summary',
        title: 'Defect Summary',
        metrics: ['defects_resolved', 'defects_open', 'pass_rate'],
      }),
    ];

    mockFetchSections.mockResolvedValue(sampleSections);
    mockCreateReport.mockResolvedValue({
      filename: 'quality-report.pdf',
      contentType: 'application/pdf',
      content: 'base64-payload',
    });

    const user = userEvent.setup();

    renderWithProviders(<ReportBuilder />);
    await waitFor(() => expect(mockFetchSections).toHaveBeenCalled());

    const availableList = screen.getByRole('list', { name: /available sections/i });
    const layoutRegion = screen.getByRole('region', { name: /report layout/i });

    const dragIntoLayout = async (title: string, id: string) => {
      const item = within(availableList).getByText(title).closest('li');
      if (!item) {
        throw new Error(`List item for ${title} not found`);
      }
      const payload = createDataTransfer(`available:${id}`);
      fireEvent.dragStart(item, { dataTransfer: payload });
      fireEvent.dragOver(layoutRegion, { dataTransfer: payload });
      fireEvent.drop(layoutRegion, { dataTransfer: payload });
    };

    await dragIntoLayout('Analytics Overview', 'analytics-overview');
    await dragIntoLayout('Defect Summary', 'defect-summary');

    const previewRegion = screen.getByRole('region', { name: /report preview/i });
    expect(within(previewRegion).getByRole('heading', { name: /preview/i })).toBeInTheDocument();
    expect(within(previewRegion).getByText(/2 sections selected/i)).toBeInTheDocument();
    const previewList = within(previewRegion).getByRole('list', { name: /selected sections/i });
    const previewItems = within(previewList).getAllByRole('listitem');
    expect(previewItems).toHaveLength(2);
    expect(previewItems[0]).toHaveTextContent('Analytics Overview');
    expect(previewItems[1]).toHaveTextContent('Defect Summary');

    await user.type(screen.getByLabelText(/report title/i), 'Weekly Quality Pulse');
    await user.type(screen.getByLabelText(/description/i), 'Executive summary of quality performance.');
    const startDate = screen.getByLabelText(/start date/i);
    await user.clear(startDate);
    await user.type(startDate, '2024-01-01');
    const endDate = screen.getByLabelText(/end date/i);
    await user.clear(endDate);
    await user.type(endDate, '2024-01-31');

    const formatSelect = screen.getByLabelText(/format/i);
    await user.selectOptions(formatSelect, 'pdf');

    const exportButton = screen.getByRole('button', { name: /export report/i });
    expect(exportButton).toBeEnabled();

    await user.click(exportButton);

    await waitFor(() => expect(mockCreateReport).toHaveBeenCalledTimes(1));

    expect(mockCreateReport).toHaveBeenCalledWith({
      title: 'Weekly Quality Pulse',
      description: 'Executive summary of quality performance.',
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      format: 'pdf',
      metrics: ['pass_rate', 'defect_density', 'defects_resolved', 'defects_open'],
    });

    expect(await screen.findByText(/quality-report\.pdf ready for download/i)).toBeInTheDocument();
  });
});
