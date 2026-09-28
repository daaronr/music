import { useState } from 'react';
import { LINKS, track } from '../api.ts';

// Where each form starts in the 18-forms video (its YouTube chapters), in seconds.
const FORM_START = [12, 48, 85, 123, 161, 199, 238, 277, 317, 356, 397, 435, 475, 513, 547, 586, 623, 661];

interface Video {
  id: string;
  title: string;
  blurb: string;
  poster: string;
}

const VIDEOS: Record<'tour' | 'forms', Video> = {
  tour: {
    id: LINKS.videoTour,
    title: 'Quick tour of the app',
    blurb: 'What everything on this page does (2 minutes).',
    poster: 'blues-flow-tour.jpg',
  },
  forms: {
    id: LINKS.videoForms,
    title: 'All 18 forms, played and named',
    blurb: 'One chorus of each in F with the chart on screen and the current bar lit (11½ minutes).',
    poster: 'blues-18-forms.jpg',
  },
};

const watchUrl =(id: string, start = 0) => `https://youtu.be/${id}${start ? `?t=${start}` : ''}`;

// Nothing loads from YouTube until someone presses play: the poster is a local image,
// and the player comes from youtube-nocookie.com.
function Embed({ which, start, autoplay = false }: { which: keyof typeof VIDEOS; start: number; autoplay?: boolean }) {
  const v = VIDEOS[which];
  const [on, setOn] = useState(autoplay);
  return (
    <div className="video-frame">
      {on ? (
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${v.id}?autoplay=1&rel=0&start=${start}`}
          title={v.title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
        />
      ) : (
        <button
          className="video-poster"
          onClick={() => {
            setOn(true);
            track('video', which);
          }}
          aria-label={`Play: ${v.title}`}
        >
          <img src={`${import.meta.env.BASE_URL}video/${v.poster}`} alt="" loading="lazy" />
          <span className="video-play" aria-hidden="true" />
        </button>
      )}
    </div>
  );
}

export function Videos({ currentId, onPause }: { currentId: number; onPause: () => void }) {
  const [formsStart, setFormsStart] = useState(0);
  const [formsKey, setFormsKey] = useState(0);
  const start = FORM_START[currentId - 1] ?? 0;
  return (
    <section className="videos" id="videos" aria-labelledby="videos-h">
      <h2 id="videos-h">Videos</h2>
      <div className="video-grid" onClickCapture={onPause}>
        <div className="listen">
          <Embed which="tour" start={0} />
          <h3>{VIDEOS.tour.title}</h3>
          <p>
            {VIDEOS.tour.blurb}{' '}
            <a href={watchUrl(VIDEOS.tour.id)} onClick={() => track('video-link', 'tour')}>
              Watch on YouTube
            </a>
          </p>
        </div>
        <div className="listen">
          <Embed key={formsKey} which="forms" start={formsStart} autoplay={formsKey > 0} />
          <h3>{VIDEOS.forms.title}</h3>
          <p>
            {VIDEOS.forms.blurb}{' '}
            <a href={watchUrl(VIDEOS.forms.id)} onClick={() => track('video-link', 'forms')}>
              Watch on YouTube
            </a>
          </p>
          <p>
            <button
              className="link"
              onClick={() => {
                setFormsStart(start);
                setFormsKey((k) => k + 1);
                track('video-form', String(currentId));
              }}
            >
              Cue it at form {currentId}
            </button>{' '}
            (the one on screen) ·{' '}
            <a href={watchUrl(VIDEOS.forms.id, start)} onClick={() => track('video-link', `form-${currentId}`)}>
              form {currentId} on YouTube
            </a>
          </p>
        </div>
      </div>
      <p className="hint">
        More music on <a href={LINKS.youtube}>my YouTube channel</a>.
      </p>
    </section>
  );
}
