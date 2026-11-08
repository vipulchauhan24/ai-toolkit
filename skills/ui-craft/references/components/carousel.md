# Carousel

**Try a grid or list first.** Many people scroll past carousels and never see later items. Use one only for a set of equal items, where seeing the first few is enough, such as photos of one product. Anything important also appears elsewhere.

**Build:** CSS scroll snap, with arrows and swipe.

- Five items at most.
- Never autoplay.
- Show the next item partly in view, so people know there's more.
- Arrows are inside the frame, at least `--touch`, and clearly visible over the content.
- Show position in words or numbers: "2 of 5". Dots are easily missed on phones.

**Behaviour:** a labelled region, with each slide labelled. Keyboard users can reach all items and the controls. Pause anything moving under reduced motion.

**Phone:** swipe, with the next item peeking.

**Avoid:** a rotating hero. Tiny dots as the only control. Using a carousel to fit more on a page.
