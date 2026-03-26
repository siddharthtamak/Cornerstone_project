import MarketingNavbar from "../components/layout/MarketingNavbar";
import Footer from "../components/layout/Footer";

function Section({ id, title, children }) {
  return (
    <section id={id} className="scroll-mt-28 space-y-4">
      <h2 className="text-2xl font-semibold text-black">{title}</h2>
      <div className="prose prose-slate max-w-none">
        {children}
      </div>
    </section>
  );
}

export default function HowItWorks() {
  return (
    <>
      <MarketingNavbar />

      <main className="pt-24 pb-32 bg-slate-50">
        <div className="mx-auto max-w-4xl px-6">
          <div className="rounded-xl bg-white shadow-sm p-10 space-y-16">

            {/* Page Header */}
            <header className="space-y-4">
              <h1 className="text-3xl font-semibold text-black">
                How Aegis AI Works
              </h1>
              <p className="text-gray-600 max-w-2xl">
                Aegis AI uses a multimodal pipeline to analyze video content,
                combining visual, textual, and audio-based signals to detect
                potentially harmful content with temporal precision.
              </p>
            </header>

            <Section id="overview" title="Overview">
              <p>
                Aegis AI analyzes video content using a <strong>multimodal
                approach</strong>, combining signals from visual frames, spoken
                language, and audio characteristics. Each modality is processed
                independently using specialized models, and their outputs are
                later combined to produce a final moderation verdict.
              </p>
              <p>
                This design allows the system to identify not only whether
                harmful content exists, but also <em>when</em> it occurs within
                a video.
              </p>
            </Section>

            <Section
              id="preprocessing"
              title="Video Ingestion & Preprocessing"
            >
              <p>
                When a video is uploaded, it is decomposed into its core
                components:
              </p>
              <ul>
                <li>Video frames, each associated with a precise timestamp</li>
                <li>The audio track extracted from the video</li>
                <li>A transcript generated from the audio</li>
              </ul>
              <p>
                This preprocessing step ensures that all downstream models
                operate on timestamp-aligned data, enabling accurate temporal
                flagging of detected content.
              </p>
            </Section>

            <Section id="vision" title="Vision Modality">
              <p>
                The vision modality performs <strong>frame-level analysis</strong>
                on extracted video frames.
              </p>

              <h3>Optical Character Recognition (OCR)</h3>
              <p>
                Text appearing within video frames is detected using OCR. The
                extracted text is passed through the same text classification
                model used in the text modality. However, because the source is
                visual, these predictions contribute to the <strong>vision
                modality</strong>.
              </p>

              <h3>Visual Classification Models</h3>
              <p>
                In addition to OCR, two dedicated CNN-based models analyze each
                frame:
              </p>
              <ul>
                <li>Sexually explicit content detection</li>
                <li>Violence detection</li>
              </ul>

              <p>
                Frames flagged as potentially harmful are mapped back to their
                original timestamps, allowing precise identification of
                problematic visual segments.
              </p>
            </Section>

            <Section id="text" title="Text Modality">
              <p>
                The text modality focuses on the <strong>spoken content</strong>
                of the video.
              </p>
              <p>
                Audio is first transcribed into text. The transcript is then
                segmented line by line, with each line associated with the time
                at which it was spoken.
              </p>

              <p>
                A fine-tuned <strong>RoBERTa-based multiclass classification
                model</strong> is applied to each text segment to detect:
              </p>

              <ul>
                <li>Sexually explicit content</li>
                <li>Violent content</li>
                <li>Hate speech</li>
                <li>Neutral content</li>
              </ul>

              <p>
                If a segment is classified as harmful, its corresponding
                timestamp is recorded, enabling accurate temporal moderation.
              </p>
            </Section>

            <Section id="audio" title="Audio Modality">
              <p>
                The audio modality analyzes <strong>non-semantic audio
                characteristics</strong>, independent of spoken meaning.
              </p>

              <p>
                This model focuses on features such as pitch, amplitude, and
                other acoustic patterns. The audio stream is divided into
                <strong> fixed 6-second segments</strong>, each analyzed
                independently.
              </p>

              <p>
                The audio modality is designed to capture signals such as
                aggressive tones, heightened intensity, or disturbing
                non-verbal sounds. It does not analyze the semantic content of
                speech.
              </p>
            </Section>

            <Section id="outputs" title="Multiclass Outputs">
              <p>
                Each model across all modalities produces multiclass confidence
                scores for the following categories:
              </p>

              <ul>
                <li>Sexually explicit content</li>
                <li>Violent content</li>
                <li>Hate speech</li>
                <li>Neutral content</li>
              </ul>

              <p>
                These outputs remain modality-specific and preserve timestamp
                information wherever applicable.
              </p>
            </Section>

            <Section id="verdict" title="Final Verdict (High-Level)">
              <p>
                The final moderation verdict is derived by combining the outputs
                of the vision, text, and audio modalities.
              </p>

              <p>
                While the exact aggregation strategy is still under active
                development, the system is designed to ensure that no single
                modality dominates the decision and that confidence scores are
                treated as probabilistic signals rather than absolute truths.
              </p>
            </Section>

            <Section
              id="notes"
              title="Notes on Ongoing Development"
            >
              <p>
                Aegis AI is an evolving system. Some aspects of the pipeline —
                including how timestamp-level predictions are aggregated and how
                modality outputs are combined — are intentionally left flexible
                to allow future refinement and improvement.
              </p>
            </Section>

          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
