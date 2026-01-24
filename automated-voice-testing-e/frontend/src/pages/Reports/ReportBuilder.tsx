import { useEffect, useMemo, useState } from 'react';
import { Trash2, ClipboardList } from 'lucide-react';

import {
  createCustomReport,
  fetchReportSections,
  type ReportSection,
} from '../../services/reportBuilder.service';

type DragSource = 'available' | 'layout';

function ReportBuilder(): JSX.Element {
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [availableSections, setAvailableSections] = useState<ReportSection[]>([]);
  const [layoutSections, setLayoutSections] = useState<ReportSection[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [format, setFormat] = useState<'pdf' | 'json'>('pdf');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const loadSections = async () => {
      try {
        setIsLoading(true);
        const sections = await fetchReportSections();
        if (!active) {
          return;
        }
        setAvailableSections(sections);
        setLoadError(null);
      } catch {
        if (!active) {
          return;
        }
        setLoadError('Failed to load report sections.');
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadSections();

    return () => {
      active = false;
    };
  }, []);

  const availableById = useMemo(
    () => Object.fromEntries(availableSections.map((section) => [section.id, section])),
    [availableSections],
  );

  const selectedMetrics = useMemo(() => {
    const seen = new Set<string>();
    const metrics: string[] = [];

    for (const section of layoutSections) {
      for (const metric of section.metrics) {
        if (!seen.has(metric)) {
          seen.add(metric);
          metrics.push(metric);
        }
      }
    }

    return metrics;
  }, [layoutSections]);

  const canExport =
    layoutSections.length > 0 && Boolean(startDate) && Boolean(endDate) && !isSubmitting;

  const layoutById = useMemo(
    () => Object.fromEntries(layoutSections.map((section) => [section.id, section])),
    [layoutSections],
  );

  const renderLoadingState = () => (
    <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
      <div className="flex flex-col items-center justify-center p-20">
        <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
        <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Report Sections...</div>
      </div>
    </div>
  );

  const insertAt = (items: ReportSection[], index: number, section: ReportSection): ReportSection[] => {
    const safeIndex = Math.max(0, Math.min(index, items.length));
    const next = [...items];
    next.splice(safeIndex, 0, section);
    return next;
  };

  const parseTransfer = (event: React.DragEvent): { source: DragSource; id: string } | null => {
    const payload = event.dataTransfer?.getData('text/plain');
    if (!payload) {
      return null;
    }

    const [rawSource, id] = payload.split(':');
    if (id && (rawSource === 'available' || rawSource === 'layout')) {
      return { source: rawSource, id };
    }

    return null;
  };

  const handleLayoutDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const handleLayoutDrop = (event: React.DragEvent<HTMLDivElement | HTMLLIElement>, targetIndex?: number) => {
    event.preventDefault();
    event.stopPropagation();

    const transfer = parseTransfer(event);
    if (!transfer) {
      return;
    }

    if (transfer.source === 'available') {
      const section = availableById[transfer.id];
      if (!section) {
        return;
      }

      if (layoutById[section.id]) {
        return;
      }

      setAvailableSections((prev) => prev.filter((item) => item.id !== section.id));
      setLayoutSections((prev) => {
        if (targetIndex == null) {
          return [...prev, section];
        }
        return insertAt(prev, targetIndex, section);
      });
    } else {
      setLayoutSections((prev) => {
        const currentIndex = prev.findIndex((item) => item.id === transfer.id);
        if (currentIndex === -1) {
          return prev;
        }

        const reordered = prev.filter((item) => item.id !== transfer.id);
        const destinationIndex =
          targetIndex == null
            ? reordered.length
            : Math.max(0, Math.min(targetIndex, reordered.length));

        const section = prev[currentIndex];
        if (destinationIndex === currentIndex || destinationIndex === currentIndex + 1) {
          return prev;
        }

        return insertAt(reordered, destinationIndex, section);
      });
    }

    event.dataTransfer?.clearData();
  };

  const handleAvailableDragStart = (event: React.DragEvent<HTMLLIElement>, sectionId: string) => {
    event.dataTransfer.setData('text/plain', `available:${sectionId}`);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleLayoutDragStart = (event: React.DragEvent<HTMLLIElement>, sectionId: string) => {
    event.dataTransfer.setData('text/plain', `layout:${sectionId}`);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleRemoveFromLayout = (sectionId: string) => {
    setLayoutSections((prev) => {
      const toRemove = prev.find((item) => item.id === sectionId);
      if (!toRemove) {
        return prev;
      }
      setAvailableSections((available) => insertAt(available, available.length, toRemove));
      return prev.filter((item) => item.id !== sectionId);
    });
  };

  const handleExport = async () => {
    if (!canExport) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);
    setSuccessMessage(null);

    try {
      const response = await createCustomReport({
        title: title.trim() || undefined,
        description: description.trim() || undefined,
        startDate,
        endDate,
        format,
        metrics: selectedMetrics,
      });

      setSuccessMessage(`${response.filename} ready for download (${response.contentType}).`);
    } catch {
      setSubmitError('Failed to export report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await handleExport();
  };

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <ClipboardList className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Report Builder
          </h1>
          <div className="text-sm text-[var(--color-content-muted)] mt-1">
            Assemble bespoke quality reports by dragging analytics sections into your layout, then preview and export the
            result.
          </div>
        </div>
      </div>

      {/* Error */}
      {loadError && (
        <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger ">
          <div className="text-xl">⚠️</div>
          <div className="flex-1">
            <div className="font-semibold">{loadError}</div>
          </div>
        </div>
      )}

      {/* Loading */}
      {isLoading && renderLoadingState()}

      {!isLoading && !loadError && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[var(--color-surface-raised)] rounded-lg shadow-sm border border-[var(--color-border-default)] p-6 min-h-[240px]">
            <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-2">Available Sections</h2>
            <p className="text-sm text-[var(--color-content-secondary)] mb-4">Drag a section to add it to your report layout.</p>
            <ul aria-label="Available sections" className="space-y-2">
              {availableSections.map((section) => (
                <li
                  key={section.id}
                  draggable
                  onDragStart={(event) => handleAvailableDragStart(event, section.id)}
                  data-testid={`available-${section.id}`}
                  className="p-3 border-b border-[var(--color-border-default)] cursor-move hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  <p className="font-medium text-[var(--color-content-primary)]">{section.title}</p>
                  <p className="text-sm text-[var(--color-content-secondary)]">{section.description}</p>
                </li>
              ))}
            </ul>
          </div>

          <div
            className="bg-[var(--color-surface-inset)] rounded-lg shadow-sm border-2 border-dashed border-[var(--color-border-strong)] p-6 min-h-[240px]"
            role="region"
            aria-label="Report layout"
            onDragOver={handleLayoutDragOver}
            onDrop={(event) => handleLayoutDrop(event)}
          >
            <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Report Layout</h2>
            {layoutSections.length === 0 ? (
              <p className="text-[var(--color-content-secondary)]">Drag sections here to build your report.</p>
            ) : (
              <ul aria-label="Report layout sections" className="space-y-2">
                {layoutSections.map((section, index) => (
                  <li
                    key={section.id}
                    draggable
                    onDragStart={(event) => handleLayoutDragStart(event, section.id)}
                    onDragOver={handleLayoutDragOver}
                    onDrop={(event) => handleLayoutDrop(event, index)}
                    data-testid={`layout-${section.id}`}
                    className="p-3 bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-lg cursor-move hover:border-[var(--color-border-strong)] transition-colors flex items-start gap-3"
                  >
                    <div className="flex-grow">
                      <h3 className="font-medium text-[var(--color-content-primary)]">{section.title}</h3>
                      <p className="text-sm text-[var(--color-content-secondary)]">{section.description}</p>
                    </div>
                    <button
                      aria-label={`Remove ${section.title} from layout`}
                      onClick={() => handleRemoveFromLayout(section.id)}
                      className="flex-shrink-0 p-1 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="bg-[var(--color-surface-raised)] rounded-lg shadow-sm border border-[var(--color-border-default)] p-6 min-h-[240px]" role="region" aria-label="Report preview">
            <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Preview</h2>
            {layoutSections.length === 0 ? (
              <p className="text-[var(--color-content-secondary)] mt-4">Add sections to see a preview of your report contents.</p>
            ) : (
              <div className="space-y-4">
                <p className="text-[var(--color-content-secondary)]">
                  {layoutSections.length} {layoutSections.length === 1 ? 'section' : 'sections'} selected
                </p>
                <ul aria-label="Selected sections" className="space-y-2">
                  {layoutSections.map((section) => (
                    <li key={section.id} className="border-b border-[var(--color-border-default)] pb-2">
                      <p className="text-sm font-medium text-[var(--color-content-primary)]">{section.title}</p>
                      <p className="text-xs text-[var(--color-content-secondary)]">{section.description}</p>
                    </li>
                  ))}
                </ul>
                <p className="text-sm text-[var(--color-content-secondary)]">
                  Metrics included: {selectedMetrics.join(', ') || 'None'}
                </p>
              </div>
            )}

            <div className="border-t border-[var(--color-border-default)] my-6" />

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="report-title" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                  Report title
                </label>
                <input
                  id="report-title"
                  type="text"
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="Executive QA Summary"
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)]"
                />
              </div>
              <div>
                <label htmlFor="report-description" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                  Description
                </label>
                <textarea
                  id="report-description"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Outline the focus of this report"
                  rows={2}
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)]"
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="start-date" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                    Start date
                  </label>
                  <input
                    id="start-date"
                    type="date"
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                    className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                  />
                </div>
                <div>
                  <label htmlFor="end-date" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                    End date
                  </label>
                  <input
                    id="end-date"
                    type="date"
                    value={endDate}
                    onChange={(event) => setEndDate(event.target.value)}
                    className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="format" className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                  Format
                </label>
                <select
                  id="format"
                  value={format}
                  onChange={(event) => setFormat(event.target.value as 'pdf' | 'json')}
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
                >
                  <option value="pdf">PDF</option>
                  <option value="json">JSON</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={!canExport}
                aria-busy={isSubmitting}
                className={`w-full py-2.5 rounded-lg font-semibold transition-all ${
                  canExport
                    ? 'text-white hover:shadow-lg hover:-translate-y-0.5'
                    : 'bg-[var(--color-interactive-active)] text-[var(--color-content-muted)] cursor-not-allowed'
                }`}
                style={canExport ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : undefined}
              >
                {isSubmitting ? 'Exporting…' : 'Export report'}
              </button>
              {submitError && (
                <div className="p-4 rounded-lg flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger ">
                  <div className="text-xl">⚠️</div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{submitError}</div>
                  </div>
                </div>
              )}
              {successMessage && (
                <div className="p-4 rounded-lg flex items-center gap-3 bg-success-light  text-[var(--color-status-success)] border-l-4 border-success ">
                  <div className="text-xl">✅</div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{successMessage}</div>
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default ReportBuilder;
