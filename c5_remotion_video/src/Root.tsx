import { Composition } from 'remotion';
import { JaranaMovie } from './JaranaMovie';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="JaranaMovie"
        component={JaranaMovie}
        durationInFrames={1920}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
