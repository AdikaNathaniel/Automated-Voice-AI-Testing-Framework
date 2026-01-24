/**
 * HomePage Component
 *
 * Modern landing page with animated waveform hero, feature showcase,
 * and social proof sections. Designed with "Technical Elegance" philosophy.
 */

import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  ArrowRight,
  Play,
  MessageSquare,
  Brain,
  GitBranch,
  Globe,
  BarChart3,
  FileText,
  Users,
  CheckCircle,
  Shield,
} from 'lucide-react';
import type { RootState } from '../store';
import { OuterNav, Footer, WaveformVisualization, FeatureCard } from '../components/outer';

// Feature data for bento grid
const features = [
  {
    icon: MessageSquare,
    title: 'Multi-Turn Conversation Testing',
    description:
      'Create realistic conversation scenarios with multiple steps. Test complete user journeys with context preservation across turns.',
    accent: 'teal' as const,
    size: 'large' as const,
  },
  {
    icon: Brain,
    title: 'AI + Human Validation',
    description:
      'Hybrid validation using LLM ensemble (Gemini, GPT, Claude) with human-in-the-loop review for edge cases.',
    accent: 'amber' as const,
  },
  {
    icon: GitBranch,
    title: 'CI/CD Integration',
    description:
      'Webhook-based automation with GitHub, GitLab, and custom pipeline integration. Trigger tests on every deploy.',
    accent: 'emerald' as const,
  },
  {
    icon: Globe,
    title: '8+ Language Support',
    description:
      'Test scenarios in English, Spanish, French, German, Italian, Portuguese, Japanese, and Chinese.',
    accent: 'purple' as const,
    size: 'large' as const,
  },
  {
    icon: BarChart3,
    title: 'Analytics & Defect Tracking',
    description:
      'Real-time dashboards, regression detection, edge case library, and automated pattern discovery from failed tests.',
    accent: 'rose' as const,
    size: 'large' as const,
  },
  {
    icon: Shield,
    title: 'Edge Case Library',
    description:
      'Capture, categorize, and learn from unexpected scenarios. Build regression coverage automatically over time.',
    accent: 'teal' as const,
  },
];

// Feature highlights for social proof bar
const highlights = [
  { icon: Brain, label: 'AI + Human Validation' },
  { icon: Globe, label: '8+ Languages' },
  { icon: GitBranch, label: 'CI/CD Ready' },
  { icon: BarChart3, label: 'Real-Time Analytics' },
];

// How it works steps
const steps = [
  {
    number: 1,
    title: 'Create Scenarios',
    description: 'Define multi-turn conversation scripts with expected outcomes for each step.',
    icon: FileText,
  },
  {
    number: 2,
    title: 'Execute Tests',
    description: 'Run scenarios through voice AI integration. Tests execute via TTS and capture responses.',
    icon: Play,
  },
  {
    number: 3,
    title: 'Validate & Review',
    description: 'AI validates results automatically. Edge cases route to human reviewers for final decisions.',
    icon: Users,
  },
];

function HomePage() {
  const navigate = useNavigate();
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated || Boolean(state.auth.accessToken)
  );

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen bg-[var(--color-surface-base)] font-display">
      <OuterNav />

      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center overflow-hidden">
        {/* Background Pattern */}
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, var(--color-slate-300) 1px, transparent 0)`,
            backgroundSize: '32px 32px',
          }}
        />

        {/* Teal Accent Glow */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-[#2A6B6E]/10 via-transparent to-transparent pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-gradient-to-tr from-[#2A6B6E]/5 via-transparent to-transparent pointer-events-none" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Content */}
            <div className="text-center lg:text-left">
              {/* Eyebrow */}
              <span className="inline-block animate-fade-up text-sm font-semibold uppercase tracking-widest text-[var(--color-brand-primary)] mb-4">
                Enterprise Voice AI Testing
              </span>

              {/* Headline */}
              <h1 className="hero-headline text-[var(--color-content-primary)] mb-6">
                <span className="block animate-fade-up delay-100">Test Your Voice AI</span>
                <span className="block animate-fade-up delay-200 text-gradient">
                  With Confidence
                </span>
              </h1>

              {/* Subheadline */}
              <p className="hero-subheadline text-[var(--color-content-secondary)] mb-8 animate-fade-up delay-300 max-w-xl mx-auto lg:mx-0">
                Multi-turn conversation testing with AI-powered validation and human-in-the-loop
                review. Ship quality voice experiences faster.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-fade-up delay-400">
                <Link
                  to="/register"
                  className="btn-primary-glow inline-flex items-center justify-center gap-2"
                >
                  Start Free Trial
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <button className="btn-ghost inline-flex items-center justify-center gap-2 border border-[var(--color-border-strong)] rounded-xl">
                  <Play className="w-4 h-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Waveform Visualization */}
            <div className="relative animate-scale-in delay-500">
              <WaveformVisualization className="w-full" />
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights Bar */}
      <section className="py-10 border-y border-[var(--color-border-default)] bg-[var(--color-surface-raised)]/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {highlights.map((item, index) => (
              <div
                key={item.label}
                className="flex items-center justify-center gap-3 animate-fade-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="w-10 h-10 rounded-lg bg-[var(--color-brand-muted)] flex items-center justify-center">
                  <item.icon className="w-5 h-5 text-[var(--color-brand-primary)]" />
                </div>
                <span className="text-sm font-medium text-[var(--color-content-secondary)]">
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 lg:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <span className="inline-block text-sm font-semibold uppercase tracking-widest text-[var(--color-brand-primary)] mb-4 animate-fade-up">
              Features
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-[var(--color-content-primary)] mb-4 animate-fade-up delay-100">
              Everything You Need for Voice QA
            </h2>
            <p className="text-lg text-[var(--color-content-secondary)] max-w-2xl mx-auto animate-fade-up delay-200">
              Comprehensive testing tools built for modern voice AI applications
            </p>
          </div>

          {/* Bento Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 [grid-auto-flow:dense]">
            {features.map((feature, index) => (
              <FeatureCard
                key={feature.title}
                {...feature}
                delay={300 + index * 100}
              />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 lg:py-28 bg-[var(--color-surface-raised)]/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <span className="inline-block text-sm font-semibold uppercase tracking-widest text-[var(--color-brand-primary)] mb-4">
              How It Works
            </span>
            <h2 className="text-3xl lg:text-4xl font-bold text-[var(--color-content-primary)] mb-4">
              Three Steps to Voice AI Quality
            </h2>
            <p className="text-lg text-[var(--color-content-secondary)] max-w-2xl mx-auto">
              Get started in minutes with our streamlined testing workflow
            </p>
          </div>

          {/* Steps */}
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            {steps.map((step, index) => (
              <div
                key={step.number}
                className="relative text-center animate-fade-up"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-12 left-1/2 w-full h-0.5 bg-gradient-to-r from-[#2A6B6E]/30 to-[#2A6B6E]/10" />
                )}

                {/* Step Number */}
                <div className="relative z-10 w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center shadow-lg shadow-[#2A6B6E]/20">
                  <step.icon className="w-10 h-10 text-white" />
                </div>

                <h3 className="text-xl font-semibold text-[var(--color-content-primary)] mb-3">
                  {step.title}
                </h3>
                <p className="text-[var(--color-content-secondary)]">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-28">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-[var(--color-content-primary)] mb-6 animate-fade-up">
            Ready to Ship Quality Voice Experiences?
          </h2>
          <p className="text-lg text-[var(--color-content-secondary)] mb-8 animate-fade-up delay-100">
            Start testing your voice AI with comprehensive scenario coverage and AI-assisted validation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-up delay-200">
            <Link
              to="/register"
              className="btn-primary-glow inline-flex items-center justify-center gap-2"
            >
              Get Started Free
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/login"
              className="btn-ghost inline-flex items-center justify-center gap-2 border border-[var(--color-border-strong)] rounded-xl"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

export default HomePage;
