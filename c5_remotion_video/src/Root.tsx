import { Composition } from 'remotion';
import { EpistemicLimits } from './EpistemicLimits';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="EpistemicLimits"
        component={EpistemicLimits}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
