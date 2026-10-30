import { PUBLIC_SKELETON_DEBUG_DELAY } from '$env/static/public';

export const skeletonDebugDelay = async () => {
  if (PUBLIC_SKELETON_DEBUG_DELAY) {
    await new Promise((resolve) => {
      setTimeout(() => resolve(0), parseFloat(PUBLIC_SKELETON_DEBUG_DELAY));
    });
  }
};
