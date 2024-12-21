import Glide from '@glidejs/glide';

export function launch() {
  const slider = new Glide('.glide', {
    type: 'carousel',
    perView: 3,
    breakpoints: {
      800: {
        perView: 2
      },
      500: {
        perView: 1
      }
    }
  });
  slider.mount();
}
