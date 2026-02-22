export const checkReachedTarget = (selectors, threshold = 90) => {
  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el) {
      const rect = el.getBoundingClientRect();
      if (rect.top <= threshold) {
        return true;
      }
    }
  }
  return false;
};

export const calculateHeaderState = (params) => {
  const {
    currentY,
    lastY,
    reachedTarget,
    isWindow,
    showThreshold = 60,
    hideThreshold = 100,
    upThreshold = 150,
  } = params;

  const scrollingDown = currentY > lastY;

  if (currentY <= showThreshold) {
    return false;
  }

  if (!scrollingDown && currentY < upThreshold) {
    return false;
  }

  if (scrollingDown) {
    const desktopThreshold = isWindow ? hideThreshold : showThreshold;
    if (reachedTarget || currentY > desktopThreshold) {
      return true;
    }
  }

  return null;
};
