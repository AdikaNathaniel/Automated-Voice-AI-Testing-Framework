/**
 * Tests for StepManager component
 *
 * Covers:
 * - AudioUploadZone: drag & drop, file selection, progress, errors
 * - AudioPlayerCard: playback, transcription display, remove functionality
 * - Step management: add, remove, reorder, expand/collapse
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StepManager, type ScenarioStepData } from '../StepManager';

// Mock the API client
vi.mock('../../../services/api', () => ({
  default: {
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

import apiClient from '../../../services/api';

// Mock HTMLMediaElement methods
window.HTMLMediaElement.prototype.load = vi.fn();
window.HTMLMediaElement.prototype.play = vi.fn().mockImplementation(() => Promise.resolve());
window.HTMLMediaElement.prototype.pause = vi.fn();

// Mock requestAnimationFrame
global.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 0) as unknown as number);
global.cancelAnimationFrame = vi.fn();

describe('StepManager component', () => {
  const mockOnChange = vi.fn();
  const mockOnStepSelect = vi.fn();

  const defaultProps = {
    steps: [] as ScenarioStepData[],
    onChange: mockOnChange,
    onStepSelect: mockOnStepSelect,
    selectedStepIndex: undefined,
    scenarioId: undefined,
  };

  const sampleStep: ScenarioStepData = {
    id: 'step-123',
    step_order: 1,
    user_utterance: 'Hello, how are you?',
    step_metadata: {
      primary_language: 'en-US',
      language_variants: [{ language_code: 'en-US', user_utterance: 'Hello, how are you?' }],
    },
  };

  const stepWithAudio: ScenarioStepData = {
    id: 'step-456',
    step_order: 1,
    user_utterance: 'Play some music',
    step_metadata: {
      primary_language: 'en-US',
      language_variants: [{ language_code: 'en-US', user_utterance: 'Play some music' }],
      audio_source: 'uploaded',
      uploaded_audio: {
        'en-US': {
          s3_key: 'scenarios/test/steps/step-456/audio-en-US.mp3',
          transcription: 'Play some music',
          duration_ms: 2500,
          original_format: 'mp3',
          stt_confidence: 0.95,
          language_code: 'en-US',
        },
      },
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderStepManager = (props = {}) => {
    return render(<StepManager {...defaultProps} {...props} />);
  };

  // ===========================================================================
  // Empty State Tests
  // ===========================================================================
  describe('Empty State', () => {
    it('renders empty state when no steps exist', () => {
      renderStepManager();
      expect(screen.getByText('No steps added yet')).toBeInTheDocument();
    });

    it('renders "Add First Step" button in empty state', () => {
      renderStepManager();
      expect(screen.getByRole('button', { name: /Add First Step/i })).toBeInTheDocument();
    });

    it('shows step count as "0 steps"', () => {
      renderStepManager();
      expect(screen.getByText('0 steps')).toBeInTheDocument();
    });
  });

  // ===========================================================================
  // Step Management Tests
  // ===========================================================================
  describe('Step Management', () => {
    it('renders steps when provided', () => {
      renderStepManager({ steps: [sampleStep] });
      expect(screen.getByText('Step 1')).toBeInTheDocument();
    });

    it('displays step utterance in collapsed view', () => {
      renderStepManager({ steps: [sampleStep] });
      expect(screen.getByText('"Hello, how are you?"')).toBeInTheDocument();
    });

    it('shows correct step count', () => {
      renderStepManager({ steps: [sampleStep, { ...sampleStep, id: 'step-2', step_order: 2 }] });
      expect(screen.getByText('2 steps')).toBeInTheDocument();
    });

    it('calls onChange when adding a step', async () => {
      renderStepManager();
      const addButton = screen.getByRole('button', { name: /Add First Step/i });
      await userEvent.click(addButton);
      expect(mockOnChange).toHaveBeenCalled();
    });

    it('calls onChange when removing a step', async () => {
      renderStepManager({ steps: [sampleStep] });
      const removeButton = screen.getByTitle('Remove step');
      await userEvent.click(removeButton);
      expect(mockOnChange).toHaveBeenCalled();
    });

    it('expands step when clicking on header', async () => {
      renderStepManager({ steps: [sampleStep] });
      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }
      // After click, should show Audio Source section
      expect(screen.getByText('Audio Source')).toBeInTheDocument();
    });

    it('shows language badge for primary language', () => {
      renderStepManager({ steps: [sampleStep] });
      expect(screen.getByText('en-US')).toBeInTheDocument();
    });
  });

  // ===========================================================================
  // AudioUploadZone Tests
  // ===========================================================================
  describe('AudioUploadZone', () => {
    it('renders upload zone when no audio uploaded', async () => {
      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });
      // Expand the step first
      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }
      expect(screen.getByText(/Click to upload/i)).toBeInTheDocument();
    });

    it('shows supported formats hint', async () => {
      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });
      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }
      expect(screen.getByText(/WAV, MP3, OGG, or FLAC/i)).toBeInTheDocument();
    });

    it('shows disabled message when scenario not saved', async () => {
      renderStepManager({ steps: [sampleStep], scenarioId: undefined });
      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }
      expect(screen.getByText(/Save scenario first/i)).toBeInTheDocument();
    });

    it('accepts valid audio file on drop', async () => {
      (apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            s3_key: 'test/audio.mp3',
            transcription: 'Test transcription',
            duration_ms: 2000,
            original_format: 'mp3',
            stt_confidence: 0.9,
            language_code: 'en-US',
          },
        },
      });

      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });

      // Expand the step
      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      const dropZone = screen.getByText(/Click to upload/i).closest('div[class*="border-dashed"]');

      if (dropZone) {
        const file = new File(['audio content'], 'test.mp3', { type: 'audio/mpeg' });
        const dataTransfer = {
          files: [file],
          items: [{ kind: 'file', type: 'audio/mpeg', getAsFile: () => file }],
          types: ['Files'],
        };

        fireEvent.dragOver(dropZone, { dataTransfer });
        fireEvent.drop(dropZone, { dataTransfer });

        await waitFor(() => {
          expect(apiClient.post).toHaveBeenCalled();
        });
      }
    });

    it('shows progress during upload', async () => {
      // Mock a slow upload
      (apiClient.post as ReturnType<typeof vi.fn>).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({
          data: {
            success: true,
            data: {
              s3_key: 'test/audio.mp3',
              transcription: 'Test',
              duration_ms: 1000,
              original_format: 'mp3',
              stt_confidence: 0.9,
              language_code: 'en-US',
            },
          },
        }), 1000))
      );

      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      const dropZone = screen.getByText(/Click to upload/i).closest('div[class*="border-dashed"]');

      if (dropZone) {
        const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
        fireEvent.drop(dropZone, {
          dataTransfer: { files: [file] },
        });

        await waitFor(() => {
          expect(screen.getByText(/Uploading & Transcribing/i)).toBeInTheDocument();
        });
      }
    });

    it('displays error on upload failure', async () => {
      (apiClient.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce({
        response: { data: { detail: 'Invalid audio format' } },
      });

      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      const dropZone = screen.getByText(/Click to upload/i).closest('div[class*="border-dashed"]');

      if (dropZone) {
        const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
        fireEvent.drop(dropZone, {
          dataTransfer: { files: [file] },
        });

        await waitFor(() => {
          expect(screen.getByText(/Invalid audio format/i)).toBeInTheDocument();
        });
      }
    });

    it('rejects invalid file type', async () => {
      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      const dropZone = screen.getByText(/Click to upload/i).closest('div[class*="border-dashed"]');

      if (dropZone) {
        // Drop a PDF file (invalid)
        const file = new File(['pdf content'], 'document.pdf', { type: 'application/pdf' });
        fireEvent.drop(dropZone, {
          dataTransfer: { files: [file] },
        });

        // API should not be called for invalid file type
        await waitFor(() => {
          expect(apiClient.post).not.toHaveBeenCalled();
        });
      }
    });

    it('calls API with correct multipart data', async () => {
      (apiClient.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            s3_key: 'test/audio.mp3',
            transcription: 'Test transcription',
            duration_ms: 2000,
            original_format: 'mp3',
            stt_confidence: 0.9,
            language_code: 'en-US',
          },
        },
      });

      renderStepManager({ steps: [sampleStep], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      const dropZone = screen.getByText(/Click to upload/i).closest('div[class*="border-dashed"]');

      if (dropZone) {
        const file = new File(['audio content'], 'test.mp3', { type: 'audio/mpeg' });
        fireEvent.drop(dropZone, {
          dataTransfer: { files: [file] },
        });

        await waitFor(() => {
          expect(apiClient.post).toHaveBeenCalledWith(
            expect.stringContaining('/scenarios/scenario-123/steps/step-123/audio'),
            expect.any(FormData),
            expect.objectContaining({
              headers: { 'Content-Type': 'multipart/form-data' },
            })
          );
        });
      }
    });
  });

  // ===========================================================================
  // AudioPlayerCard Tests
  // ===========================================================================
  describe('AudioPlayerCard', () => {
    it('renders player when audio is uploaded', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // Should show Uploaded badge
      expect(screen.getAllByText('Uploaded').length).toBeGreaterThan(0);
    });

    it('displays transcription text', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      expect(screen.getByText('"Play some music"')).toBeInTheDocument();
    });

    it('shows confidence score', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // Confidence is 0.95 = 95%
      expect(screen.getByText('95%')).toBeInTheDocument();
    });

    it('shows audio format badge', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      expect(screen.getByText('MP3')).toBeInTheDocument();
    });

    it('shows duration', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // 2500ms = 0:02
      expect(screen.getByText('0:02')).toBeInTheDocument();
    });

    it('calls delete API on remove click', async () => {
      (apiClient.delete as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});

      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // Find the X button in the audio player (not the step remove button)
      const audioSection = screen.getByText('Audio Source').closest('div[class*="border"]');
      const removeButtons = audioSection?.querySelectorAll('button');

      // The last button in the audio player section should be the remove button
      const removeAudioButton = Array.from(removeButtons || []).find(
        btn => btn.querySelector('svg')
      );

      if (removeAudioButton) {
        await userEvent.click(removeAudioButton);
        await waitFor(() => {
          expect(apiClient.delete).toHaveBeenCalledWith(
            expect.stringContaining('/audio/en-US')
          );
        });
      }
    });

    it('plays audio from S3 URL', async () => {
      renderStepManager({ steps: [stepWithAudio], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // Find the play button in the audio player
      const playButton = screen.getByRole('button', { name: '' });
      // The audio element should have the S3 key as source
      const audioElement = document.querySelector('audio');

      expect(audioElement).toBeInTheDocument();
      expect(audioElement?.src).toContain(stepWithAudio.step_metadata?.uploaded_audio?.['en-US']?.s3_key);

      // Click play button
      if (playButton) {
        await userEvent.click(playButton);
        expect(window.HTMLMediaElement.prototype.play).toHaveBeenCalled();
      }
    });
  });

  // ===========================================================================
  // Drag and Drop Reorder Tests
  // ===========================================================================
  describe('Drag and Drop', () => {
    it('has draggable steps', () => {
      renderStepManager({ steps: [sampleStep] });
      const stepContainer = screen.getByText('Step 1').closest('div[draggable="true"]');
      expect(stepContainer).toBeInTheDocument();
    });

    it('shows drag handle', () => {
      renderStepManager({ steps: [sampleStep] });
      const dragHandle = screen.getByTitle('Drag to reorder');
      expect(dragHandle).toBeInTheDocument();
    });
  });

  // ===========================================================================
  // Multi-language Tests
  // ===========================================================================
  describe('Multi-language Support', () => {
    const multiLangStep: ScenarioStepData = {
      id: 'step-multi',
      step_order: 1,
      user_utterance: 'Hello',
      step_metadata: {
        primary_language: 'en-US',
        language_variants: [
          { language_code: 'en-US', user_utterance: 'Hello' },
          { language_code: 'es-ES', user_utterance: 'Hola' },
          { language_code: 'fr-FR', user_utterance: 'Bonjour' },
        ],
      },
    };

    it('shows variant count badge', () => {
      renderStepManager({ steps: [multiLangStep] });
      expect(screen.getByText('+2 variants')).toBeInTheDocument();
    });

    it('shows upload zone for each language variant', async () => {
      renderStepManager({ steps: [multiLangStep], scenarioId: 'scenario-123' });

      const stepHeader = screen.getByText('Step 1').closest('div[class*="cursor-pointer"]');
      if (stepHeader) {
        await userEvent.click(stepHeader);
      }

      // Should show language codes for each variant
      expect(screen.getAllByText('en-US').length).toBeGreaterThan(0);
      expect(screen.getAllByText('es-ES').length).toBeGreaterThan(0);
      expect(screen.getAllByText('fr-FR').length).toBeGreaterThan(0);
    });
  });

  // ===========================================================================
  // Selection Tests
  // ===========================================================================
  describe('Step Selection', () => {
    it('highlights selected step', () => {
      renderStepManager({ steps: [sampleStep], selectedStepIndex: 0 });
      const stepContainer = screen.getByText('Step 1').closest('div[draggable="true"]');
      expect(stepContainer?.className).toContain('ring-2');
    });
  });

  // ===========================================================================
  // Accessibility Tests
  // ===========================================================================
  describe('Accessibility', () => {
    it('has accessible Add Step button', () => {
      renderStepManager();
      const addButton = screen.getByRole('button', { name: /Add First Step/i });
      expect(addButton).toBeInTheDocument();
    });

    it('has title on remove button', () => {
      renderStepManager({ steps: [sampleStep] });
      const removeButton = screen.getByTitle('Remove step');
      expect(removeButton).toBeInTheDocument();
    });

    it('has title on drag handle', () => {
      renderStepManager({ steps: [sampleStep] });
      const dragHandle = screen.getByTitle('Drag to reorder');
      expect(dragHandle).toBeInTheDocument();
    });
  });
});
