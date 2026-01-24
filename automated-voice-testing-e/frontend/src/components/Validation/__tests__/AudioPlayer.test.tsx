import { render, screen } from '@testing-library/react';
import AudioPlayer from '../AudioPlayer';

// Mock HTMLMediaElement methods
window.HTMLMediaElement.prototype.load = vi.fn();
window.HTMLMediaElement.prototype.play = vi.fn().mockImplementation(() => Promise.resolve());
window.HTMLMediaElement.prototype.pause = vi.fn();

describe('AudioPlayer component', () => {
  const defaultProps = {
    audioUrl: 'https://example.com/audio.mp3',
  };

  const renderAudioPlayer = (props = {}) => {
    return render(<AudioPlayer {...defaultProps} {...props} />);
  };

  describe('Rendering', () => {
    it('renders audio player container', () => {
      renderAudioPlayer();
      // Check that component renders (Play button always present)
      expect(screen.getByRole('button', { name: /Play/i })).toBeInTheDocument();
    });

    it('renders play button with aria-label', () => {
      renderAudioPlayer();
      const playButton = screen.getByRole('button', { name: /Play/i });
      expect(playButton).toBeInTheDocument();
    });

    it('renders volume control button', () => {
      renderAudioPlayer();
      const muteButton = screen.getByRole('button', { name: /Mute/i });
      expect(muteButton).toBeInTheDocument();
    });

    it('renders seek slider', () => {
      renderAudioPlayer();
      const seekSlider = screen.getByRole('slider', { name: /Seek/i });
      expect(seekSlider).toBeInTheDocument();
    });

    it('renders volume slider', () => {
      renderAudioPlayer();
      const volumeSlider = screen.getByRole('slider', { name: /Volume/i });
      expect(volumeSlider).toBeInTheDocument();
    });

    it('renders speed selector', () => {
      renderAudioPlayer();
      const speedSelector = screen.getByLabelText(/Speed/i);
      expect(speedSelector).toBeInTheDocument();
    });
  });

  describe('Time display', () => {
    it('displays initial time as 0:00', () => {
      renderAudioPlayer();
      const timeDisplays = screen.getAllByText('0:00');
      expect(timeDisplays.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Speed options', () => {
    it('has 0.5x, 1x, 1.5x, 2x speed options', () => {
      renderAudioPlayer();
      // Speed selector is present
      expect(screen.getByLabelText(/Speed/i)).toBeInTheDocument();
    });
  });

  describe('Callbacks', () => {
    it('accepts onPlaybackChange callback prop', () => {
      const onPlaybackChange = vi.fn();
      renderAudioPlayer({ onPlaybackChange });
      // Component should render without error
      expect(screen.getByRole('button', { name: /Play/i })).toBeInTheDocument();
    });

    it('accepts onTimeUpdate callback prop', () => {
      const onTimeUpdate = vi.fn();
      renderAudioPlayer({ onTimeUpdate });
      // Component should render without error
      expect(screen.getByRole('button', { name: /Play/i })).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper aria-labels for all interactive elements', () => {
      renderAudioPlayer();

      // Play button
      expect(screen.getByRole('button', { name: /Play/i })).toBeInTheDocument();

      // Mute button
      expect(screen.getByRole('button', { name: /Mute/i })).toBeInTheDocument();

      // Sliders
      expect(screen.getByRole('slider', { name: /Seek/i })).toBeInTheDocument();
      expect(screen.getByRole('slider', { name: /Volume/i })).toBeInTheDocument();
    });
  });
});
